# Episode playbook — "Hành Trình Nhân Loại" (and later series)

> **Philosophy-Zk2 note:** copied unchanged from Science Media Academy (commit `c79937b`), where it was written for the
> history series (H001–H019). The steps and gates apply here as written; for this repo read `episodes/PNNN` for
> `episodes/history/HNNN`, `research/PHILOSOPHY_SOURCE_REGISTER.md` (PS ids) for the history register (HS ids),
> `curriculum/PHILOSOPHY_SERIES_BIBLE.md` for the history bible, and `tools/research.py web|add` for `si` (Smithsonian).
> The one-day clock (`research.py clock`) belongs to the history series and is not used here.

How one episode goes from idea to a QA-passed MP3 on the phone, written from H001–H003. Follow it step by step;
every step names its tool and its gate. Living document: add each new lesson to §9 the day it is learned.

## 0. Quality bar (non-negotiable)
- Every factual sentence carries a claim tag; every claim cites a source **quote found in a cached copy** (`tools/research.py quote`).
- Uncertainty is stated as the source states it. Authors' interpretations are attributed ("theo các tác giả…").
- Hypotheses are labelled and **ranked by evidence type** (measurement > model > observation > proposal); no false balance.
- No invented IPA, quotes, behaviour or dialogue. Reconstructions are announced ("hãy hình dung…").
- No sentence over 30 words; jargon glossed at first use for L0 listeners.
- Nothing is published without the user. Episode PRs may be merged to main (user permission 2026-10-15) after a diff check for audio, models and secrets. Audio never goes into git.

## 1. Plan (≈ 10 min)
1. Read `curriculum/HUMAN_HISTORY_SERIES_BIBLE.md` (season list, method rules) and the previous episode's script (terms, clock, teaser it promised).
2. Branch `feat/hNNN-<slug>` from `main`.
3. Decide scope: what this episode owns vs. neighbouring episodes (teasers only for neighbours).

## 2. Research (tool: `tools/research.py`)
- `si <path>` for Smithsonian Human Origins pages (species pages, human-characteristics, evidence/behavior…).
- `pm-search "<author>[au] AND <keywords>"` — search by **first author + journal/year** or exact title; keyword-only searches are noisy.
- `pm <pmids>` caches abstracts; read them fully. Only abstracts are used; do not cite what an abstract does not say.
- Hunt deliberately for: the newest revision of a famous date (e.g. Schöningen spears 400→300→~200 ka),
  a published critique of each striking claim (e.g. Dikika cut marks vs. trampling), and a myth to correct
  (e.g. "100 billion neurons" → 86 billion).
- Target 25–35 sources: Smithsonian pages for the scaffold, 12–20 peer-reviewed abstracts for depth and debate.
- Add sources to `research/HISTORY_SOURCE_REGISTER.md` (series-wide HS IDs, continue numbering; 3-digit IDs are fine), write `claims.csv`, then
  `python3 tools/sources_build.py <ep> [--notes notes.md]` builds `<ep>/sources.md` from the IDs used and fills DOIs.

## 3. Write (target 5,000–6,500 words ≈ 21–27 min)
Structure that worked: Hook (a hands-on or surprising observation) → Context (recap of previous episode in 3
sentences) → Mental model → 4–6 Evidence sections in time order with **one-day-clock cues** (`research.py clock`)
→ "Why?" hypotheses ranked by evidence → Costs / debates → Limits → Thought experiment (announced) → Recap with
3 self-test questions (brief rubric) → Teaser of the next episode.
- Tag every factual sentence `[HNNN-Cxx]`; write `claims.csv` (12 columns, see H002) right after the draft.
- Run `python3 -m sma.claims <ep>` and the sentence-length check (§8) before review.

## 4. Names (tools: `python3 -m sma.names <ep>`, `tools/names_add.py <ep>`)
- Standing user decision: engine-default reading for new names (LISTENED_OK). `names_add.py` adds them.
- If the listener flags a name: research cited IPA, build a reel (`tools/name_reel.py`), let the listener choose.

## 5. Review (independent subagent; prompt template: `production/REVIEW_PROMPT.md`)
- Round 1 full review → apply every finding after **re-verifying the quote yourself** → round 2 confirmation of
  the changed sentences only. Expect 1–4 MAJOR per episode; typical ones are listed in §9.
- Set claim statuses from the reviewer's table; never self-approve without a confirmation round.

