#!/bin/bash
# One-shot: approve Telegram join requests + answer keyword comments, sync bot state. Prints ONE line.
cd "$(dirname "$0")/.."
git pull -q --rebase origin claude/trusting-cray-jkn30e 2>/dev/null
A=$([ -n "$TG_BOT_TOKEN" ] && [ -f reels/state/tg.json ] && python3 reels/tg_bot.py approve 2>&1 | tail -1 || echo "tg: skip")
B=$(python3 reels/ig_bot.py run 2>&1 | tail -1)
if [ -n "$(git status --porcelain reels/state)" ]; then
  git add reels/state && git commit -qm "bot state" && git pull -q --rebase origin claude/trusting-cray-jkn30e && git push -q origin claude/trusting-cray-jkn30e
fi
echo "$A | $B"
