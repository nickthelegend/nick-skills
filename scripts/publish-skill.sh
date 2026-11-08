#!/usr/bin/env bash
# Publish one skill folder from this repo to its own standalone repo, keeping that folder's history.
# The skill stays edited here, in skills/<name>/. This script only pushes it out, as a fast-forward.
#   scripts/publish-skill.sh dribbble-frontend git@github.com:nickthelegend/dribbble-frontend.git
set -euo pipefail
name="${1:?usage: publish-skill.sh <skill-name> <remote-url>}"
remote="${2:?usage: publish-skill.sh <skill-name> <remote-url>}"
cd "$(git rev-parse --show-toplevel)"
[ -d "skills/$name" ] || { echo "no skills/$name" >&2; exit 1; }
git diff --quiet HEAD -- "skills/$name" || { echo "skills/$name has uncommitted changes; commit first" >&2; exit 1; }
sha=$(git subtree split --prefix="skills/$name")
echo "skills/$name -> $sha"
git push "$remote" "$sha:refs/heads/main"   # no --force: a non-fast-forward is refused
