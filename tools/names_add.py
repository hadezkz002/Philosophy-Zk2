#!/usr/bin/env python3
"""Add every name the gate reports as NOT_IN_LEXICON to the lexicon with the engine's own reading.

    python3 tools/names_add.py episodes/P001 [--dry-run]

Standing user decision (2026-10-15, after listening to H001): engine-default readings are accepted for new names
(status LISTENED_OK, mode as_is); a listener can later flag one, and a cited-IPA candidate is then researched
(see production/PRONUNCIATION_LEXICON.json conventions). Multi-word runs that only exist because two names sit
next to each other (e.g. "Hadar Ethiopia") are skipped when every part already resolves.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from sma import names  # noqa: E402

ep = sys.argv[1]
script = open(os.path.join(ep, "script.md"), encoding="utf-8").read()
entries = names.load_lexicon()
res = names.resolve(names.candidates(script), entries)
missing = [n for n, (st, _) in res.items() if st == "NOT_IN_LEXICON"]
# drop runs whose words each resolve on their own; add the single words otherwise
todo = []
for n in missing:
    parts = n.split()
    if len(parts) > 1 and all(names.resolve([p], entries)[p][0] != "NOT_IN_LEXICON" for p in parts):
        continue
    todo.append(n)
print("adding:", todo)
if "--dry-run" in sys.argv or not todo:
    sys.exit(0)
d = json.load(open(names.LEXICON, encoding="utf-8"))
for n in todo:
    d["entries"].append({"original": n, "lang": None, "region_or_variant": os.path.basename(ep), "IPA_if_verified": None,
                         "ipa_source": None, "vi_established_form": None, "vi_source": None,
                         "tts": {"vieneu-turbo": {"mode": "as_is", "value": None,
                                                  "derived_from": "engine default G2P; standing user decision 2026-10-15"}},
                         "reference_url": None, "status": "LISTENED_OK", "used_in": [os.path.basename(ep)],
                         "notes": "Cách engine tự đọc theo quyết định của người dùng; chưa nghe riêng tên này."})
json.dump(d, open(names.LEXICON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(names.LEXICON, "a").write("\n")
