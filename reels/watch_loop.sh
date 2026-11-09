#!/bin/bash
# Every 5 minutes: answer keyword comments + approve Telegram join requests, then sync bot state to git.
# Runs inside a live session (scheduled tasks can't fire more often than hourly). Usage: reels/watch_loop.sh <minutes_total>
cd "$(dirname "$0")/.."
END=$(( $(date +%s) + ${1:-115} * 60 ))
while [ "$(date +%s)" -lt "$END" ]; do
  reels/autoreply.sh
  sleep 300
done
