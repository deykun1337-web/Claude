#!/bin/bash
# Waits for the DB render, composes it, then renders + composes the intern video.
cd "$(dirname "$0")"
until [ "$(ls build/r_baza | wc -l)" -ge 1341 ] || ! pgrep -f "plan_baza" >/dev/null; do sleep 20; done
python3 compose.py ../klod_baza build/r_baza ../klod_baza/output/klod_baza_3d.mp4 > logs/compose_baza.log 2>&1
echo BAZA_DONE >> logs/chain.log
mkdir -p build/r_stazher; N=1424
for k in 0 1 2; do a=$((k*N/3)); b=$(((k+1)*N/3)); xvfb-run -a -s "-screen 0 1280x1280x24" blender -b -P scene3d.py -- build/plan_stazher.json build/r_stazher $a $b > logs/st_$k.log 2>&1 & done
wait
python3 compose.py ../klod_stazher build/r_stazher ../klod_stazher/output/klod_stazher_3d.mp4 > logs/compose_st.log 2>&1
echo STAZHER_DONE >> logs/chain.log
