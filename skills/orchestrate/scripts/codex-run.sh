#!/usr/bin/env bash
# Usage: codex-run.sh <repo> <brief.md> [model]
# Runs a Codex worker in the background on <repo> with <brief.md>. Logs to $ORCH_WORK/codex/logs/.
# Set CODEX_SANDBOX=workspace-write to stop the worker committing (then you review and commit).
set -euo pipefail
repo=$(cd "$1" && pwd); brief=$2; model=${3:-${CODEX_MODEL:-gpt-6-sol}}
work=${ORCH_WORK:-$PWD}; mkdir -p "$work/codex/logs"
name=$(basename "$repo")-$(basename "$brief" .md)-$(date +%H%M)
log="$work/codex/logs/$name.log"; out="$work/codex/logs/$name.result.md"
sandbox=${CODEX_SANDBOX:-danger-full-access}
args=(exec -m "$model" --skip-git-repo-check -s "$sandbox" -c 'approval_policy="never"' -C "$repo" -o "$out")
[ "$sandbox" = workspace-write ] && args+=(-c sandbox_workspace_write.network_access=true)
nohup codex "${args[@]}" - < "$brief" > "$log" 2>&1 &
echo "worker $name pid $! log $log result $out"
