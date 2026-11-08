#!/bin/bash
cd "$(dirname "$0")"
while pgrep -f "agents3d.py|compose_agents.py" >/dev/null; do sleep 20; done
mkdir -p build/r_michael; N=$(python3 -c "import json; print(len(json.load(open('build/plan_michael.json'))['frames']))")
for k in 0 1 2; do a=$((k*N/3)); b=$(((k+1)*N/3)); xvfb-run -a -s "-screen 0 1280x1280x24" blender -b -P michael3d.py -- build/plan_michael.json build/r_michael $a $b > logs/mi_$k.log 2>&1 & done
wait
python3 compose_michael.py ../ruslan build/r_michael build/plan_michael.json build/extra/00000.png build/extra/00001.png ../ruslan/output/maikl_3d.mp4 > logs/compose_michael.log 2>&1
echo MICHAEL_DONE >> logs/chain.log
