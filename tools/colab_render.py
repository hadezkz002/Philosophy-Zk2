#!/usr/bin/env python3
"""Render an episode's missing TTS chunks on a Colab GPU, then hand them back to the local pipeline.

    python3 tools/colab_render.py episodes/P001 [--backend gpu:T4] [--limit N] [--only s001,s002]

Planning, gates, validation, mastering and music stay local (sma.produce / tools/run_episode.sh). This tool only
replaces the heavy `render` step: it builds a job from the local plan (same text, voice, seed, watermark and phoneme
overrides), runs the unchanged `sma.runners.vieneu_runner` on Colab through the `colabjob` adapter (owned session,
PyTorch backend on CUDA), downloads the WAVs into the plan's chunk paths and records provenance in
<build>/colab_render.json. Afterwards `tools/run_episode.sh <ep>` finds every chunk present and only validates/masters.
Uploaded: the narration texts (public episode script) and four runner source files. Nothing else leaves the phone.

Drive route (no `colabjob`, e.g. a cloud session or a laptop): `--bundle DIR` writes the same three job files to DIR;
put them in MyDrive/Science_Media_Academy/colab_jobs/<job>/, run tools/colab/SMA_Drive_Render.ipynb in Colab (GPU
runtime), then `--ingest <that folder>/sma_out.tar`. The remote script is the same REMOTE string in both routes.
"""
import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from sma import produce  # noqa: E402

REMOTE = r'''
import json, os, subprocess, sys, tarfile, time
t0 = time.time()
def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"$ {cmd[:80]} -> {r.returncode}", flush=True)
    if r.returncode:
        print(r.stdout[-1500:], r.stderr[-1500:], flush=True)
        raise SystemExit(r.returncode)
import torch
print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NONE", flush=True)
if not torch.cuda.is_available():
    raise SystemExit("no CUDA device: refusing to render on CPU and call it GPU")
sh("pip install -q vieneu==3.8.3")
os.makedirs("/content/sma_src", exist_ok=True)
tarfile.open("/content/sma_runner.tar").extractall("/content/sma_src")
os.makedirs("/content/sma_out", exist_ok=True)
env = dict(os.environ, PYTHONPATH="/content/sma_src")
p = subprocess.Popen([sys.executable, "-m", "sma.runners.vieneu_runner", "/content/sma_job.json"],
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
done = err = 0
for line in p.stdout:
    if line.startswith("{"):
        ev = json.loads(line)
        done += ev.get("event") == "done"
        err += ev.get("event") == "error"
        if ev.get("event") in ("loaded", "error") or done % 10 == 0:
            print(line.strip()[:300], flush=True)
p.wait()
# FLAC is lossless and about half the size of WAV: the download over the phone link is the slow step, not the GPU.
sh("cd /content/sma_out && for f in *.wav; do ffmpeg -nostdin -loglevel error -y -i \"$f\" \"${f%.wav}.flac\" && rm \"$f\"; done")
with tarfile.open("/content/sma_out.tar", "w") as t:
    t.add("/content/sma_out", arcname="sma_out")
print(json.dumps({"rc": p.returncode, "done": done, "errors": err, "seconds": round(time.time() - t0)}), flush=True)
if p.returncode or err:
    raise SystemExit(1)
'''


def prepare(a):
    """Write sma_job.json, sma_runner.tar and remote_render.py for the chunks still missing. Returns (build dir, work dir, todo)."""
    plan = produce.load_plan(a.episode, a.engine)
    d = produce.build_dir(a.episode, a.engine)
    speech = [s for s in plan["segments"] if s["kind"] == "speech"]
    if a.only:
        pre = tuple(a.only.split(","))
        todo = [s for s in speech if s["id"].startswith(pre)]
    else:
        todo = [s for s in speech if not os.path.exists(produce.chunk_path(d, s))]
    todo = todo[: a.limit] if a.limit else todo
    work = os.path.join(d, "colab")
    if not todo:
        return d, work, todo
    os.makedirs(work, exist_ok=True)
    params = {k: v for k, v in produce.ENGINES[a.engine]["params"].items() if k != "onnx_dir"}
    params.update(backend="pytorch", device="cuda", phoneme_overrides=plan.get("phoneme_overrides", []))
    name = lambda s: os.path.basename(produce.chunk_path(d, s))  # noqa: E731
    job = {"engine_params": params,
           "items": [{"id": s["id"], "text": s["spoken_text"], "out": "/content/sma_out/" + name(s)} for s in todo]}
    json.dump(job, open(os.path.join(work, "sma_job.json"), "w"), ensure_ascii=False)
    with tarfile.open(os.path.join(work, "sma_runner.tar"), "w") as t:
        for f in ("__init__.py", "runners/__init__.py", "runners/common.py", "runners/vieneu_runner.py"):
            src = os.path.join(ROOT, "src", "sma", f)
            if os.path.exists(src):
                t.add(src, arcname="sma/" + f)
            elif f.endswith("__init__.py"):
                info = tarfile.TarInfo("sma/" + f)
                t.addfile(info, io.BytesIO(b""))
    open(os.path.join(work, "remote_render.py"), "w").write(REMOTE)
    return d, work, todo


