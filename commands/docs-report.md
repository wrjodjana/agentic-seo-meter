---
description: Report documentation fetches and estimated token cost for this session
argument-hint: "[--all]"
disable-model-invocation: true
allowed-tools: Bash(bash "${CLAUDE_PLUGIN_ROOT}/scripts/python.sh" *)
---

!`bash "${CLAUDE_PLUGIN_ROOT}/scripts/python.sh" "${CLAUDE_PLUGIN_ROOT}/scripts/report.py" --data "${CLAUDE_PLUGIN_DATA}" --session "${CLAUDE_SESSION_ID}" $ARGUMENTS`

Show the report above to the user exactly as written. Do not fetch anything or run other tools.
