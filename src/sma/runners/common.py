"""Shared job protocol for TTS runners.

A runner is executed with the interpreter of the venv that holds its engine:
    <venv>/bin/python -m sma.runners.<engine>_runner job.json
job.json = {"engine_params": {...}, "items": [{"id": "c0001", "text": "...", "out": "/abs/c0001.wav"}]}
Existing outputs are skipped (checkpoint/resume). Each finished item prints one JSON line on stdout.
Runners only depend on numpy + their engine; no project imports beyond this file.
"""
import json
import os
import sys
import time
import wave

import numpy as np

PEAK_CEILING = 0.97  # about -0.26 dBFS; below the -0.1 dB clipping flag in sma.produce.validate


def load_job():
    if len(sys.argv) != 2:
        sys.exit("usage: runner job.json")
    with open(sys.argv[1], encoding="utf-8") as f:
        return json.load(f)


def write_wav_atomic(path, samples, sample_rate):
    """Write float mono samples as 16-bit PCM WAV via tmp + rename.

    Engines can overshoot ±1.0; scale the whole chunk down instead of hard-clipping it
    (loudness is normalised later in mastering, so only the peak changes).
    """
    x = np.asarray(samples, dtype=np.float32)
    peak = float(np.max(np.abs(x))) if x.size else 0.0
    if peak > PEAK_CEILING:
        x = x * (PEAK_CEILING / peak)
    pcm = (np.clip(x, -1.0, 1.0) * 32767).astype("<i2")
    tmp = path + ".tmp"
    with wave.open(tmp, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(int(sample_rate))
        w.writeframes(pcm.tobytes())
    os.replace(tmp, path)
    return len(pcm) / sample_rate


def run(job, synth, sample_rate, engine_name, load_sec):
    """synth(text) -> float samples. Emits progress JSON lines."""
    print(json.dumps({"event": "loaded", "engine": engine_name, "load_sec": round(load_sec, 2),
                      "sample_rate": sample_rate}), flush=True)
    for item in job["items"]:
        if os.path.exists(item["out"]):
            print(json.dumps({"event": "skip", "id": item["id"]}), flush=True)
            continue
        t0 = time.monotonic()
        try:
            audio = synth(item["text"])
            dur = write_wav_atomic(item["out"], audio, sample_rate)
        except Exception as e:  # report and continue; the pipeline decides whether to fail
            print(json.dumps({"event": "error", "id": item["id"], "error": f"{type(e).__name__}: {e}"}), flush=True)
            continue
        el = time.monotonic() - t0
        ev = {"event": "done", "id": item["id"], "synth_sec": round(el, 3), "audio_sec": round(dur, 3),
              "rtf": round(el / dur, 3) if dur else None}
        if getattr(synth, "last_meta", None):
            ev.update(synth.last_meta)
        print(json.dumps(ev, ensure_ascii=False), flush=True)
