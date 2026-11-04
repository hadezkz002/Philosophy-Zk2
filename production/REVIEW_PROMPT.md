# Review prompt template (independent fact-check, philosophy check + listening review)

Copy, fill the `<…>` fields, and give it to a fresh general-purpose subagent. The reviewer may create exactly one
file and must not commit.

---
You are an independent reviewer for a Vietnamese educational philosophy audio episode (<topic>, audience L0–L1).
Repo: <path to Philosophy-Zk2 checkout>. Do NOT edit any file except creating episodes/<ID>/review_<version>.md.
Do not commit or push.

Read: episodes/<ID>/script.md (<version>), claims.csv (all PENDING), sources.md, brief.md, outline.md;
method rules in curriculum/PHILOSOPHY_SERIES_BIBLE.md and production/EPISODE_PLAYBOOK.md §0 and §9; the previous
episode's script for terms and continuity.

Verify against sources yourself (never invent quotes, never disable TLS):
- Cached texts: ~/.cache/sma-research/src/ (web_*.txt pages such as SEP/IEP/ctext/SuttaCentral, local_*.txt texts
  obtained via Google Drive, pm_<PMID>.txt PubMed abstracts). Search them with `python3 tools/research.py quote "<regex>"`.
  Live fetch is allowed with curl -sL or `tools/research.py web|pm` where the network allows it.

Tasks:
1. Check every tagged sentence against its cited source text: wording of quotations, standard locators (Stephanus,
   chapter.verse, sutta number), translator named, certainty (over/understatement), wrong source, details from another
   source inside an attributed sentence.
2. Flag untagged factual sentences.
3. Philosophy checks (bible, "Sản xuất"):
   (a) Is every quotation really in the primary text, at the stated location, in the named translation?
   (b) Has a scholar's interpretation slipped into the narrator's voice?
   (c) Is each criticised view first presented in its strongest form (steelman), and is there no false balance?
   (d) Does any sentence tell the listener what to believe or do (religion, politics, ethics, mental health)?
   (e) Is any quotation a misattribution or paraphrase presented as a quote?
4. Method: the three layers (text / interpretation / evaluation) kept apart; `ARGUMENT_RECONSTRUCTION` premises traceable
   to the text or labelled as the narrator's; uncertain dates of ancient thinkers stated as uncertain; thought experiments
   announced; neighbouring-episode topics only as teasers; safe-messaging rules for death, suffering and suicide.
5. Listening quality for L0: sentences > 30 words, ambiguity, jargon or Greek/Sanskrit/Pali/Hán Việt terms needing a gloss,
   translation traps, consistency with previous episodes.
6. Up to 3 high-value additions supported by the cached sources (quote them).

Write the review file in concise Vietnamese: verdict (APPROVE / APPROVE_WITH_REVISIONS / REJECT), per-claim table
(APPROVED/REJECTED + note), findings with severity (MAJOR/MINOR) and concrete replacement Vietnamese wording.
Final message: short summary (verdict + MAJOR findings).
---

Confirmation round (after fixes): ask the same agent to check only the changed sentences against sources, joins,
and sentence length, and to append "## Xác nhận <version>" to the same review file.
