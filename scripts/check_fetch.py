import json
import os
import sys

from store import log_path
from urls import absorb, recalled

WARNING = (
    "agentic-seo-meter: {url} does not appear in any search result or page fetched "
    "earlier this session, so the path looks recalled rather than verified. If it "
    "404s or returns the wrong page, search for the real URL instead of typing "
    "another guess."
)


def seen_urls(path, session):
    seen = set()
    if not session or not os.path.exists(path):
        return seen
    with open(path, "rb") as f:
        for line in f:
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if isinstance(record, dict) and record.get("session_id") == session:
                absorb(record, seen)
    return seen


try:
    payload = json.loads(sys.stdin.buffer.read())
    tool_input = payload.get("tool_input")
    url = tool_input.get("url") if isinstance(tool_input, dict) else None
    if recalled(url, seen_urls(log_path(), payload.get("session_id"))):
        sys.stdout.write(json.dumps({"systemMessage": WARNING.format(url=url)}))
except Exception:
    pass

sys.exit(0)
