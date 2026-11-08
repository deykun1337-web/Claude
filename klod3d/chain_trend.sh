#!/bin/bash
cd "$(dirname "$0")"
while pgrep -f "chain_fix.sh|michael3d.py|compose_michael.py" >/dev/null; do sleep 20; done
xvfb-run -a -s "-screen 0 1280x1280x24" blender -b -P trend3d.py -- build/plan_tplate.json build/tplate 0 1 > logs/tplate.log 2>&1
for V in telefon musya; do
  mkdir -p build/r_$V; N=$(python3 -c "import json; print(len(json.load(open('build/plan_$V.json'))['frames']))")
  for k in 0 1 2; do a=$((k*N/3)); b=$(((k+1)*N/3)); xvfb-run -a -s "-screen 0 1280x1280x24" blender -b -P trend3d.py -- build/plan_$V.json build/r_$V $a $b > logs/${V}_$k.log 2>&1 & done
  wait
  python3 compose_trend.py ../$V build/r_$V build/plan_$V.json build/tplate/00000.png ../$V/output/$V.mp4 > logs/compose_$V.log 2>&1
  echo ${V}_DONE >> logs/chain.log
done
