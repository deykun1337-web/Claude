#!/bin/bash
# Prints "IG_OK" if the Instagram Graph API answers, else "IG_BLOCKED: <reason>" (exit 1). Cheap pre-check for every run.
R=$(curl -sS --max-time 30 "https://graph.facebook.com/v24.0/17841409120122863?fields=id" 2>&1)
if echo "$R" | grep -q '"id"'; then echo IG_OK; else echo "IG_BLOCKED: $(echo "$R" | head -c 160)"; exit 1; fi
