"""Vietnamese narration text normalization (stdlib only).

Order: strip script markup -> pronunciation dictionary -> units -> numbers -> whitespace.
The approved script text is never edited; normalization produces a separate spoken form that is stored
next to every chunk so reviewers can diff "what was approved" vs "what was sent to TTS".
"""
import json
import re

DIGITS = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
SCALES = ["", "nghìn", "triệu", "tỷ"]


def read_triplet(n, full):
    """Read 0..999. `full` forces 'không trăm' / 'linh' forms inside a larger number."""
    h, t, u = n // 100, n // 10 % 10, n % 10
    words = []
    if h or full:
        words += [DIGITS[h], "trăm"]
    if t == 0:
        if u and (h or full):
            words.append("linh")
    elif t == 1:
        words.append("mười")
    else:
        words += [DIGITS[t], "mươi"]
    if u:
        if t >= 2 and u == 1:
            words.append("mốt")
        elif t >= 1 and u == 5:
            words.append("lăm")
        elif t >= 2 and u == 4:
            words.append("tư")
        else:
            words.append(DIGITS[u])
    return words


def read_int(n):
    if n == 0:
        return "không"
    if n < 0:
        return "âm " + read_int(-n)
    if n >= 10 ** 12:  # beyond tỷ grouping: read digit by digit rather than guess
        return " ".join(DIGITS[int(d)] for d in str(n))
    groups = []
    while n:
        groups.append(n % 1000)
        n //= 1000
    words = []
    for i in range(len(groups) - 1, -1, -1):
        g = groups[i]
        if g == 0:
            continue
        words += read_triplet(g, full=i < len(groups) - 1)
        words.append(SCALES[i])
    return " ".join(w for w in words if w)


def read_decimal(int_part, frac_part):
    frac = frac_part.lstrip("0")
    zeros = " ".join(["không"] * (len(frac_part) - len(frac)))
    tail = (zeros + " " if zeros else "") + (read_int(int(frac)) if frac else "")
    return f"{read_int(int(int_part))} phẩy {tail}".strip()


NUM = re.compile(r"(?<![\w.,])(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?(?![\w])")
UNITS = [  # (regex, spoken) applied before numbers; order matters (longest first)
    (r"(?<=\d)\s*km/s\b", " ki-lô-mét trên giây"),
    (r"\bkm/s\b", "ki-lô-mét trên giây"),
    (r"(?<=\d)\s*km\b", " ki-lô-mét"),
    (r"\bkm\b", "ki-lô-mét"),
    (r"(?<=\d)\s*m/s\b", " mét trên giây"),
    (r"(?<=\d)\s*MeV\b", " triệu e-léc-trôn vôn"),
    (r"(?<=\d)\s*%", " phần trăm"),
]
MARKUP = [
    (r"<!--.*?-->", " "),
    (r"\[(?:[A-Z]\d{3}-)?C\d{2,3}\]", " "),
    (r"\*\*|__|`", ""),
    (r"[“”\"«»]", ""),
]


def strip_markup(text):
    for pat, rep in MARKUP:
        text = re.sub(pat, rep, text, flags=re.S)
    return text


def apply_lexicon(text, lexicon):
    """lexicon: list of {"pattern", "replacement", "case_sensitive"?}; longest pattern wins."""
    for e in sorted(lexicon, key=lambda e: -len(e["pattern"])):
        flags = 0 if e.get("case_sensitive", True) else re.I
        text = re.sub(r"(?<!\w)" + re.escape(e["pattern"]) + r"(?!\w)", e["replacement"], text, flags=flags)
    return text


def numbers_to_words(text):
    def rep(m):
        int_part = m.group(1).replace(".", "")
        return read_decimal(int_part, m.group(2)) if m.group(2) else read_int(int(int_part))
    return NUM.sub(rep, text)


def normalize(text, lexicon=()):
    text = strip_markup(text)
    text = apply_lexicon(text, lexicon)
    for pat, rep in UNITS:
        text = re.sub(pat, rep, text)
    text = numbers_to_words(text)
    return re.sub(r"\s+", " ", text).strip()


def load_lexicon(path, engine):
    """pronunciation.json entries apply to all engines unless `engines` lists specific ones."""
    with open(path, encoding="utf-8") as f:
        entries = json.load(f)["entries"]
    return [e for e in entries if not e.get("engines") or engine in e["engines"]]


if __name__ == "__main__":
    import sys
    print(normalize(sys.stdin.read()))