## 6. Render (Colab GPU first; local CPU fallback)
- **Default since 2026-10-16 (Colab Pro, user-approved for production):** `python3 -m sma.produce plan <ep> --engine vieneu-turbo-fp32`
  then `python3 tools/colab_render.py <ep>` (T4; same runner, voice, seed, watermark, phoneme overrides; PyTorch/CUDA
  backend). It downloads WAVs into the plan's chunk paths, records `<build>/colab_render.json`, and releases the runtime.
  Verified on H003 chunks: Tesla T4, 4 chunks in 54 s remote, 0.01 CU, ASR identical to local CPU renders.
  Then `tools/run_episode.sh <ep>` only validates/masters/mixes locally (light).
- Fallback (Colab BLOCKED/quota): local render as below.

### Local render (tool: `tools/run_episode.sh <ep>` inside a Termux tmux session)
- Pre-render with `python3 -m sma.produce render <ep> --engine vieneu-turbo-fp32 --allow-unapproved` while review runs;
  chunks are keyed by content hash, so only changed sentences re-render after the fixes.
- Final run: `tools/run_episode.sh <ep>` (production gates: all narrated claims APPROVED, all names LISTENED_OK).
- Metadata needs `audio.filename` (`SMA_HNNN_<Slug>_speech-only.mp3`), `audio.target_duration_s` ([1200,1650]), `title`, `audio.comment`.

## 7. QA (tools: produce QA, `tools/asr_report.py <ep>`)
- QA must be 9/9 PASS (duration target from metadata, -16 LUFS ±1.5, ≤ -1 dBTP, decode, silences, ID3).
- ASR median CER ≈ 2 % is normal; episodes dense in foreign names (H007: 2/3 of chunks) reach ≈ 5 % while Vietnamese-only chunks stay ≈ 0 % — check the split before worrying. For suspected word drops in Vietnamese-only chunks: re-render with another seed;
  identical ASR + normal rate ⇒ ASR bias (known: "tinh tinh"→"tinh", "mảnh"→"mạnh", "duỗi"→"rũi", "răng"→"xăng", "bán đảo Ả Rập"→"bán đảo" in ~half of chunks).
- Write `<ep>/qa_full.md`, update `metadata.json`, commit, push, comment on the series issue, then PR → merge (user allows).

## 8. Commands cheat-sheet
```bash
python3 tools/research.py clock 3.3 1.76 0.79          # one-day clock times
python3 -m sma.claims episodes/history/H003 --release   # release gate (use --partial for proofs)
python3 -c "import re;s=open('episodes/history/H003/script.md').read();t=re.sub(r'<!--.*?-->','',s,flags=re.S);t=re.sub(r'\[[^\]]*\]|^#.*$','',t,flags=re.M);print(len(t.split()),[len(x.split()) for x in re.split(r'(?<=[.?!])\s+',t) if len(x.split())>30])"
```

## 9. Lessons learned (append; newest last)
1. Clock times are easy to get wrong by hand → always compute with `research.py clock`.
2. "Mỗi giả thuyết đúng một phần" is false balance → rank hypotheses by evidence type.
3. Author claims slip into narrator voice ("loài này đã gắn bó…") → keep "theo các tác giả" around the whole idea.
4. A detail from source B inside a sentence attributed to source A misattributes it → split the sentence.
5. Translations: "vượn" ≠ great ape (gibbons are vượn); "ngón cái" heard as thumb → "ngón chân cái"; "fittest" ≠ "mạnh nhất".
6. Ages: "fossils are X years old" ≠ "species lived X years ago" when the source gives no range.
7. Smithsonian pages lag the literature (Sahelanthropus "no post-cranial fossils"; Schöningen 400 ka) → search for revisions.
8. Engine: VieNeu lowercases and spells acronyms before phonemizing → phoneme overrides must use placeholders (done in runner).
9. Pipeline: chunk files keyed by content hash; validator counts foreign-word syllables by vowel groups; duration QA reads metadata.
10. Device: Android kills Termux; long jobs in a separate tmux session; `tmux kill-session` leaves the proot runner alive
    (kill by PID from `ps -eo pid,etimes,args`); never `pkill -f` a pattern that matches your own shell.
