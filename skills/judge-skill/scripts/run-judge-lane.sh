#!/usr/bin/env bash
# Round 0: run the judge-and-fix brief on each repo in turn with the Codex CLI.
# Usage: PROJECTS=~/code JUDGING=~/judging scripts/run-judge-lane.sh repo:port[,port] ...
set -u
HERE="$(cd "$(dirname "$0")/.." && pwd)"
PROJECTS="${PROJECTS:?set PROJECTS to the folder holding the repos}"
JUDGING="${JUDGING:?set JUDGING to a folder for the judging notes}"
MODEL="${CODEX_MODEL:-gpt-6-sol}"
mkdir -p "$JUDGING"
for item in "$@"; do
  repo="${item%%:*}"; ports="${item#*:}"
  brief="$JUDGING/judge-$repo.brief.md"
  { sed "s|<JUDGING_DIR>|$JUDGING|g" "$HERE/briefs/round0-judge-fix.md"; echo; echo "## This run"
    echo "Repo folder: $repo. Your local chain/dev port(s): $ports."; } > "$brief"
  echo "$(date -u +%H:%M) start $repo"
  codex exec -m "$MODEL" -C "$PROJECTS/$repo" -s workspace-write \
    -c sandbox_workspace_write.network_access=true --add-dir "$JUDGING" --skip-git-repo-check \
    -o "$JUDGING/judge-$repo.result.md" - < "$brief" > "$JUDGING/judge-$repo.log" 2>&1
  echo "$(date -u +%H:%M) done $repo exit $?"
done
