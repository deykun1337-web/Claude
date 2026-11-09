#!/bin/bash
cd "$(dirname "$0")"
sleep 20
while pgrep -f "zak3d.py" >/dev/null; do sleep 20; done
python3 compose_zak.py ../zakryv build/r_zak build/plan_zak.json ../zakryv/output/zakryv.mp4 > logs/compose_zak.log 2>&1
echo zak_DONE >> logs/chain.log
