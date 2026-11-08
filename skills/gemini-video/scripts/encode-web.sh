#!/usr/bin/env bash
# Usage: encode-web.sh <in.mp4> <out-basename>
# Makes a muted, looping-friendly web hero: H.264 MP4 + WebM + a poster frame. Keeps the full frame (and the
# Gemini sparkle mark): never crop the watermark out.
set -euo pipefail
in=$1 out=$2
ffmpeg -y -loglevel error -i "$in" -an -c:v libx264 -preset slow -crf 24 -pix_fmt yuv420p -movflags +faststart "$out.mp4"
ffmpeg -y -loglevel error -i "$in" -an -c:v libvpx-vp9 -b:v 0 -crf 34 "$out.webm"
ffmpeg -y -loglevel error -ss 1 -i "$in" -frames:v 1 -q:v 3 "$out-poster.jpg"
ls -la "$out".mp4 "$out".webm "$out"-poster.jpg
