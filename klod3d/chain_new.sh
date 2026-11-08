#!/bin/bash
cd "$(dirname "$0")"
sleep 30
while pgrep -f "chain_trend.sh|trend3d.py|compose_trend.py" >/dev/null; do sleep 20; done
for V in obidelsya:trend3d.py vmoskve:city3d.py; do
  N_=${V%%:*}; SCR=${V##*:}
  mkdir -p build/r_$N_; N=$(python3 -c "import json; print(len(json.load(open('build/plan_$N_.json'))['frames']))")
  for k in 0 1 2; do a=$((k*N/3)); b=$(((k+1)*N/3)); xvfb-run -a -s "-screen 0 1280x1280x24" blender -b -P $SCR -- build/plan_$N_.json build/r_$N_ $a $b > logs/${N_}_$k.log 2>&1 & done
  wait
  python3 compose_trend.py ../$N_ build/r_$N_ build/plan_$N_.json build/tplate/00000.png ../$N_/output/$N_.mp4 > logs/compose_$N_.log 2>&1
  echo ${N_}_DONE >> logs/chain.log
done
