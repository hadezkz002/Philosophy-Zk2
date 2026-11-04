#!/bin/bash
# Full production for one episode: plan -> render -> validate -> master (speech-only) -> [mix with theme] -> SHA256.
# Music mix only when metadata audio.music_mix is true (user decision 2026-10-16: no music from H005 on).
#   tools/run_episode.sh episodes/P001 [extra produce flags, e.g. --proof]
# Output dir, file names, title and comment come from <episode>/metadata.json (audio.filename, title, audio.comment).
# Resumable: rerun after any interruption; only missing/changed chunks render. Run inside a Termux tmux session.
set -e
EP=${1:?episode dir}; shift || true
cd "$(dirname "$0")/.."
export PYTHONPATH=src
eval "$(python3 - "$EP" <<'PY'
import json, os, shlex, sys
ep = sys.argv[1]; m = json.load(open(os.path.join(ep, "metadata.json"), encoding="utf-8"))
v = {"OUT": "/sdcard/Download/Science_Audio_VN/00_Science_Media_Academy/" + m["episode_id"],
     "VM": m["audio"]["filename"].replace("_speech-only.mp3", "_voice+music.mp3"),
     "TITLE": m["title"], "COMMENT": m["audio"].get("comment", ""),
     "MIX": "1" if m["audio"].get("music_mix") else ""}
print("\n".join(f"{k}={shlex.quote(x)}" for k, x in v.items()))
PY
)"
python3 -m sma.produce all "$EP" --engine vieneu-turbo-fp32 --out-dir "$OUT" "$@"
ID=$(basename "$EP")
[ -n "$MIX" ] && python3 -m sma.mix "$HOME/.cache/sma-build/$ID/vieneu-turbo-fp32/episode_raw.wav" "$HOME/.cache/sma-music/v1" "$OUT/$VM" \
  --bed-seconds 60 --title "$TITLE" --comment "$COMMENT (co nhac goc MUS-001..004)"
cd "$OUT" && sha256sum *.mp3 > SHA256SUMS.txt && cat SHA256SUMS.txt