def ingest(out_tar, d, work, a, res):
    """Unpack the FLACs of sma_out.tar into the build's chunk paths (as WAV) and record provenance."""
    expected = [os.path.basename(i["out"]) for i in json.load(open(os.path.join(work, "sma_job.json")))["items"]]
    got = []
    os.makedirs(a.out_dir or os.path.join(d, "chunks"), exist_ok=True)
    with tarfile.open(out_tar) as t:
        for m in t.getmembers():
            if m.isfile() and m.name.endswith(".flac"):
                dest = os.path.join(a.out_dir or os.path.join(d, "chunks"), os.path.basename(m.name)[:-5] + ".wav")
                if os.path.basename(dest) not in expected:   # only files this job asked for
                    continue
                src, tmp = dest + ".flac.part", dest + ".part"
                open(src, "wb").write(t.extractfile(m).read())
                subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", src, "-f", "wav", tmp], check=True)
                os.remove(src)
                with wave.open(tmp) as w:   # reject truncated/invalid files before they enter the build
                    assert w.getnframes() > 0
                os.replace(tmp, dest)
                got.append(os.path.basename(dest))
    missing = [n for n in expected if n not in got]
    rec_p = os.path.join(a.out_dir or d, "colab_render.json")  # comparison runs never touch the build record
    rec = json.load(open(rec_p)) if os.path.exists(rec_p) else {"renders": []}
    rec["renders"].append({"job": res.get("id"), "backend": a.backend, "runtime_backend": "pytorch/cuda",
                           "chunks": got, "missing": missing, "stdout_tail": res.get("stdout_tail", "")[-400:]})
    json.dump(rec, open(rec_p, "w"), ensure_ascii=False, indent=1)
    print(json.dumps({"ok": not missing, "rendered": len(got), "missing": missing, "job": res.get("id"),
                      "record": rec_p}, ensure_ascii=False, indent=1))
    return missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--engine", default="vieneu-turbo-fp32")
    ap.add_argument("--backend", default="gpu:T4")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--only", help="comma-separated chunk id prefixes (e.g. s001,s014) for tests")
    ap.add_argument("--timeout", type=int, default=7200)
    ap.add_argument("--out-dir", help="extract WAVs here instead of the build's chunk dir (comparison tests)")
    ap.add_argument("--bundle", metavar="DIR", help="Drive route: copy the job files to DIR for the Colab notebook "
                    "tools/colab/SMA_Drive_Render.ipynb instead of submitting with colabjob")
    ap.add_argument("--ingest", metavar="TAR", help="Drive route: unpack sma_out.tar written by the notebook "
                    "(job files must be the ones from the matching --bundle run)")
    a = ap.parse_args()
    if a.ingest:
        d = produce.build_dir(a.episode, a.engine)
        work = os.path.join(d, "colab")
        a.backend = "drive-notebook"
        raise SystemExit(1 if ingest(a.ingest, d, work, a, {"id": "drive-notebook"}) else 0)
    d, work, todo = prepare(a)
    if not todo:
        print("all chunks present; nothing to render")
        return
    if a.bundle:
        os.makedirs(a.bundle, exist_ok=True)
        for f in ("sma_job.json", "sma_runner.tar", "remote_render.py"):
            shutil.copy(os.path.join(work, f), os.path.join(a.bundle, f))
        print(json.dumps({"bundle": a.bundle, "chunks": len(todo), "episode": os.path.basename(a.episode.rstrip("/")),
                          "next": "upload the 3 files to MyDrive/Science_Media_Academy/colab_jobs/<job>/, run the "
                                  "notebook, then --ingest the sma_out.tar it writes there"}, ensure_ascii=False, indent=1))
        return
    out_tar = os.path.join(work, "sma_out.tar")
    if os.path.exists(out_tar):
        os.remove(out_tar)
    cmd = ["colabjob", "submit", "--task", f"TTS render {len(todo)} chunks for {os.path.basename(a.episode)}",
           "--script", os.path.join(work, "remote_render.py"), "--backend", a.backend, "--mode", "session",
           "--upload", os.path.join(work, "sma_job.json") + ":/content/sma_job.json",
           "--upload", os.path.join(work, "sma_runner.tar") + ":/content/sma_runner.tar",
           "--fetch", "/content/sma_out.tar:" + out_tar, "--timeout", str(a.timeout), "--force"]
    print(f"submitting {len(todo)} chunks to Colab {a.backend}", file=sys.stderr)
    r = subprocess.run(cmd, capture_output=True, text=True)
    sys.stderr.write(r.stderr[-2000:])
    res = json.loads(r.stdout) if r.stdout.strip().startswith("{") else {"ok": False, "raw": r.stdout[-1000:]}
    if not res.get("ok") or not os.path.exists(out_tar):
        print(json.dumps(res, ensure_ascii=False, indent=1))
        raise SystemExit("Colab render failed; chunks left untouched (see job logs: colabjob logs <id>)")
    missing = ingest(out_tar, d, work, a, res)
    subprocess.run(["colabjob", "cleanup"], capture_output=True)  # release the owned GPU runtime
    raise SystemExit(1 if missing else 0)


if __name__ == "__main__":
    main()
