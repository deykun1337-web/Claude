#!/bin/bash
cd "$(dirname "$0")"
until [ -f ../dima/build/voice.json ]; do sleep 15; done
(cd ../dima && python3 tighten.py && python3 -c "import json; json.dump([0]*100,open('build/mouth.json','w'))" && python3 audio.py) > logs/dima_prep.log 2>&1
python3 plan_dima.py ../dima build/plan_dima.json >> logs/dima_prep.log 2>&1
sleep 30
while pgrep -f "chain_trend.sh|chain_new.sh|trend3d.py|city3d.py|compose_trend.py" >/dev/null; do sleep 20; done
mkdir -p build/r_dima; N=$(python3 -c "import json; print(len(json.load(open('build/plan_dima.json'))['frames']))")
for k in 0 1 2; do a=$((k*N/3)); b=$(((k+1)*N/3)); xvfb-run -a -s "-screen 0 1280x1280x24" blender -b -P michael3d.py -- build/plan_dima.json build/r_dima $a $b > logs/dima_$k.log 2>&1 & done
wait
python3 compose_dima.py ../dima build/r_dima build/plan_dima.json ../dima/output/dima.mp4 > logs/compose_dima.log 2>&1
echo dima_DONE >> logs/chain.log
