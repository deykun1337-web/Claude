#!/bin/bash
cd "$(dirname "$0")"
sleep 20
while pgrep -f "kak3d.py" >/dev/null; do sleep 20; done
python3 compose_kak.py ../kakdelayu build/r_kak build/plan_kak.json ../kakdelayu/output/kakdelayu.mp4 > logs/compose_kak.log 2>&1
echo kak_DONE >> logs/chain.log
