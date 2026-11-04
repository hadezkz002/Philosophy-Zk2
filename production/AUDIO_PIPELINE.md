# Audio-first production architecture (Termux/Ubuntu)

## Principle
Generate an **original, reviewable episode package** first; render to local audio only after the text is approved. Keep project code/state in Ubuntu home and deliver final MP3 to the **verified** Android Download mount.

## Stages
1. Select concept from prerequisite map; record skill level, claims and target minutes.
2. Gather bibliography; export evidence ledger with source URLs and scientific type labels.
3. Draft full Vietnamese narration + separate structured visual notes for future video.
4. Independent editorial QA; fail closed on unsupported claims; version the approved script.
5. Pronunciation pass: proper nouns, abbreviations, numbers, units, chemical symbols, e.g. eV/MeV, m/s² and English names.
6. 30–60s TTS bake-off. Candidate engines: sherpa-onnx/Piper Vietnamese VITS, VieNeu-TTS Nano; verify actual ARM64 compatibility, model licenses, memory, heat and speed; do **not** assume fit.
7. Chunk script on paragraphs or sentence boundaries, preserve original text and sequence indexes; local synthesis to lossless intermediate WAV; record model version, seed, parameters.
8. Validate chunks against expected lengths, silences and potential missing words; ASR comparison optional as secondary check, never absolute authority.
9. Master with FFmpeg (conservative loudness normalization, clipping prevention, no aggressive music); export 64–96 kb/s mono MP3 speech unless listening tests show lower quality.
10. Validate ffprobe duration, decode integrity, peak/clipping, file size, checksum, filename and M3U8 relative paths. Human listening sample.
11. Export metadata JSON, accessible TXT/Markdown transcript, attribution, errata and six-category index.

## Paths
```
~/projects/science-media-academy/      # code/config; verify path
  scripts/
  evidence/
  episodes/<episode_id>/brief.md
  episodes/<episode_id>/claims.csv
  episodes/<episode_id>/script.md
  episodes/<episode_id>/pronunciation.json
  episodes/<episode_id>/qc.json
  cache/                         # gitignored, temp audio/model assets
Android/Download/Science_Audio_VN/
  01_Vat_Ly_Vu_Tru/
  02_Hoa_Hoc/
  03_Sinh_Hoc_Y_Hoc/
  04_AI_Cong_Nghe/
  05_Toan_Hoc_Tu_Duy/
  06_Lich_Su_Triet_Hoc/
  Playlists/
  Metadata/
```

Check `~/storage/downloads` in Termux, `/sdcard/Download` or actual bind in Ubuntu/proot; **never guess** availability. Work must survive interrupted sessions with atomic writes and idempotent resume. No mass dependency installs on first audit.

## Technical gates
- Free/local-first TTS. No paid APIs without explicit authorization.
- Bounded retries, process/resource limits, temperature and storage monitoring.
- No concurrent synthesis without benchmark proof; Android thermal behavior is unknown until measured.
- Do not collect/upload voiceprints or synthesize cloned real voice without explicit rights and consent.
- Final delivery not equal publication; publishing is a separately approved step.
- Do not include licensed source media, model weights, large WAV/MP3 or tokens in Git.

## MVP milestones
M0: environment audit; M1: two TTS models or one practical fallback benchmarked on 60s sample; M2: fully sourced 8–12m script; M3: generated pilot MP3 with QC evidence; M4: integrate a single canonical package; M5: expand in batches of 5 only after review.
