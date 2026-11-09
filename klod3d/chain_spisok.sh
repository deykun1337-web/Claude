#!/bin/bash
cd "$(dirname "$0")"
until grep -q dolg_DONE logs/chain.log 2>/dev/null; do sleep 30; done
for r in "0 304" "304 608" "608 910"; do set -- $r; xvfb-run -a -s "-screen 0 1280x1280x24" blender -b -P spisok3d.py -- build/plan_spisok.json build/r_spisok $1 $2 > logs/spisok_$1.log 2>&1 & done
wait
python3 compose_spisok.py ../spisok build/r_spisok build/plan_spisok.json ../spisok/output/spisok.mp4 > logs/compose_spisok.log 2>&1
echo spisok_DONE >> logs/chain.log
