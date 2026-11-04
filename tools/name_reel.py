#!/usr/bin/env python3
"""Render a proper-name A/B listening reel with the production TTS engine (issue #1).

    python3 tools/name_reel.py <reel.json> <out_dir> [--engine vieneu-turbo-fp32]

reel.json = [{"name": "Einstein", "ref_audio": "optional reference clip played after the intro",
              "variants": {"A_original": {"text": "Einstein"},
                                                "B_pilot": {"text": "Anh-xtanh"},
                                                "C_phonemes": {"text": "Einstein", "phonemes": "…"}}}]
Each variant is spoken inside the same carrier sentence. Phoneme variants run in one runner job per variant
key (overrides are per job, so a key must not hold two phoneme sets for the same text). Output: one WAV per item, reel MP3 with spoken index, and reel_index.csv with timestamps.
"""
import csv
import json
import os
import subprocess
import sys
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from sma.produce import ENGINES  # noqa: E402

CARRIER = "Cách {label}: {text}. Một lần nữa, {text}."
LABELS = {"A": "thứ nhất", "B": "thứ hai", "C": "thứ ba", "D": "thứ tư"}


def run_job(engine, items, overrides, job_path):
    cfg = ENGINES[engine]
    params = dict(cfg["params"], phoneme_overrides=overrides)
    with open(job_path, "w", encoding="utf-8") as f:
        json.dump({"engine_params": params, "items": items}, f, ensure_ascii=False)
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"), HF_HUB_OFFLINE="1")
    r = subprocess.run([os.path.join(ROOT, cfg["python"]), "-m", cfg["runner"], job_path],
                       capture_output=True, text=True, env=env)
    events = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    errors = [e for e in events if e["event"] == "error"]
    if r.returncode or errors:
        raise SystemExit(f"runner failed: {errors or r.stderr[-400:]}")
    done = {e["id"]: e for e in events if e["event"] == "done"}
    missing = [i["id"] for i in items if i["id"] not in done and not os.path.exists(i["out"])]
    if missing:  # fail closed: a silent runner must not yield a reel with holes
        raise SystemExit(f"runner produced no audio for {missing[:5]} (+{max(0, len(missing) - 5)})")
    return done


def main():
    reel_path, out = sys.argv[1], sys.argv[2]
    engine = sys.argv[sys.argv.index("--engine") + 1] if "--engine" in sys.argv else "vieneu-turbo-fp32"
    os.makedirs(out, exist_ok=True)
    reel = json.load(open(reel_path, encoding="utf-8"))
    reel = reel["items"] if isinstance(reel, dict) else reel
    plain, phon, refs = [], {}, {}  # phoneme variants grouped by variant key
    order = []
    for i, entry in enumerate(reel, 1):
        intro_id = f"n{i:02d}_intro"
        plain.append({"id": intro_id, "text": f"Tên số {i}.", "out": os.path.join(out, intro_id + ".wav")})
        order.append((intro_id, entry["name"], "intro", ""))
        if entry.get("ref_audio"):
            refs[f"n{i:02d}_R_reference"] = os.path.expanduser(entry["ref_audio"])
            order.append((f"n{i:02d}_R_reference", entry["name"], "R_reference", ""))
        for key, v in entry["variants"].items():
            vid = f"n{i:02d}_{key}"
            item = {"id": vid, "text": CARRIER.format(label=LABELS[key[0]], text=v["text"]),
                    "out": os.path.join(out, vid + ".wav")}
            order.append((vid, entry["name"], key, v.get("phonemes", "")))
            if v.get("phonemes"):
                items, ov = phon.setdefault(key, ([], {}))
                if ov.setdefault(v["text"], v["phonemes"]) != v["phonemes"]:
                    raise SystemExit(f"{key}: two phoneme sets for {v['text']!r}")
                items.append(item)
            else:
                plain.append(item)
    meta = run_job(engine, plain, [], os.path.join(out, "job_plain.json"))
    for key, (items, ov) in phon.items():
        overrides = [{"text": t, "phonemes": ph} for t, ph in ov.items()]
        meta.update(run_job(engine, items, overrides, os.path.join(out, f"job_{key}.json")))
    # concatenate with short gaps and an index of start times
    sr = wave.open(os.path.join(out, order[0][0] + ".wav")).getframerate()
    for rid, src in refs.items():  # reference clips: same format as the TTS chunks for the concat demuxer
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i", src, "-ac", "1", "-ar", str(sr),
                        "-c:a", "pcm_s16le", os.path.join(out, rid + ".wav")], check=True)
    gap = os.path.join(out, "gap.wav")
    with wave.open(gap, "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(sr), w.writeframes(b"\x00\x00" * int(sr * 0.7))
    t, rows, lines = 0.0, [], []
    for vid, name, key, ph in order:
        p = os.path.join(out, vid + ".wav")
        d = wave.open(p).getnframes() / sr
        rows.append({"start": f"{int(t // 60)}:{t % 60:04.1f}", "name": name, "variant": key, "phonemes_sent": ph,
                     "overrides_applied": json.dumps(meta.get(vid, {}).get("phoneme_overrides_applied", {}),
                                                     ensure_ascii=False)})
        lines += [f"file '{p}'", f"file '{gap}'"]
        t += d + 0.7
    with open(os.path.join(out, "concat.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    mp3 = os.path.join(out, "name_reel.mp3")
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i",
                    os.path.join(out, "concat.txt"), "-af", "loudnorm=I=-16:TP=-1.5", "-ar", "44100", "-ac", "1",
                    "-c:a", "libmp3lame", "-b:a", "96k", mp3], check=True)
    with open(os.path.join(out, "reel_index.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(mp3, f"{t:.0f}s", len(order), "items")


if __name__ == "__main__":
    main()
