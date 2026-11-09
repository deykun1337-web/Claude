#!/bin/bash
cd "$(dirname "$0")"
while pgrep -f "kak3d.py|compose_kak" >/dev/null; do sleep 20; done
for r in "0 258" "258 516" "516 774"; do set -- $r; xvfb-run -a -s "-screen 0 1280x1280x24" blender -b -P dolg3d.py -- build/plan_dolg.json build/r_dolg $1 $2 > logs/dolg_$1.log 2>&1 & done
wait
python3 compose_dolg.py ../dolg build/r_dolg build/plan_dolg.json ../dolg/output/dolg.mp4 > logs/compose_dolg.log 2>&1
echo dolg_DONE >> logs/chain.log
