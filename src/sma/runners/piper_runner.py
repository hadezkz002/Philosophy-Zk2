"""Piper (VITS) Vietnamese voice through sherpa-onnx. Run with the `.venv` interpreter."""
import os
import time

import sherpa_onnx

from sma.runners.common import load_job, run


def main():
    job = load_job()
    p = job["engine_params"]
    d = os.path.expanduser(p["model_dir"])
    name = p.get("model_file") or next(f for f in os.listdir(d) if f.endswith(".onnx"))
    t0 = time.monotonic()
    cfg = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                model=os.path.join(d, name), tokens=os.path.join(d, "tokens.txt"),
                data_dir=os.path.join(d, "espeak-ng-data"),
                length_scale=float(p.get("length_scale", 1.0))),
            num_threads=int(p.get("threads", 4)), provider="cpu"),
        max_num_sentences=1)
    tts = sherpa_onnx.OfflineTts(cfg)
    load = time.monotonic() - t0

    def synth(text):
        return tts.generate(text, sid=int(p.get("sid", 0)), speed=float(p.get("speed", 1.0))).samples

    run(job, synth, tts.sample_rate, f"piper:{name}", load)


if __name__ == "__main__":
    main()
