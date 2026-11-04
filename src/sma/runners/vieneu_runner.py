"""VieNeu-TTS v3 (Turbo or Nano) on CPU/ONNX. Run with the `.venv-vieneu` interpreter.

engine_params: mode ("v3turbo" | "v3nano"), voice (preset name), precision (turbo: fp32|int8), onnx_dir,
temperature, seed, watermark (bool, default True: keep the SDK's AI-audio watermark),
phoneme_overrides: [{"text": "LIGO", "phonemes": "lˈaɪɡoʊ"}] (Turbo only).

Phoneme overrides: the engine lowercases and normalizes text (acronyms become Vietnamese letter names) and then
phonemizes each chunk with sea-g2p, which sends non-Vietnamese words to an English G2P ("fluent but wrong" names).
Each lexicon name is swapped for a letters-only placeholder that survives normalization, and the phonemizer is
wrapped to insert the name's target phoneme string at the placeholder. The canonical script text is untouched.
"""
import os
import random
import time

import numpy as np

from sma.runners.common import load_job, run


def main():
    job = load_job()
    p = job["engine_params"]
    from vieneu import Vieneu

    mode = p.get("mode", "v3turbo")
    kwargs = {"precision": p["precision"]} if mode == "v3turbo" and p.get("precision") else {}
    if p.get("onnx_dir"):  # real-file copy: onnxruntime>=1.31 rejects external data reached via HF cache symlinks
        kwargs["onnx_dir"] = os.path.expanduser(p["onnx_dir"])
    for k in ("backend", "device"):  # e.g. backend="pytorch", device="cuda" on a Colab GPU (tools/colab_render.py)
        if p.get(k):
            kwargs[k] = p[k]
    t0 = time.monotonic()
    tts = Vieneu(mode=mode, **kwargs)
    load = time.monotonic() - t0
    voice = p.get("voice")
    seed = p.get("seed")
    encode, applied = install_phoneme_overrides(p.get("phoneme_overrides") or []) if mode == "v3turbo" else (None, None)

    def synth(text):
        if seed is not None:  # best-effort determinism for re-renders
            random.seed(seed)
            np.random.seed(seed)
        extra = {"temperature": float(p["temperature"])} if "temperature" in p and mode == "v3turbo" else {}
        if applied is not None:
            applied.clear()
        wav = tts.infer(encode(text) if encode else text, voice=voice, apply_watermark=bool(p.get("watermark", True)), **extra)
        synth.last_meta = {"phoneme_overrides_applied": dict(applied)} if applied else None
        return wav

    run(job, synth, tts.sample_rate, f"vieneu:{mode}:{p.get('precision', '')}:{voice}", load)


def install_phoneme_overrides(overrides):
    """Patch vieneu's chunk phonemizer. Returns (encode, applied): `encode(text)` swaps names for placeholders
    before tts.infer; `applied` counts inserted overrides per name.

    Names match exact, case-sensitive, whole word, longest first, on the canonical text. Matching after the
    engine's normalizer is impossible: it lowercases and spells acronyms ("DNA" -> "đê nờ a").
    """
    if not overrides:
        return None, None
    import re
    import string
    import vieneu.v3turbo as vt
    names = sorted(overrides, key=lambda o: -len(o["text"]))  # longest first
    # placeholder = "qzxname" + letters (digits would be read as numbers); survives lowercasing/normalization
    tag = {o["text"]: "qzxname" + "".join(string.ascii_lowercase[int(d)] for d in f"{i:02d}")
           for i, o in enumerate(names)}
    name_re = re.compile("|".join(r"(?<!\w)" + re.escape(o["text"]) + r"(?!\w)" for o in names))
    pattern = re.compile(r"(?<!\w)qzxname[a-z]{2}(?!\w)")
    target = {tag[o["text"]]: (o["text"], o["phonemes"]) for o in names}
    original = vt.phonemize_text_with_emotions
    applied = {}
    LEADING_PUNCT = re.compile(r"^\s*[.!?…,;:\"'”)]*\s*")

    def encode(text):
        return name_re.sub(lambda m: tag[m.group(0)], text)

    def fragment(text):
        """Phonemize a mid-sentence fragment without the sentence-final punctuation the G2P appends."""
        ph = original(text).strip()
        if text.rstrip()[-1:] not in ".!?…,;:" and ph[-1:] in ".!?…":
            ph = ph[:-1].rstrip()
        return ph

    def patched(chunk):
        out, pos = [], 0
        for m in pattern.finditer(chunk):
            before = chunk[pos:m.start()]
            lead = LEADING_PUNCT.match(before).group(0)
            if out and lead.strip():  # punctuation right after the previous name belongs to it
                out[-1] += lead.strip()
            before = before[len(lead):]
            if before.strip():
                out.append(fragment(before))
            name, ph = target[m.group(0)]
            out.append(ph)
            applied[name] = applied.get(name, 0) + 1
            pos = m.end()
        if pos == 0:
            return original(chunk)
        rest = chunk[pos:]
        lead = LEADING_PUNCT.match(rest).group(0)
        out[-1] += lead.strip()  # keep the comma/full stop (and its pause) right after the name
        rest = rest[len(lead):]
        if rest.strip():
            out.append(original(rest).strip())
        return " ".join(x for x in out if x)

    vt.phonemize_text_with_emotions = patched
    return encode, applied


if __name__ == "__main__":
    main()
