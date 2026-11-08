#!/bin/bash
cd "$(dirname "$0")"
sleep 20
while pgrep -f "pyatnica3d.py" >/dev/null; do sleep 20; done
python3 compose_pyatnica.py ../pyatnica build/r_pyatnica build/plan_pyatnica.json ../pyatnica/output/pyatnica.mp4 > logs/compose_pyatnica.log 2>&1
echo pyatnica_DONE >> logs/chain.log
