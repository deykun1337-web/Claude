#!/bin/bash
# Every 5 minutes: answer keyword comments + approve Telegram join requests, then sync bot state to git.
# Runs inside a live session (scheduled tasks can't fire more often than hourly). Usage: reels/watch_loop.sh <minutes_total>
cd "$(dirname "$0")/.."
END=$(( $(date +%s) + ${1:-115} * 60 ))
while [ "$(date +%s)" -lt "$END" ]; do
  git pull -q --rebase origin claude/trusting-cray-jkn30e 2>/dev/null
  [ -n "$TG_BOT_TOKEN" ] && python3 reels/tg_bot.py approve 2>&1 | tail -1
  python3 reels/ig_bot.py run 2>&1 | tail -2
  if [ -n "$(git status --porcelain reels/state)" ]; then
    git add reels/state && git commit -qm "bot state" && git pull -q --rebase origin claude/trusting-cray-jkn30e && git push -q origin claude/trusting-cray-jkn30e
  fi
  echo "$(date +%H:%M) tick"
  sleep 300
done
