import datetime
import json
import os
import sys

from store import log_path


def field(obj, key):
    if isinstance(obj, dict):
        return obj.get(key)
    return None


def text_bytes(value):
    if isinstance(value, str):
        return len(value.encode("utf-8"))
    if isinstance(value, dict):
        value = list(value.values())
    if not isinstance(value, list):
        return None
    sizes = [size for size in (text_bytes(item) for item in value) if size is not None]
    if not sizes:
        return None
    return sum(sizes)


try:
    payload = json.loads(sys.stdin.buffer.read())
    tool_input = field(payload, "tool_input")
    tool_response = field(payload, "tool_response")

    size = field(tool_response, "bytes")
    if not isinstance(size, int):
        size = text_bytes(tool_response)

    duration_ms = field(payload, "duration_ms")
    if duration_ms is None:
        duration_ms = field(tool_response, "durationMs")

    url = field(tool_input, "url")
    if url is None:
        url = field(tool_response, "url")

    record = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "event": field(payload, "hook_event_name"),
        "session_id": field(payload, "session_id"),
        "cwd": field(payload, "cwd"),
        "tool_name": field(payload, "tool_name"),
        "url": url,
        "bytes": size,
        "code": field(tool_response, "code"),
        "duration_ms": duration_ms,
    }

    path = log_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "ab") as f:
        f.write((json.dumps(record) + "\n").encode("utf-8"))
except Exception:
    pass

sys.exit(0)
