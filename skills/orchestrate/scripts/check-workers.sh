#!/usr/bin/env bash
# Usage: check-workers.sh <repo>...   (the five-minute check)
# For each repo: changed files, newest commit and its age, and the tail of the newest Codex log for it.
work=${ORCH_WORK:-$PWD}
for r in "$@"; do
  n=$(git -C "$r" status --short 2>/dev/null | wc -l | tr -d ' ')
  c=$(git -C "$r" log -1 --format='%h %cr %s' 2>/dev/null | cut -c1-90)
  echo "== $(basename "$r"): $n changed file(s); last commit: $c"
  l=$(ls -t "$work"/codex/logs/"$(basename "$r")"-*.log 2>/dev/null | head -1)
  [ -n "$l" ] && tail -n 3 "$l" | cut -c1-160 | sed 's/^/   /'
done
echo "codex workers running: $(pgrep -f 'codex exec' | wc -l | tr -d ' ')"
echo "free memory: $(memory_pressure 2>/dev/null | awk '/free percentage/{print $5}')"
