#!/usr/bin/env bash
# Round 1: generate a product's brand art with the Codex CLI's built-in image tool (needs a ChatGPT plan).
# Usage: scripts/assets-codex.sh <out-dir> "<shared style line>" "file.png|subject" ...
set -u
out="$1"; style="$2"; shift 2
mkdir -p "$out"
list=""
for item in "$@"; do f="${item%%|*}"; s="${item#*|}"; [ -f "$out/$f" ] || list="$list
- $f: $s"; done
[ -z "$list" ] && { echo "nothing to make"; exit 0; }
codex exec -m "${CODEX_MODEL:-gpt-6-sol}" -C "$out" -s workspace-write --skip-git-repo-check \
"Use your built-in image generation tool to create each image below and save it in the current directory with exactly that filename. Shared style: $style Rules: original artwork, no text or letters, no logos, no real brands, no real people. Files marked 'transparent' need a real alpha channel, not a painted checkerboard. Images:$list
After saving, append each filename and the exact prompt to prompts.md and print each file's pixel size." > "$out/codex.log" 2>&1
ls -la "$out"
