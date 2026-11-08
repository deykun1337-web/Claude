#!/bin/bash
cd "$(dirname "$0")"
sleep 20
while pgrep -f "clay3d.py" >/dev/null; do sleep 20; done
python3 compose_clay.py ../redkost build/r_clay build/plan_clay.json ../redkost/output/redkost.mp4 > logs/compose_clay.log 2>&1
echo clay_DONE >> logs/chain.log
