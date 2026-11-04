#!/usr/bin/env python3
"""Secondary intelligibility check for a rendered episode (run with system python3; calls the .venv ASR).

    python3 tools/asr_report.py episodes/P001

Writes <build>/asr_check.json and prints the median CER plus the worst Vietnamese-only chunks (sentences with
foreign names are excluded from the worst list: a Vietnamese ASR cannot spell them). ASR is never sole evidence:
suspects are re-rendered with another seed; identical ASR + normal speaking rate = ASR bias, not a TTS word drop
(EPISODE_PLAYBOOK.md §QA).
"""
import json
import os
import statistics
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from sma import names, produce  # noqa: E402

MODEL = os.path.expanduser("~/.cache/sma-models/sherpa-onnx-zipformer-vi-int8-2025-04-20")
ep = sys.argv[1]
engine = "vieneu-turbo-fp32"
plan = produce.load_plan(ep, engine)
d = produce.build_dir(ep, engine)
speech = [s for s in plan["segments"] if s["kind"] == "speech"]
pairs = os.path.join(d, "asr_pairs.json")
json.dump([{"id": s["id"], "wav": produce.chunk_path(d, s), "reference": s["spoken_text"]} for s in speech],
          open(pairs, "w"), ensure_ascii=False)
out = os.path.join(d, "asr_check.json")
subprocess.run([os.path.join(ROOT, ".venv/bin/python"), "-m", "sma.asr_check", MODEL, pairs, out],
               env=dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src")), check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
r = json.load(open(out))
r = r["results"] if isinstance(r, dict) else r
foreign = {s["id"] for s in speech if names.candidates(s["spoken_text"])}
med = statistics.median(x["cer"] for x in r)
print(f"chunks {len(r)}  median CER {med:.4f}")
for x in sorted((x for x in r if x["id"] not in foreign), key=lambda x: -x["cer"])[:8]:
    print(f"{x['cer']:.3f} {x['id']}\n   ASR {x['hypothesis'][:110]}\n   REF {x['reference'][:110]}")
