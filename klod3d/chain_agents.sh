#!/bin/bash
cd "$(dirname "$0")"
while pgrep -f "agents3d.py" >/dev/null; do sleep 20; done
python3 compose_agents.py ../agenty build/r_agents build/plan_agents.json ../agenty/output/agenty.mp4 > logs/compose_agents.log 2>&1
echo AGENTS_DONE >> logs/chain.log
