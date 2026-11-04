"""Proper-name extraction and lexicon resolution (stdlib only).

    python3 -m sma.names episodes/<id>          # list candidate names and their lexicon status

Candidates = tokens a Vietnamese G2P is likely to misread: words containing letters outside the Vietnamese
alphabet (f j w z, ø, ö…), ALL-CAPS acronyms, and capitalised non-Vietnamese words/phrases mid-sentence.
The canonical script is never modified; resolution happens per engine in `sma.produce.plan`.
"""
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEXICON = os.path.join(ROOT, "production", "PRONUNCIATION_LEXICON.json")
# Statuses whose TTS rendering may be used (still subject to human listening before release).
USABLE = {"TTS_CANDIDATE", "NEEDS_HUMAN_REVIEW", "LISTENED_OK"}
BLOCKING = {"PENDING_RESEARCH", "UNRESOLVED", "REJECTED"}

UNITS = {"km", "m", "s", "kg", "MeV", "Hz", "km/s"}  # read by sma.textnorm unit rules, not names
VI_TONED = re.compile(r"[àáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵăâđêôơư]", re.I)
# Capitalised Vietnamese words without diacritics that legitimately appear mid-sentence.
VI_PLAIN_CAPS = {"Sao", "Hai", "Ba", "Nam", "Bac", "Ta", "Anh", "Em", "Con", "Hoa", "Ma"}


# Approximate Vietnamese syllable (diacritics stripped): onset + vowel cluster + coda.
# ponytail: heuristic, not a full phonotactic model; false positives only add names to review.
VI_SYLLABLE = re.compile(
    r"^(ngh|ng|nh|ch|gh|gi|kh|ph|th|tr|qu|b|c|d|g|h|k|l|m|n|p|r|s|t|v|x)?"
    r"(uye|uya|ieu|yeu|uoi|uou|oai|oay|oeo|uay|ia|ie|ua|uo|ai|ao|au|ay|eo|eu|iu|oa|oe|oi|ue|ui|uu|uy|ye|a|e|i|o|u|y)"
    r"(ch|ng|nh|c|m|n|p|t)?$")


def is_vietnamese_word(w):
    """True if every hyphen-separated part looks like a Vietnamese syllable."""
    for part in w.split("-"):
        base = unicodedata.normalize("NFD", part.lower()).replace("\u0111", "d")
        base = "".join(c for c in base if unicodedata.category(c) != "Mn").replace("đ", "d")
        if not base or not VI_SYLLABLE.match(base):
            return False
    return True


def candidates(text):
    """Return ordered unique candidate names found in narration text."""
    text = re.sub(r"<!--.*?-->|\[((?:[A-Z]\d{3}-)?C\d{2,3}|PAUSE)\]", " ", text, flags=re.S)
    found = []

    def add(x):
        if x not in found:
            found.append(x)

    for line in text.splitlines():
        if line.startswith(("#", ">")) and not line.startswith("# "):
            continue
        for sent in re.split(r"(?<=[.!?…:])\s+", line):
            tokens = re.findall(r"[\w'’-]+", sent)
            run = []
            for i, t in enumerate(tokens):
                if t in UNITS:
                    t = ""
                foreign = bool(t) and (t.isalpha() or "-" in t) and (
                    not is_vietnamese_word(t) or (t.isupper() and len(t) >= 2))
                cap_mid = i > 0 and t[:1].isupper() and not VI_TONED.search(t) and t not in VI_PLAIN_CAPS
                if t and (foreign or (cap_mid and not is_vietnamese_word(t))):
                    run.append(t)
                else:
                    if run:
                        add(" ".join(run))
                    run = []
            if run:
                add(" ".join(run))
    return found


# Reference IPA -> the notation VieNeu's English G2P emits (misaki-style: US vowels, stress mark right before
# the stressed vowel, no syllable dots). Symbols the engine never saw are mapped to the nearest seen one and
# reported, so every approximation is recorded in the lexicon's `derived_from`.
IPA_MAP = [("t͡ʃ", "tʃ"), ("d͡ʒ", "dʒ"), ("əʊ", "oʊ"), ("i:", "iː"), ("ɝ", "ɜː"), ("ɒ", "ɑː"), ("ɨ", "ɪ"),
           ("g", "ɡ"), ("ʁ", "ɹ"), ("œ", "ɜ"), ("ø", "ɜ"), ("ʒ", "ʒ")]
APPROX = {"ʁ": "ɹ", "œ": "ɜ", "ø": "ɜ", "ˀ": "", "ʔ": "", "ɝ": "ɜː", "ɒ": "ɑː", "ɨ": "ɪ"}  # vowel/consonant substitutions
DROP = "/[].‿̯͡ˀʔ"
VOWELS = set("aeiouæɑɒɔəɚɛɜɪʊʌøœɐɨyɝɵʉ")


def ipa_to_engine(ipa, lang="en"):
    """Return (engine phonemes, approximations used). Optional '(x)' segments are dropped.
    /r/ is English ɹ for lang 'en', a tap ɾ otherwise (it, es, ka…)."""
    approx = sorted({k for k in APPROX if k in ipa})
    s = re.sub(r"\([^)]*\)", "", ipa)
    s = re.sub(r"ər(?![aeiouæɑɒɔəɛɜɪʊʌ])", "ɚ", s)  # rhotic schwa before a consonant or word end
    for a, b in IPA_MAP + [("r", "ɹ" if lang == "en" else "ɾ")]:
        s = s.replace(a, b)
    s = "".join(c for c in s if c not in DROP)
    out, pending = [], ""
    for c in s:  # move each stress mark from the syllable onset to just before its vowel
        if c in "ˈˌ":
            pending = c
        elif c in VOWELS and pending:
            out.append(pending + c)
            pending = ""
        else:
            out.append(c)
    return re.sub(r"\s+", " ", "".join(out)).strip(), approx


def load_lexicon(path=LEXICON):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["entries"]


def resolve(names, entries, episode_respell=()):
    """Map each candidate to (status, entry). Matches whole entries or multi-word names containing them."""
    by = {e["original"]: e for e in entries}
    respelled = {e["pattern"] for e in episode_respell}
    out = {}
    for n in names:
        e = by.get(n) or next((by[k] for k in sorted(by, key=len, reverse=True) if re.search(
            r"(?<!\w)" + re.escape(k) + r"(?!\w)", n)), None)
        if e:
            out[n] = (e["status"], e)
        elif n in respelled or any(p in n for p in respelled):
            out[n] = ("EPISODE_RESPELL", None)
        else:
            out[n] = ("NOT_IN_LEXICON", None)
    return out


def main():
    ep = sys.argv[1]
    with open(os.path.join(ep, "script.md"), encoding="utf-8") as f:
        names = candidates(f.read())
    pron = os.path.join(ep, "pronunciation.json")
    respell = json.load(open(pron, encoding="utf-8"))["entries"] if os.path.exists(pron) else []
    res = resolve(names, load_lexicon(), respell)
    for n, (st, _) in res.items():
        print(f"{st:18s} {n}")
    blocked = [n for n, (st, _) in res.items() if st in BLOCKING or st == "NOT_IN_LEXICON"]
    print(f"{len(names)} candidates, {len(blocked)} unresolved")
    sys.exit(1 if blocked else 0)


if __name__ == "__main__":
    main()
