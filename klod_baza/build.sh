#!/bin/bash
# Full rebuild: two-voice dialogue -> trim -> soundtrack -> 60fps frames -> 30fps mp4
set -e
cd "$(dirname "$0")"
SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 voice.py
python3 tighten.py
python3 audio.py
python3 render.py
mkdir -p output
ffmpeg -v error -y -framerate 60 -i build/frames/%05d.png -i build/mix.wav \
  -vf "tmix=frames=2:weights='1 1',fps=30,noise=alls=2:allf=t,format=yuv420p" \
  -c:v libx264 -preset slow -crf 20 -maxrate 8M -bufsize 16M \
  -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 -c:a aac -b:a 192k -ac 2 -shortest -movflags +faststart output/klod_baza.mp4
