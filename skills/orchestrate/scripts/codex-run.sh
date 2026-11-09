#!/usr/bin/env bash
# Usage: [ORCH_TASK=<task id>] codex-run.sh <repo> <brief.md> [model]
#
# Runs one Codex worker on <repo> with <brief.md> and BLOCKS until it exits.
# Call it from Claude Code with Bash `run_in_background: true`: the harness then wakes the session
# when the worker ends, so the orchestrator reviews the result instead of idling forever.
# (The old detached `nohup ... &` mode is why runs "did nothing": nobody was woken. Use --detach only
# from a plain terminal.)
#
# ORCH_TASK=<id> marks that orch.py task as waiting on this worker's pid; when the worker exits the
# Stop guard makes the session review it.
# CODEX_SANDBOX=workspace-write stops the worker committing (you review and commit). Default:
# danger-full-access. CODEX_MODEL overrides the model (default gpt-6-sol).
set -euo pipefail
detach=0; [ "${1:-}" = --detach ] && { detach=1; shift; }
[ $# -ge 2 ] || { echo "usage: codex-run.sh [--detach] <repo> <brief.md> [model]" >&2; exit 64; }
repo=$(cd "$1" && pwd); brief=$(cd "$(dirname "$2")" && pwd)/$(basename "$2")
model=${3:-${CODEX_MODEL:-gpt-6-sol}}
[ -f "$brief" ] || { echo "codex-run: brief not found: $brief" >&2; exit 66; }
command -v codex >/dev/null || { echo "codex-run: Setup required: install the Codex CLI (brew install codex) and sign in" >&2; exit 69; }
work=${ORCH_WORK:-$PWD}; mkdir -p "$work/codex/logs"
name=$(basename "$repo")-$(basename "$brief" .md)-$(date +%H%M%S)
log="$work/codex/logs/$name.log"; out="$work/codex/logs/$name.result.md"
sandbox=${CODEX_SANDBOX:-danger-full-access}
args=(exec -m "$model" --skip-git-repo-check -s "$sandbox" -c 'approval_policy="never"' -C "$repo" -o "$out")
[ "$sandbox" = workspace-write ] && args+=(-c sandbox_workspace_write.network_access=true)
orch="$(cd "$(dirname "$0")" && pwd)/orch.py"
echo "worker $name log $log result $out"
if [ "$detach" = 1 ]; then
  nohup codex "${args[@]}" - < "$brief" > "$log" 2>&1 &
  pid=$!
  [ -n "${ORCH_TASK:-}" ] && python3 "$orch" worker "$ORCH_TASK" --pid "$pid" --log "$log" || true
  echo "detached pid $pid"; exit 0
fi
[ -n "${ORCH_TASK:-}" ] && python3 "$orch" worker "$ORCH_TASK" --pid "$$" --log "$log" || true
set +e
codex "${args[@]}" - < "$brief" > "$log" 2>&1
rc=$?
set -e
echo "worker $name exited $rc"
echo "--- result ($out) ---"; [ -f "$out" ] && tail -n 40 "$out" || tail -n 20 "$log"
echo "--- changes ---"; git -C "$repo" status --short | head -40; git -C "$repo" log --oneline -5
exit $rc
