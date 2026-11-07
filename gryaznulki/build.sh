#!/bin/bash
# Full rebuild: voice -> pause trim -> soundtrack -> frames -> mp4
set -e
cd "$(dirname "$0")"
SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 voice.py
python3 tighten.py
python3 audio.py
python3 render.py
mkdir -p output
ffmpeg -v error -y -framerate 30 -i build/frames/%04d.png -i build/mix.wav -c:v libx264 -preset slow -crf 18 \
  -pix_fmt yuv420p -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 -c:a aac -b:a 192k -ac 2 -shortest -movflags +faststart output/gryaznulki.mp4
echo "ready: output/gryaznulki.mp4"
