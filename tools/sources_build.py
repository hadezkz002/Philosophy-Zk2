#!/usr/bin/env python3
"""Build <ep>/sources.md from the source IDs used in <ep>/claims.csv and research/PHILOSOPHY_SOURCE_REGISTER.md.

    python3 tools/sources_build.py episodes/P001 [--notes notes.md]

Keeps everything from the first "## " heading of an existing sources.md (supplementary quotes, notes) unless
--notes gives a file to use instead. Also fills empty `doi` cells in claims.csv from the register.
"""
import argparse
import csv
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HDR = ("| ID | Nguồn | Loại | URL / DOI | Đoạn hỗ trợ (trích ngắn) | Trạng thái học thuật | Tin cậy |\n"
       "|---|---|---|---|---|---|---|")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--notes")
    a = ap.parse_args()
    register, pre = "PHILOSOPHY_SOURCE_REGISTER.md", "PS"
    reg = open(os.path.join(ROOT, "research", register), encoding="utf-8").read()
    rows = {m.group(1): m.group(0) for m in re.finditer(rf"^\| ({pre}\d+) \|.*$", reg, re.M)}
    doi = {m.group(1): m.group(2) for m in
           re.finditer(rf"^\| ({pre}\d+) \|[^|]*\| (?:peer_reviewed|review|reference_work) \| DOI (\S+)", reg, re.M)}
    cpath = os.path.join(a.episode, "claims.csv")
    claims = list(csv.DictReader(open(cpath, encoding="utf-8")))
    ids = sorted({s for c in claims for s in c["source_ids"].split(";") if s}, key=lambda x: int(x[2:]))
    missing = [i for i in ids if i not in rows]
    if missing:
        raise SystemExit(f"not in register: {missing}")
    for c in claims:  # fill DOIs the author left blank
        if not c["doi"] and c["evidence_type"] in ("peer_reviewed", "review"):
            c["doi"] = ";".join(doi[s] for s in c["source_ids"].split(";") if s in doi)
    with open(cpath, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(claims[0].keys()))
        w.writeheader()
        w.writerows(claims)
    spath = os.path.join(a.episode, "sources.md")
    tail = ""
    if a.notes:
        tail = open(a.notes, encoding="utf-8").read()
    elif os.path.exists(spath):
        old = open(spath, encoding="utf-8").read()
        i = old.find("\n## ")
        tail = old[i + 1:] if i >= 0 else ""
    head = (f"Trích từ `research/{register}`. Nguyên tác, SEP/IEP qua `tools/research.py web` hoặc `add`, bài báo qua abstract"
            " NCBI; bản cache: `~/.cache/sma-research/src/`.\n\n")
    open(spath, "w", encoding="utf-8").write(head + HDR + "\n" + "\n".join(rows[i] for i in ids) + "\n\n" + tail)
    print(f"{len(ids)} sources, {len(claims)} claims -> {spath}")


if __name__ == "__main__":
    main()
