#!/bin/bash
cd "$(dirname "$0")"
sleep 60
while pgrep -f "chain_michael.sh|michael3d.py|compose_michael.py|agents3d.py|compose_agents.py" >/dev/null; do sleep 20; done
mkdir -p build/r_vozduhan; N=$(python3 -c "import json; print(len(json.load(open('build/plan_vozduhan.json'))['frames']))")
for k in 0 1 2; do a=$((k*N/3)); b=$(((k+1)*N/3)); xvfb-run -a -s "-screen 0 1280x1280x24" blender -b -P michael3d.py -- build/plan_vozduhan.json build/r_vozduhan $a $b > logs/vo_$k.log 2>&1 & done
wait
python3 compose_vozduhan.py ../vozduhan build/r_vozduhan build/plan_vozduhan.json build/extra/00000.png ../vozduhan/output/vozduhan_3d.mp4 > logs/compose_vozduhan.log 2>&1
echo VOZDUHAN_DONE >> logs/chain.log
