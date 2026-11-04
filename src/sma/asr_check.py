"""Secondary intelligibility check: transcribe WAVs with a local Vietnamese ASR and compute CER/WER.

Run with the `.venv` interpreter (sherpa-onnx):
    .venv/bin/python -m sma.asr_check <model_dir> <pairs.json> <out.json>
pairs.json = [{"id": ..., "wav": "/abs.wav", "reference": "spoken-form text"}]

ASR has its own error rate: low CER suggests intelligible speech; high CER means "listen to this one first",
not proof of mispronunciation. Never the sole evidence (see FACT_CHECK_POLICY / AUDIO_PIPELINE).
"""
import json
import os
import re
import sys
import unicodedata
import wave

import numpy as np
import sherpa_onnx


def norm(text):
    text = unicodedata.normalize("NFC", text.lower())
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def edit_distance(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def error_rates(ref, hyp):
    r, h = norm(ref), norm(hyp)
    cer = edit_distance(r.replace(" ", ""), h.replace(" ", "")) / max(1, len(r.replace(" ", "")))
    wer = edit_distance(r.split(), h.split()) / max(1, len(r.split()))
    return round(cer, 4), round(wer, 4)


def read_wav(path):
    with wave.open(path) as w:
        assert w.getsampwidth() == 2 and w.getnchannels() == 1, "expects 16-bit mono"
        data = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
        return data, w.getframerate()


def load(model_dir):
    f = {k: next(os.path.join(model_dir, n) for n in os.listdir(model_dir) if n.startswith(k) and n.endswith(".onnx"))
         for k in ("encoder", "decoder", "joiner")}
    return sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=f["encoder"], decoder=f["decoder"], joiner=f["joiner"],
        tokens=os.path.join(model_dir, "tokens.txt"), num_threads=4, decoding_method="greedy_search")


def transcribe(rec, path):
    samples, sr = read_wav(path)
    s = rec.create_stream()
    s.accept_waveform(sr, samples)
    rec.decode_stream(s)
    return s.result.text


def main():
    model_dir, pairs_path, out_path = sys.argv[1:4]
    rec = load(model_dir)
    out = []
    for p in json.load(open(pairs_path, encoding="utf-8")):
        hyp = transcribe(rec, p["wav"])
        cer, wer = error_rates(p["reference"], hyp)
        out.append({"id": p["id"], "cer": cer, "wer": wer, "hypothesis": hyp, "reference": p["reference"]})
        print(json.dumps(out[-1], ensure_ascii=False), flush=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
