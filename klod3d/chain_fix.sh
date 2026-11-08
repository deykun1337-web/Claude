#!/bin/bash
cd "$(dirname "$0")"
sleep 30
while pgrep -f "chain_vozduhan.sh|michael3d.py|compose_vozduhan.py" >/dev/null; do sleep 20; done
A=314; B=1126; N=$((B-A))
for k in 0 1 2; do a=$((A+k*N/3)); b=$((A+(k+1)*N/3)); xvfb-run -a -s "-screen 0 1280x1280x24" blender -b -P michael3d.py -- build/plan_michael.json build/r_michael $a $b > logs/fix_$k.log 2>&1 & done
wait
rm -rf build/r_michael_c
python3 compose_michael.py ../ruslan build/r_michael build/plan_michael.json build/extra/00000.png build/extra/00001.png ../ruslan/output/maikl_3d.mp4 > logs/compose_michael2.log 2>&1
echo MICHAEL_FIX_DONE >> logs/chain.log
