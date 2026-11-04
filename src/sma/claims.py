"""Validate an episode's claim ledger against its script and source list.

Usage: python3 -m sma.claims episodes/<id>   (exit 1 on any error)
Checks: required columns, allowed labels, every [Cxxx] tag in script.md exists in claims.csv and vice versa,
every source_id is defined in sources.md, sourced categories have sources, and no claim is PENDING/REJECTED
when --release is given.
"""
import csv
import os
import re
import sys

COLUMNS = ["claim_id", "claim_vi", "category", "evidence_type", "source_ids", "doi", "supporting_location",
           "confidence", "assumptions", "limitations", "reviewer_status", "reviewer_note"]
REQUIRED = ["claim_id", "claim_vi", "category", "evidence_type", "supporting_location", "confidence", "reviewer_status"]
CATEGORIES = {"ESTABLISHED", "OBSERVED", "DERIVED", "HYPOTHESIS", "SPECULATION", "ANALOGY", "FICTION", "HISTORICAL",
              "DEFINITION",
              # history series (HUMAN_HISTORY_SERIES_BIBLE.md)
              "FOSSIL", "ARCHAEOLOGICAL", "GENETIC", "CONTEMPORARY_TEXT", "LATER_HISTORIOGRAPHY", "CONTESTED",
              "RECONSTRUCTION", "STORYTELLER_CONJECTURE",
              # philosophy series (PHILOSOPHY_SERIES_BIBLE.md)
              "PRIMARY_TEXT", "TRANSLATION_NOTE", "INTERPRETATION", "ARGUMENT_RECONSTRUCTION", "OBJECTION",
              "THOUGHT_EXPERIMENT", "MISATTRIBUTION", "NARRATOR_VIEW"}
EVIDENCE = {"standard", "peer_reviewed", "review", "textbook", "institutional", "historical_primary",
            "historical_secondary", "calculation", "PREPRINT", "none",
            # philosophy series: a primary text in a named translation; a peer-reviewed reference work (SEP, IEP)
            "primary_text", "reference_work"}
UNSOURCED_OK = {"ANALOGY", "FICTION", "RECONSTRUCTION", "STORYTELLER_CONJECTURE", "NARRATOR_VIEW"}
STATUSES = {"PENDING", "APPROVED", "REVISED", "REJECTED"}
TAG = re.compile(r"\[((?:[A-Z]\d{3}-)?C\d{2,3})\]")  # C001 (pilot), H001-C01 (history), P001-C01 (philosophy)
SOURCE_DEF = re.compile(r"^\|\s*([A-Z]?S\d{2,3})\s*\|", re.M)  # S01, HS01/HS101 (history), PS01/PS101 (philosophy)


def validate(ep_dir, release=False, partial=False):
    errors = []
    with open(os.path.join(ep_dir, "claims.csv"), encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != COLUMNS:
            errors.append(f"columns must be exactly {COLUMNS}, got {reader.fieldnames}")
            return errors, {}
        rows = list(reader)
    with open(os.path.join(ep_dir, "sources.md"), encoding="utf-8") as f:
        sources = set(SOURCE_DEF.findall(f.read()))
    with open(os.path.join(ep_dir, "script.md"), encoding="utf-8") as f:
        script_tags = TAG.findall(re.sub(r"<!--.*?-->", "", f.read(), flags=re.S))  # comments are not narrated

    ids = [r["claim_id"] for r in rows]
    for dup in {i for i in ids if ids.count(i) > 1}:
        errors.append(f"duplicate claim_id {dup}")
    for r in rows:
        cid = r["claim_id"]
        for col in REQUIRED:
            if not r[col].strip():
                errors.append(f"{cid}: empty {col}")
        if r["category"] not in CATEGORIES:
            errors.append(f"{cid}: bad category {r['category']}")
        if r["evidence_type"] not in EVIDENCE:
            errors.append(f"{cid}: bad evidence_type {r['evidence_type']}")
        if r["confidence"] not in {"high", "medium", "low"}:
            errors.append(f"{cid}: bad confidence {r['confidence']}")
        if r["reviewer_status"] not in STATUSES:
            errors.append(f"{cid}: bad reviewer_status {r['reviewer_status']}")
        srcs = [s for s in r["source_ids"].split(";") if s.strip()]
        if r["category"] not in UNSOURCED_OK and not srcs:
            errors.append(f"{cid}: {r['category']} claim needs source_ids")
        for s in srcs:
            if s.strip() not in sources:
                errors.append(f"{cid}: source {s} not defined in sources.md")
        # partial (proof) release: only claims actually narrated must be approved
        if release and r["reviewer_status"] in {"PENDING", "REJECTED"} and (not partial or cid in script_tags):
            errors.append(f"{cid}: status {r['reviewer_status']} blocks release")
    for t in sorted(set(script_tags) - set(ids)):
        errors.append(f"script tag [{t}] missing from claims.csv")
    if not partial:  # --partial: proof scripts cover only some beats of the outline
        for t in sorted(set(ids) - set(script_tags)):
            errors.append(f"claim {t} never tagged in script.md")
    stats = {"claims": len(rows), "script_tags": len(set(script_tags)), "sources": len(sources),
             "by_status": {s: sum(r["reviewer_status"] == s for r in rows) for s in STATUSES}}
    return errors, stats


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    errors, stats = validate(args[0], release="--release" in sys.argv, partial="--partial" in sys.argv)
    print(stats)
    for e in errors:
        print("ERROR", e)
    print("CLAIMS_OK" if not errors else f"CLAIMS_FAIL ({len(errors)} errors)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
