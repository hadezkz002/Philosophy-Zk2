"""Episode audio production pipeline (system python3, stdlib + ffmpeg/ffprobe).

    python3 -m sma.produce plan    episodes/pilot-001 --engine vieneu-turbo-fp32
    python3 -m sma.produce render  episodes/pilot-001 --engine ...
    python3 -m sma.produce validate episodes/pilot-001 --engine ...
    python3 -m sma.produce master  episodes/pilot-001 --engine ... [--out-dir /sdcard/Download/...]
    python3 -m sma.produce all     episodes/pilot-001 --engine ... [--allow-unapproved]

Script -> normalize (pronunciation.json) -> segments -> TTS chunks (checkpointed, content-hashed)
-> chunk validation -> concat with pauses -> loudness normalization -> MP3 + ID3 -> QA + SHA-256.
Build artifacts live in ~/.cache/sma-build/<episode>/<engine>/ (never in git).
"""
import argparse
import glob
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
import wave

from sma import claims as claims_mod
from sma import names as names_mod
from sma.textnorm import load_lexicon, normalize

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUILD = os.path.expanduser("~/.cache/sma-build")
ENGINES = json.load(open(os.path.join(ROOT, "production", "engines.json"), encoding="utf-8"))
PAUSES = {"sentence": 0.30, "paragraph": 0.65, "section": 1.10, "explicit": 1.80, "lead": 0.5, "tail": 1.5}
MAX_CHARS = 220  # sentence groups per TTS call; small chunks = finer checkpoints and validation
MARKUP_LEAK = re.compile(r"<!--|-->|\[|\]|^#|\bPAUSE\b|\bC\d{2,3}\b|[<>]")
log = logging.getLogger("sma.produce")


# ---------- planning ----------

def split_sentences(par):
    parts = re.split(r"(?<=[.!?…])\s+", par.strip())
    groups, cur = [], ""
    for s in parts:
        if cur and len(cur) + 1 + len(s) > MAX_CHARS:
            groups.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        groups.append(cur)
    return groups