11. Meaning-critical short words ("ít", "không", "chưa") can be swallowed or misheard; if ASR misses one at two seeds, **reword** so the meaning does not hinge on it (H003 C42: "ít mỡ hơn" → "não càng lớn thì mỡ dự trữ càng nhỏ").
12. Render throughput on this phone: ~14 s/chunk at full clocks, ~30 s when thermally capped, 75–100 s at the 1 GHz battery-saver cap → ask the user to charge / disable battery saver before long renders.
13. Colab render (H004): the GPU is not the bottleneck (233 chunks ≈ 5 min on T4); the download is. `colab_render.py`
    ships lossless FLAC (≈ half of WAV). Run it as **one job** (no batching). The two lost renders on 2026-10-16 were
    caused by the user's internet outage, not by the method; if a render is lost, just rerun (present chunks are skipped).
    Launch long jobs in the *Termux* tmux server via `proot-distro login ubuntu -- bash <script>`.
14. **No music from H005 on** (user decision 2026-10-16). Deliver speech-only MP3 only; `run_episode.sh` mixes the
    theme only when `metadata.audio.music_mix` is true (set for H004 only, which was already planned with music).
15. **No duration cap from H005 on** (user decision 2026-10-16: "bỏ giới hạn về thời lượng, càng nhiều kiến thức càng tốt,
    ưu tiên hiểu biết"). Set `audio.target_duration_s` to `[1200, 7200]` (the QA check still needs a range). Length is
    driven by content: explain each idea until an L0 listener understands *why*, not just *what*. The quality gates
    (sources, claims, review, ≤30-word sentences) are unchanged.
16. Workflow that worked for H005–H006 (≈ 2–3 h per episode): research 20–25 abstracts → register rows → script with tags →
    claims.csv → `sources_build.py` → `names_add.py` → launch the review subagent **and** the Colab pre-render in parallel
    → apply findings → confirmation round → re-render only changed chunks (hash-keyed) + master + QA + ASR in one tmux
    script → reword any ASR-suspect sentence (lists of 4+ items and sentences ending in a short clause are the usual
    victims) → commit/PR/merge.
17. (H013–H018) Pipeline per episode, unchanged since H012: research (20–30 abstracts) → register HS rows → claims.csv with quoted
    `supporting_location` → script → `sma.claims` + quote check + `names_add.py` → **review subagent and Colab pre-render in parallel** → apply
    review (re-verify every quote yourself) → **confirmation subagent** → `sma.claims --release` → re-render only changed chunks →
    `run_episode.sh` → `asr_report.py` → `qa_full.md` → commit → PR → merge. Every review found 5–8 MAJOR; never skip the confirmation round.
18. Reviewer findings that recur: "may/likely" stated as fact; an author's inference in the narrator's voice (use "theo các tác giả");
    false balance between two views (rank by evidence type; say when one side rests on one site); mixing BCE and "năm trước" in one sentence
    (convert both); a claim tag on a sentence whose detail comes from another source; a narrator's joined inference between two studies
    (label it "suy luận của người kể").
19. ASR drops short words. Reword sentences whose meaning hangs on "không/chưa/ít/chẳng/khác" with positive phrasing ("vắng mặt", "thiếu",
    "gần giống"); split lists of 4+ items into two sentences; split every sentence >30 words (`re.split` check in §8).
20. New source IDs: take the next free HS number from the register; a reviewer's proposed IDs may collide with another episode's → renumber and
    say so in the script's HTML comment. Take titles/authors from the cached abstract, never from memory.
21. `research.py clock` is the 7-Myr scale; for the series' 300 ka clock compute by hand: hour = 24 × (1 − ka/300). Say "khoảng" for BCE→BP.
22. Before a PR: `git diff --name-only origin/main...HEAD` must show no mp3/wav/onnx/pt/bin or secrets; audio goes only to Android Downloads.
    The user pre-approved auto-merge of episode PRs after QA 9/9 (2026-10-18). If `gh` says "Bad credentials", the user must run `gh auth login`.
23. Topic safety: the model's safety classifier stopped drafting H015 (zoonoses) three times. For pathogen/biology-adjacent topics ask the user to
    choose another model or re-scope before writing; do not retry on the same model.
24. (2026-11-04, cloud session) No `colabjob` in a cloud container → Drive route: `tools/colab_render.py <ep> --bundle <dir>`, upload the 3 files to
    `MyDrive/Science_Media_Academy/colab_jobs/<job>/`, run `tools/colab/SMA_Drive_Render.ipynb` (T4), then `--ingest <sma_out.tar>`. Same REMOTE script.
    The cloud network may deny source sites (PubMed, SEP…): allow them in the environment settings, cache on the phone, or pass texts through Drive
    (`tools/research.py add`). The philosophy series uses the same playbook with its own bible (`curriculum/PHILOSOPHY_SERIES_BIBLE.md`).
