#!/usr/bin/env python3
"""Source research helper (stdlib + curl). Everything is cached under ~/.cache/sma-research/src/.

    python3 tools/research.py si <path> [<path>...]        # Smithsonian Human Origins page -> clean text
    python3 tools/research.py pm-search "<query>" [n]      # PubMed search -> pmid | author year | journal | title | doi
    python3 tools/research.py pm <pmid>[,<pmid>...]        # PubMed abstracts (cached per PMID)
    python3 tools/research.py quote "<regex>" [name...]    # find a quote in cached texts (verify before citing)
    python3 tools/research.py clock <Ma> [<Ma>...]         # one-day clock (7 Myr = 24 h) used by the series
    python3 tools/research.py web <name> <url>             # any public page (SEP, IEP, SuttaCentral, ctext…) -> clean text
    python3 tools/research.py add <name> <file> [<url>]    # a text you obtained another way (e.g. from Google Drive)

Rules (production/EPISODE_PLAYBOOK.md): cite only text that `quote` finds in a cached source; TLS is never
disabled; PubMed abstracts only (no paywalled full text).
"""
import html
import json
import os
import re
import subprocess
import sys
import urllib.parse

CACHE = os.path.expanduser("~/.cache/sma-research/src")
SI = "https://humanorigins.si.edu/"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def fetch(url):
    r = subprocess.run(["curl", "-sL", "--max-time", "40", "-A", "Mozilla/5.0 (SMA research)", url],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"fetch failed ({r.returncode}): {url}")
    return r.stdout


def si_text(raw):
    """Body text of a Smithsonian page: from 'Discovery Date' (species) or the last page-URL echo to the footer."""
    t = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style).*?</\1>", "", raw, flags=re.S)))
    t = re.sub(r"\s+", " ", t)
    k = t.find("Discovery Date")
    if k < 0:
        urls = list(re.finditer(r"https://humanorigins\.si\.edu/\S+", t))
        k = urls[-1].end() if urls else 0
    end = t.find("© Copyright Smithsonian Institution For Press", k)
    return t[k:end if end > 0 else None].strip()


def cmd_si(paths):
    os.makedirs(CACHE, exist_ok=True)
    for p in paths:
        p = p.replace(SI, "").strip("/")
        txt = si_text(fetch(SI + p))
        name = "si_" + re.sub(r"\W+", "_", p) + ".txt"
        with open(os.path.join(CACHE, name), "w", encoding="utf-8") as f:
            f.write(f"URL: {SI}{p}\n\n{txt}\n")
        print(f"== {name} ({len(txt)} chars)\n{txt[:1500]}\n")


def page_text(raw):
    """Readable text of a generic HTML page: drop scripts/styles/nav/footer, strip tags, collapse spaces."""
    raw = re.sub(r"<(script|style|nav|header|footer|noscript)\b.*?</\1>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<(br|p|div|li|h[1-6]|tr|blockquote)\b[^>]*>", "\n", raw, flags=re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    t = re.sub(r"[ \t\r\f\v]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n\n", t).strip()


def cache_name(prefix, name):
    return f"{prefix}_" + re.sub(r"\W+", "_", name).strip("_") + ".txt"


def save(fname, url, txt):
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, fname), "w", encoding="utf-8") as f:
        f.write(f"URL: {url}\n\n{txt}\n")
    print(f"== {fname} ({len(txt)} chars)\n{txt[:1500]}\n")


def cmd_web(name, url):
    """Cache a public page under web_<name>.txt. Record the page's own revision date in the register."""
    save(cache_name("web", name), url, page_text(fetch(url)))


def cmd_add(name, path, url=""):
    """Cache a text obtained outside this tool (Drive upload, library PDF converted to text) as local_<name>.txt.
    The register row must say where it came from; `quote` treats it like any other cached source."""
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    save(cache_name("local", name), url or f"local file {os.path.basename(path)}", txt.strip())


def cmd_pm_search(q, n=5):
    ids = json.loads(fetch(EUTILS + "esearch.fcgi?db=pubmed&retmode=json&retmax=%d&term=%s" % (int(n), urllib.parse.quote(q))))
    ids = ids["esearchresult"]["idlist"]
    if not ids:
        print("(no results)")
        return
    res = json.loads(fetch(EUTILS + "esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(ids)))["result"]
    for i in res["uids"]:
        r = res[i]
        doi = next((a["value"] for a in r["articleids"] if a["idtype"] == "doi"), "")
        print(f"{i} | {r['sortfirstauthor']} {r['pubdate'][:4]} | {r['source']} {r.get('volume', '')}:{r.get('pages', '')} | {r['title']} | {doi}")


def abstract_of(block):
    """Longest paragraph that is not author/affiliation metadata."""
    paras = [re.sub(r"\s+", " ", p) for p in re.split(r"\n\s*\n", block)]
    paras = [p for p in paras if not re.match(r"^(Author information|\(\d+\)|DOI:|PMID:|Copyright|Comment|Erratum)", p)]
    return max(paras, key=len) if paras else ""


def cmd_pm(ids):
    os.makedirs(CACHE, exist_ok=True)
    ids = [i for i in re.split(r"[,\s]+", ids) if i]
    todo = [i for i in ids if not os.path.exists(os.path.join(CACHE, f"pm_{i}.txt"))]
    if todo:
        raw = fetch(EUTILS + "efetch.fcgi?db=pubmed&rettype=abstract&retmode=text&id=" + ",".join(todo))
        for blk in re.split(r"\n(?=\d+\. [A-Z])", raw.strip()):
            pm = re.search(r"PMID: (\d+)", blk)
            if pm:
                with open(os.path.join(CACHE, f"pm_{pm.group(1)}.txt"), "w", encoding="utf-8") as f:
                    f.write(blk.strip() + "\n")
    for i in ids:
        p = os.path.join(CACHE, f"pm_{i}.txt")
        if not os.path.exists(p):
            print(f"== {i}: not found")
            continue
        blk = open(p, encoding="utf-8").read()
        head = re.sub(r"\s+", " ", " ".join(blk.splitlines()[:3]))[:200]
        print(f"== {i} | {head}\n{abstract_of(blk)}\n")


def cmd_quote(pattern, names):
    rx = re.compile(pattern, re.I)
    files = sorted(os.listdir(CACHE))
    if names:
        files = [f for f in files if any(n in f for n in names)]
    hits = 0
    for f in files:
        t = re.sub(r"\s+", " ", open(os.path.join(CACHE, f), encoding="utf-8").read())
        for m in rx.finditer(t):
            hits += 1
            print(f"{f}: …{t[max(0, m.start() - 160):m.end() + 160]}…")
    print(f"({hits} hits)")


def clock(ma):
    """Clock time when 7 million years = 24 hours (H001 convention)."""
    h = 24 * (1 - ma / 7)
    return f"{int(h):02d}:{round(h % 1 * 60):02d}"


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "si":
        cmd_si(args)
    elif cmd == "pm-search":
        cmd_pm_search(args[0], args[1] if len(args) > 1 else 5)
    elif cmd == "pm":
        cmd_pm(",".join(args))
    elif cmd == "quote":
        cmd_quote(args[0], args[1:])
    elif cmd == "web" and len(args) == 2:
        cmd_web(args[0], args[1])
    elif cmd == "add" and len(args) in (2, 3):
        cmd_add(*args)
    elif cmd == "clock":
        for a in args:
            print(f"{a} Ma -> {clock(float(a))}")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    assert clock(7) == "00:00" and clock(0.3) == "22:58" and clock(4.4) == "08:55"
    main()