def parse_script(text):
    """Yield ('speech', source_text, gap_before) / ('pause', seconds). H1 is spoken as the title."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    events, gap = [], PAUSES["lead"]
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block or block.startswith(">"):
            continue
        if block.startswith("## "):
            if not (events and events[-1][0] == "pause"):  # an explicit [PAUSE] already marks the break
                gap = max(gap, PAUSES["section"])
            continue
        if block.startswith("# "):
            events.append(("speech", block[2:].strip(), gap))
            gap = PAUSES["section"]
            continue
        if block == "[PAUSE]":
            events.append(("pause", PAUSES["explicit"]))
            gap = 0
            continue
        for i, sent in enumerate(split_sentences(block.replace("\n", " "))):
            events.append(("speech", sent, gap if i == 0 else PAUSES["sentence"]))
        gap = PAUSES["paragraph"]
    return events


def count_syllables(text):
    """Vietnamese words are one syllable each; foreign words (Latin names…) count vowel groups."""
    n = 0
    for w in re.findall(r"[\w'-]+", text):
        n += 1 if names_mod.is_vietnamese_word(w) else max(1, len(re.findall(r"[aeiouy]+", w.lower())))
    return n


def engine_family(cfg):
    """Key used in PRONUNCIATION_LEXICON tts{} (e.g. 'vieneu-turbo')."""
    if cfg["runner"].endswith("vieneu_runner"):
        return "vieneu-turbo" if cfg["params"].get("mode") == "v3turbo" else "vieneu-nano"
    return cfg["runner"].rsplit(".", 1)[-1].replace("_runner", "")


def name_plan(script, ep_dir, family, allow_unresolved, proof=False):
    """Resolve proper names against the global lexicon. Returns (respell entries, phoneme overrides, report)."""
    pron = os.path.join(ep_dir, "pronunciation.json")
    episode = json.load(open(pron, encoding="utf-8"))["entries"] if os.path.exists(pron) else []
    entries = names_mod.load_lexicon()
    found = names_mod.candidates(script)
    res = names_mod.resolve(found, entries, episode)
    report = {n: st for n, (st, _) in res.items()}
    ok = names_mod.USABLE if proof else {"LISTENED_OK"}  # candidates are for test renders only
    blocked = [n for n, st in report.items() if st not in ok]
    if blocked and not allow_unresolved:  # fail closed (issue #1): no full synthesis with unreviewed names
        raise SystemExit(f"proper names not cleared for this render {blocked}: production needs LISTENED_OK in "
                         "production/PRONUNCIATION_LEXICON.json; --proof accepts candidates; "
                         "--allow-unresolved-names for a labelled test render")
    overrides, respell, handled = [], [], set()
    for e in entries:
        t = (e.get("tts") or {}).get(family)
        if not t or e["status"] not in names_mod.USABLE:
            continue
        handled.add(e["original"])
        if t["mode"] == "phonemes":
            overrides.append({"text": e["original"], "phonemes": t["value"]})
        elif t["mode"] == "respell":
            respell.append({"pattern": e["original"], "replacement": t["value"]})
    # Global lexicon wins over the episode's legacy respellings for the same name.
    respell += [x for x in episode if x["pattern"] not in handled and (not x.get("engines") or family in x["engines"])]
    return respell, overrides, report


def plan(ep_dir, engine, allow_unresolved=False, proof=False):
    cfg = ENGINES[engine]
    with open(os.path.join(ep_dir, "script.md"), encoding="utf-8") as f:
        script = f.read()
    lex, overrides, name_report = name_plan(script, ep_dir, engine_family(cfg), allow_unresolved, proof)
    version = re.search(r"script_version:\s*([\d.]+)", script)
    segs, n = [], 0
    for ev in parse_script(script):
        if ev[0] == "pause":
            segs.append({"kind": "pause", "seconds": ev[1]})
            continue
        spoken = normalize(ev[1], lex)
        if not re.search(r"\w", spoken):
            continue
        if MARKUP_LEAK.search(spoken):  # fail closed: editorial notes/markup must never be narrated
            raise SystemExit(f"markup leaked into narration: {spoken[:120]!r}")
        n += 1
        # Hash only the overrides this chunk actually uses, so unrelated chunks keep their audio.
        used = [o for o in overrides if re.search(r"(?<!\w)" + re.escape(o["text"]) + r"(?!\w)", spoken)]
        h = hashlib.sha1(json.dumps([spoken, cfg["params"], used] if used else [spoken, cfg["params"]],
                                    ensure_ascii=False).encode()).hexdigest()[:10]
        segs.append({"kind": "speech", "id": f"s{n:03d}_{h}", "gap_before": ev[2], "source_text": ev[1],
                     "spoken_text": spoken, "syllables": count_syllables(spoken), "phoneme_overrides": used})
    out = {"episode": os.path.basename(ep_dir.rstrip("/")), "engine": engine, "engine_cfg": cfg,
           "script_version": version.group(1) if version else None,
           "script_sha256": hashlib.sha256(script.encode()).hexdigest(), "segments": segs,
           "phoneme_overrides": overrides, "names": name_report,
           "unresolved_names_allowed": allow_unresolved}
    d = build_dir(ep_dir, engine)
    write_json(os.path.join(d, "segments.json"), out)
    log.info("planned %d speech chunks (%d syllables); names: %s", n, sum(s.get("syllables", 0) for s in segs),
             json.dumps(name_report, ensure_ascii=False))
    return out


# ---------- render (delegates to the engine's venv runner; resumable) ----------

def render(ep_dir, engine):
    plan_ = load_plan(ep_dir, engine)
    cfg = ENGINES[engine]
    d = build_dir(ep_dir, engine)
    os.makedirs(os.path.join(d, "chunks"), exist_ok=True)
    items = [{"id": s["id"], "text": s["spoken_text"], "out": chunk_path(d, s)} for s in plan_["segments"]
             if s["kind"] == "speech" and not os.path.exists(chunk_path(d, s))]
    if not items:
        log.info("render: all chunks present (resume no-op)")
        return
    job = os.path.join(d, "job.json")
    params = dict(cfg["params"], phoneme_overrides=plan_.get("phoneme_overrides", []))
    write_json(job, {"engine_params": params, "items": items})
    cmd = [os.path.join(ROOT, cfg["python"]), "-m", cfg["runner"], job]
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"), HF_HUB_OFFLINE="1")
    log.info("render: %d chunks missing, running %s", len(items), cfg["runner"])
    expected = {s["id"]: {o["text"] for o in s.get("phoneme_overrides", [])} for s in plan_["segments"]
                if s["kind"] == "speech"}
    bad = []
    t0 = time.monotonic()
    with open(os.path.join(d, "render.log"), "a", encoding="utf-8") as logf:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=logf, text=True, env=env)
        for line in p.stdout:
            logf.write(line)
            ev = json.loads(line)
            if ev["event"] == "error":
                log.error("chunk %s failed: %s", ev["id"], ev["error"])
            elif ev["event"] == "done":
                log.info("chunk %s %.1fs audio in %.1fs", ev["id"], ev["audio_sec"], ev["synth_sec"])
                got = set((ev.get("phoneme_overrides_applied") or {}))
                if expected.get(ev["id"], set()) - got:  # name spoken with the engine default, not the lexicon
                    bad.append(ev["id"])
                    os.remove(chunk_path(d, next(s for s in plan_["segments"] if s.get("id") == ev["id"])))
        p.wait()
    log.info("render finished rc=%s in %.0fs", p.returncode, time.monotonic() - t0)
    if p.returncode:
        raise SystemExit(f"runner exited {p.returncode}; rerun `render` to resume")
    if bad:
        raise SystemExit(f"phoneme overrides not applied in {bad}; chunks removed, fix the runner and rerun")
    missing = [i["id"] for i in items if not os.path.exists(i["out"])]
    if missing:
        raise SystemExit(f"runner produced no audio for {missing}; rerun `render` to resume")


# ---------- validation ----------

def wav_info(path):
    with wave.open(path) as w:
        return {"rate": w.getframerate(), "channels": w.getnchannels(), "width": w.getsampwidth(),
                "seconds": w.getnframes() / w.getframerate()}


def ff_stats(path):
    """Peak/RMS dB and internal silences via ffmpeg astats + silencedetect."""
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", path, "-af",
                        "astats=metadata=0:reset=0,silencedetect=n=-45dB:d=1.2", "-f", "null", "-"],
                       capture_output=True, text=True)
    err = r.stderr

    def grab(key):
        m = re.findall(rf"{key}:\s*(-?[\d.]+|-inf)", err)
        return float(m[-1]) if m and m[-1] != "-inf" else None
    return {"peak_db": grab("Peak level dB"), "rms_db": grab("RMS level dB"),
            "silences": [float(x) for x in re.findall(r"silence_duration:\s*([\d.]+)", err)],
            "decode_ok": r.returncode == 0}


def validate(ep_dir, engine):
    plan_ = load_plan(ep_dir, engine)
    d = build_dir(ep_dir, engine)
    speech = [s for s in plan_["segments"] if s["kind"] == "speech"]
    rows, problems, hashes = [], [], {}
    for s in speech:
        p = chunk_path(d, s)
        if not os.path.exists(p):
            problems.append(f"{s['id']}: MISSING chunk")
            continue
        info, st = wav_info(p), ff_stats(p)
        sha = sha256_file(p)
        rate = s["syllables"] / info["seconds"] if info["seconds"] else 0
        row = {"id": s["id"], **info, **st, "syll_per_sec": round(rate, 2), "sha256": sha}
        if sha in hashes:
            problems.append(f"{s['id']}: DUPLICATE audio of {hashes[sha]}")
        hashes[sha] = s["id"]
        if info["seconds"] < 0.4 or (st["rms_db"] is not None and st["rms_db"] < -50):
            problems.append(f"{s['id']}: near-silent/empty chunk")
        if st["peak_db"] is not None and st["peak_db"] >= -0.1:
            problems.append(f"{s['id']}: clipping (peak {st['peak_db']} dB)")
        if any(x > 1.6 for x in st["silences"]):
            problems.append(f"{s['id']}: internal silence {max(st['silences'])}s")
        if not st["decode_ok"]:
            problems.append(f"{s['id']}: decode error")
        rows.append(row)
    rates = sorted(r["syll_per_sec"] for r in rows)
    med = rates[len(rates) // 2] if rates else 0
    for r in rows:  # truncation / runaway generation shows up as abnormal speaking rate
        if med and not 0.6 * med <= r["syll_per_sec"] <= 1.6 * med:
            problems.append(f"{r['id']}: speaking rate {r['syll_per_sec']} vs median {med}")
    srs = {r["rate"] for r in rows}
    if len(srs) > 1:
        problems.append(f"inconsistent sample rates {srs}")
    report = {"chunks": len(speech), "validated": len(rows), "median_syll_per_sec": med, "problems": problems,
              "rows": rows}
    write_json(os.path.join(d, "chunk_validation.json"), report)
    log.info("validate: %d/%d chunks, median %.2f syll/s, %d problems", len(rows), len(speech), med, len(problems))
    for p_ in problems:
        log.warning("  %s", p_)
    return report


# ---------- mastering ----------

def master(ep_dir, engine, out_dir, title, meta):
    plan_ = load_plan(ep_dir, engine)
    d = build_dir(ep_dir, engine)
    rates = {wav_info(chunk_path(d, s))["rate"] for s in plan_["segments"] if s["kind"] == "speech"}
    sr = rates.pop()
    concat = os.path.join(d, "concat.txt")
    sil_cache = {}

    def silence(sec):
        key = round(sec, 2)
        if key not in sil_cache:
            path = os.path.join(d, f"sil_{key}.wav")
            with wave.open(path, "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes(b"\x00\x00" * int(sr * key))
            sil_cache[key] = path
        return sil_cache[key]

    lines = []
    for s in plan_["segments"]:
        if s["kind"] == "pause":
            lines.append(silence(s["seconds"]))
        else:
            if s["gap_before"]:
                lines.append(silence(s["gap_before"]))
            lines.append(chunk_path(d, s))
    lines.append(silence(PAUSES["tail"]))
    with open(concat, "w", encoding="utf-8") as f:
        f.writelines(f"file '{p}'\n" for p in lines)
    raw = os.path.join(d, "episode_raw.wav")
    run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat, "-c", "copy", raw])
    # Two-pass EBU R128 loudness normalization to -16 LUFS / -1.5 dBTP (spoken-word podcast target).
    first = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", raw, "-af",
                            "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    m = json.loads(first[first.rindex("{"):first.rindex("}") + 1])
    ln = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    os.makedirs(out_dir, exist_ok=True)
    final = os.path.join(out_dir, meta["filename"])
    tmp = final + ".part.mp3"
    tags = ["-metadata", f"title={title}", "-metadata", "artist=Science Media Academy",
            "-metadata", "album=Science Media Academy — Pilot", "-metadata", "genre=Podcast",
            "-metadata", "language=vie", "-metadata", f"comment={meta['comment']}",
            "-metadata", f"date={time.strftime('%Y')}"]
    run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i", raw, "-af", f"highpass=f=60,{ln}", "-ar", "44100",
         "-ac", "1", "-c:a", "libmp3lame", "-b:a", "96k", "-id3v2_version", "3", *tags, tmp])
    os.replace(tmp, final)  # atomic publish into Downloads
    log.info("master: wrote %s", final)
    return final, m


def qa(final, plan_, d, target_s=(480, 720)):
    """Technical QA of the delivered MP3 (format, duration, decode, loudness, peak, silences, checksum)."""
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                    "format=format_name,duration,bit_rate:format_tags:stream=codec_name,sample_rate,channels",
                                    "-of", "json", final], capture_output=True, text=True).stdout)
    dec = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", final, "-f", "null", "-"],
                         capture_output=True, text=True)
    ebu = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", final, "-af", "ebur128=peak=true", "-f", "null",
                          "-"], capture_output=True, text=True).stderr
    summ = ebu[ebu.rfind("Summary:"):]

    def g(k):
        m = re.search(rf"{k}:\s*(-?[\d.]+)", summ)
        return float(m.group(1)) if m else None
    st = ff_stats(final)
    speech = [s for s in plan_["segments"] if s["kind"] == "speech"]
    expected = sum(wav_info(chunk_path(d, s))["seconds"] + s["gap_before"] for s in speech) + sum(
        s["seconds"] for s in plan_["segments"] if s["kind"] == "pause") + PAUSES["tail"]
    dur = float(pr["format"]["duration"])
    res = {"file": final, "size_bytes": os.path.getsize(final), "sha256": sha256_file(final),
           "format": pr["format"]["format_name"], "codec": pr["streams"][0]["codec_name"],
           "sample_rate": int(pr["streams"][0]["sample_rate"]), "channels": pr["streams"][0]["channels"],
           "bit_rate": int(pr["format"].get("bit_rate", 0)), "duration_s": round(dur, 2),
           "expected_duration_s": round(expected, 2), "tags": pr["format"].get("tags", {}),
           "full_decode_ok": dec.returncode == 0 and not dec.stderr.strip(), "decode_stderr": dec.stderr.strip()[:300],
           "integrated_lufs": g("I"), "loudness_range_lu": g("LRA"), "true_peak_dbfs": g("Peak"),
           "sample_peak_db": st["peak_db"], "silences_over_1_2s": st["silences"]}
    checks = {
        "mp3_container": res["format"] == "mp3" and res["codec"] == "mp3",
        f"duration_{target_s[0] // 60}_{target_s[1] // 60}_min": target_s[0] <= dur <= target_s[1],
        "duration_matches_chunks": abs(dur - expected) <= 1.5,
        "full_decode": res["full_decode_ok"],
        "loudness_-16_lufs_±1.5": res["integrated_lufs"] is not None and abs(res["integrated_lufs"] + 16) <= 1.5,
        "true_peak_≤_-1_dbtp": res["true_peak_dbfs"] is not None and res["true_peak_dbfs"] <= -1.0,
        "no_clipping": st["peak_db"] is not None and st["peak_db"] < -0.1,
        # explicit [PAUSE]s are 1.8 s; anything longer than 2.5 s is unexpected
        "no_unexpected_silence": all(x <= 2.5 for x in st["silences"]),
        "id3_title": bool(res["tags"].get("title")),
    }
    res["checks"] = checks
    res["passed"] = all(checks.values())
    return res


# ---------- helpers ----------

def build_dir(ep_dir, engine):
    d = os.path.join(BUILD, os.path.basename(ep_dir.rstrip("/")), engine)
    os.makedirs(d, exist_ok=True)
    return d


def load_plan(ep_dir, engine):
    with open(os.path.join(build_dir(ep_dir, engine), "segments.json"), encoding="utf-8") as f:
        return json.load(f)


def chunk_path(d, s):
    """Audio is keyed by content hash only, so inserting a sentence does not invalidate later chunks."""
    path = os.path.join(d, "chunks", s["id"].split("_", 1)[1] + ".wav")
    if not os.path.exists(path):  # migrate pre-2026-10-15 names (sNNN_<hash>.wav, any NNN)
        legacy = glob.glob(os.path.join(d, "chunks", "s[0-9][0-9][0-9]_" + os.path.basename(path)))
        if legacy:
            os.replace(legacy[0], path)
    return path


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"command failed ({r.returncode}): {' '.join(cmd[:4])}… {r.stderr[-400:]}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "render", "validate", "master", "all"])
    ap.add_argument("episode")
    ap.add_argument("--engine", required=True, choices=sorted(ENGINES))
    ap.add_argument("--out-dir", default="/sdcard/Download/Science_Audio_VN/00_Science_Media_Academy")
    ap.add_argument("--allow-unresolved-names", action="store_true",
                    help="plan even if proper names lack a verified lexicon entry (proof renders only)")
    ap.add_argument("--allow-unapproved", action="store_true",
                    help="render even if claims are not all APPROVED/REVISED (samples only, never release)")
    ap.add_argument("--proof", action="store_true",
                    help="proof/test render: claims gate checks only narrated claims; names may be unlistened candidates")
    a = ap.parse_args(argv)
    d = build_dir(a.episode, a.engine)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.StreamHandler(), logging.FileHandler(os.path.join(d, "produce.log"))])
    if a.cmd in ("render", "all") and not a.allow_unapproved:
        errors, stats = claims_mod.validate(a.episode, release=True, partial=a.proof)
        if errors:  # fail closed: FACT_CHECK_POLICY §6
            for e in errors[:10]:
                log.error("claims gate: %s", e)
            raise SystemExit("claims gate FAILED: script not approved for audio production")
    if a.cmd in ("plan", "all"):
        plan(a.episode, a.engine, a.allow_unresolved_names, a.proof)
    if a.cmd in ("render", "all"):
        render(a.episode, a.engine)
    if a.cmd in ("validate", "all"):
        rep = validate(a.episode, a.engine)
        if rep["problems"] and a.cmd == "all":
            raise SystemExit("chunk validation found problems; inspect chunk_validation.json, delete bad chunks, rerun")
    if a.cmd in ("master", "all"):
        meta = json.load(open(os.path.join(a.episode, "metadata.json"), encoding="utf-8"))
        final, _ = master(a.episode, a.engine, a.out_dir, meta["title"], meta["audio"])
        res = qa(final, load_plan(a.episode, a.engine), d, tuple(meta["audio"].get("target_duration_s", (480, 720))))
        res["engine"] = a.engine
        write_json(os.path.join(d, "audio_qa.json"), res)
        with open(final + ".sha256", "w") as f:
            f.write(f"{res['sha256']}  {os.path.basename(final)}\n")
        log.info("QA %s: %s", "PASS" if res["passed"] else "FAIL", json.dumps(res["checks"], ensure_ascii=False))


if __name__ == "__main__":
    main()
