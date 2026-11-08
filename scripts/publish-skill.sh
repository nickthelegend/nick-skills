#!/usr/bin/env bash
# Publish one skill folder from this repo to its own standalone repo, keeping that folder's history.
# The skill is edited here, in skills/<name>/. This script only pushes it out.
#   scripts/publish-skill.sh dribbble-frontend https://github.com/nickthelegend/dribbble-frontend.git
#
# How it lands:
# - The skill's split history always goes to the standalone repo's `skill` branch (a fast-forward).
# - `main` is fast-forwarded to it when it can be.
# - If `main` has its own commits (e.g. a private library/ folder), GitHub merges `skill` into `main` on the
#   server (gh api .../merges), so this repo never downloads those files.
# - Never force-pushes.
set -euo pipefail
name="${1:?usage: publish-skill.sh <skill-name> <remote-url>}"
remote="${2:?usage: publish-skill.sh <skill-name> <remote-url>}"
cd "$(git rev-parse --show-toplevel)"
[ -d "skills/$name" ] || { echo "no skills/$name" >&2; exit 1; }
git diff --quiet HEAD -- "skills/$name" || { echo "skills/$name has uncommitted changes; commit first" >&2; exit 1; }
sha=$(git subtree split --prefix="skills/$name" 2>/dev/null)
echo "skills/$name -> $sha"

remote_main=$(git ls-remote "$remote" refs/heads/main | cut -f1)
remote_skill=$(git ls-remote "$remote" refs/heads/skill | cut -f1)
[ "$remote_skill" = "$sha" ] || git push -q "$remote" "$sha:refs/heads/skill"
[ "$remote_main" = "$sha" ] && { echo "already up to date"; exit 0; }

if git push -q "$remote" "$sha:refs/heads/main" 2>/dev/null; then
  echo "main fast-forwarded to $sha"
else
  slug=$(echo "$remote" | sed -E 's#(git@github.com:|https://github.com/)##; s#\.git$##')
  out=$(gh api "repos/$slug/merges" -f base=main -f head=skill -f commit_message="Merge skill: skills/$name at $sha from nick-skills" --jq '.sha' 2>&1) || {
    echo "merge failed: $out" >&2; exit 1; }
  [ -n "$out" ] && echo "merged skill into main: $out" || echo "already up to date (main already contains $sha)"
fi
