#!/usr/bin/env bash
# Usage: fit.sh <kind> <in.png> <out-basename>   kind = logo | hero | object | icon
# Writes web-sized copies next to <out-basename>. macOS sips; cwebp if installed.
set -euo pipefail
kind=$1 in=$2 out=$3
case "$kind" in
  logo)   sips -Z 512 "$in" --out "$out-512.png" >/dev/null; sips -Z 64 "$in" --out "$out-64.png" >/dev/null ;;
  hero)   sips -Z 1600 "$in" --out "$out.png" >/dev/null ;;
  object) sips -Z 800 "$in" --out "$out.png" >/dev/null ;;
  icon)   sips -Z 256 "$in" --out "$out.png" >/dev/null ;;
  *) echo "unknown kind $kind" >&2; exit 2 ;;
esac
if command -v cwebp >/dev/null; then
  for f in "$out"*.png; do cwebp -quiet -q 82 "$f" -o "${f%.png}.webp"; done
fi
ls -la "$out"*
