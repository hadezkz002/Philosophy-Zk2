#!/usr/bin/env python3
"""Benchmark local TTS engines under identical conditions (stdlib only).

Usage: python3 tools/bench_tts.py <out_dir> <config_name> [...]
Each config runs its runner in its own venv, one at a time (never concurrent),
sampling RSS / CPU time / CPU + battery temperature every 0.5 s. Results -> <out_dir>/bench_results.json
"""
import glob
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS = os.path.expanduser("~/.cache/sma-models")
PIPER = [os.path.join(ROOT, ".venv/bin/python"), "-m", "sma.runners.piper_runner"]
VIENEU = [os.path.join(ROOT, ".venv-vieneu/bin/python"), "-m", "sma.runners.vieneu_runner"]

CONFIGS = {
    "piper-vais1000": (PIPER, {"model_dir": f"{MODELS}/vits-piper-vi_VN-vais1000-medium", "threads": 4}),
    "vieneu-nano": (VIENEU, {"mode": "v3nano", "seed": 7}),
    "vieneu-turbo-fp32": (VIENEU, {"mode": "v3turbo", "precision": "fp32", "seed": 7,
                                     "onnx_dir": f"{MODELS}/vieneu-turbo-fp32-onnx"}),
    "vieneu-turbo-int8": (VIENEU, {"mode": "v3turbo", "precision": "int8", "seed": 7}),
}
CLK = os.sysconf("SC_CLK_TCK")


def temps():
    cpu = []
    for z in glob.glob("/sys/class/thermal/thermal_zone*"):
        try:
            if open(f"{z}/type").read().startswith(("cpu-", "cpuss")):
                v = int(open(f"{z}/temp").read())
                if v > 0:
                    cpu.append(v / 1000)
        except OSError:
            pass
    try:
        batt = int(open("/sys/class/power_supply/battery/temp").read()) / 10
    except OSError:
        batt = None
    return (max(cpu) if cpu else None), batt


def tree(pid):
    """pid plus descendants (runner may not fork, but be safe)."""
    pids, frontier = {pid}, [pid]
    while frontier:
        p = frontier.pop()
        for c in glob.glob(f"/proc/{p}/task/*/children"):
            try:
                for k in open(c).read().split():
                    if int(k) not in pids:
                        pids.add(int(k))
                        frontier.append(int(k))
            except OSError:
                pass
    return pids


def sample(pid):
    rss, ticks = 0, 0
    for p in tree(pid):
        try:
            for line in open(f"/proc/{p}/status"):
                if line.startswith("VmRSS:"):
                    rss += int(line.split()[1]) * 1024
            f = open(f"/proc/{p}/stat").read().rsplit(")", 1)[1].split()
            ticks += int(f[11]) + int(f[12])
        except (OSError, IndexError):
            pass
    return rss, ticks / CLK


def bench(name, items, out_dir):
    cmd, params = CONFIGS[name]
    d = os.path.join(out_dir, name)
    os.makedirs(d, exist_ok=True)
    job = {"engine_params": params,
           "items": [{"id": i, "text": t, "out": os.path.join(d, f"{i}.wav")} for i, t in items]}
    job_path = os.path.join(d, "job.json")
    with open(job_path, "w", encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=1)
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))
    t_cpu0, b0 = temps()
    t0 = time.monotonic()
    proc = subprocess.Popen(cmd + [job_path], stdout=subprocess.PIPE, stderr=open(os.path.join(d, "stderr.log"), "w"),
                            env=env, text=True)
    peak_rss, cpu_s, max_t, max_b = 0, 0.0, t_cpu0 or 0, b0 or 0
    events = []
    os.set_blocking(proc.stdout.fileno(), False)
    while True:
        rss, c = sample(proc.pid)
        peak_rss, cpu_s = max(peak_rss, rss), max(cpu_s, c)
        tc, tb = temps()
        max_t, max_b = max(max_t, tc or 0), max(max_b, tb or 0)
        for line in proc.stdout.readlines():
            events.append(json.loads(line))
        if proc.poll() is not None:
            events += [json.loads(l) for l in proc.stdout.readlines()]
            break
        time.sleep(0.5)
    wall = time.monotonic() - t0
    done = [e for e in events if e["event"] == "done"]
    loaded = next((e for e in events if e["event"] == "loaded"), {})
    audio = sum(e["audio_sec"] for e in done)
    synth = sum(e["synth_sec"] for e in done)
    return {"config": name, "params": params, "exit_code": proc.returncode, "wall_sec": round(wall, 1),
            "load_sec": loaded.get("load_sec"), "sample_rate": loaded.get("sample_rate"),
            "items_ok": len(done), "items_error": [e for e in events if e["event"] == "error"],
            "audio_sec": round(audio, 2), "synth_sec": round(synth, 2), "rtf": round(synth / audio, 3) if audio else None,
            "peak_rss_mib": round(peak_rss / 2**20), "cpu_sec": round(cpu_s, 1),
            "avg_cores_busy": round(cpu_s / wall, 2) if wall else None,
            "cpu_temp_start_c": t_cpu0, "cpu_temp_max_c": max_t, "batt_temp_start_c": b0, "batt_temp_max_c": max_b}


def main():
    out_dir, names = sys.argv[1], sys.argv[2:]
    items = json.load(open(os.path.join(ROOT, "production/benchmarks/bench_items.json"), encoding="utf-8"))
    path = os.path.join(out_dir, "bench_results.json")
    results = json.load(open(path)) if os.path.exists(path) else {}
    for n in names:
        print(f"== {n}", flush=True)
        results[n] = bench(n, [(i["id"], i["text"]) for i in items], out_dir)
        print(json.dumps(results[n], ensure_ascii=False), flush=True)
        with open(path, "w") as f:
            json.dump(results, f, ensure_ascii=False, indent=1)
        time.sleep(30)  # cool-down between engines so thermal readings are comparable


if __name__ == "__main__":
    main()
