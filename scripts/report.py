import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse

from store import log_path

LLMS_TIMEOUT = 5
LLMS_MIN_FETCHES = 1
LLMS_MAX_BYTES = 65536


def out(text):
    sys.stdout.buffer.write(text.encode("utf-8"))


def read_records(path):
    records = []
    with open(path, "rb") as f:
        for line in f:
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if isinstance(record, dict):
                records.append(record)
    return records


def number(value):
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return 0


def table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(" --- " for _ in headers) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def group(records, key):
    groups = {}
    for record in records:
        groups.setdefault(key(record), []).append(record)
    return groups


def byte_total(records):
    return sum(number(record.get("bytes")) for record in records)


def tokens(records):
    return sum(number(record.get("bytes")) // 4 for record in records)


def summary(records, scope):
    failures = [record for record in records if record.get("event") == "PostToolUseFailure"]
    unsized = [record for record in records if record.get("event") != "PostToolUseFailure" and record.get("bytes") is None]
    lines = [
        f"## Docs fetch report ({scope})",
        "",
        f"- Fetches: {len(records):,} ({len(failures):,} failed)",
        f"- Bytes: {byte_total(records):,}",
        f"- Estimated tokens: {tokens(records):,}",
        f"- Fetch time: {sum(number(record.get('duration_ms')) for record in records) / 1000:,.1f} s",
    ]
    if unsized:
        lines.append(f"- Fetches with unknown size: {len(unsized):,}")
    return lines


def host(url):
    name = (urlparse(url or "").hostname or "").lower()
    if name.startswith("www."):
        name = name[4:]
    return name


def is_llms_txt(url):
    return urlparse(url or "").path.lower().rstrip("/").endswith("/llms.txt")


def check_llms_txt(domain):
    request = urllib.request.Request(
        f"https://{domain}/llms.txt",
        headers={"User-Agent": "agentic-seo-meter", "Accept": "text/plain, */*"},
    )
    try:
        with urllib.request.urlopen(request, timeout=LLMS_TIMEOUT) as response:
            if getattr(response, "status", None) != 200:
                return "absent", f"HTTP {getattr(response, 'status', '?')}"
            body = response.read(LLMS_MAX_BYTES)
    except urllib.error.HTTPError as error:
        return "absent", f"HTTP {error.code}"
    except Exception as error:
        return "unknown", type(error).__name__
    if not body.strip():
        return "absent", "empty body"
    return "present", ""


def cost(items):
    return f"{len(items):,} fetch{'' if len(items) == 1 else 'es'}, {tokens(items):,} est. tokens"


def llms_lines(records):
    hosts = group([record for record in records if host(record.get("url"))], lambda record: host(record.get("url")))
    frequent = [item for item in hosts.items() if len(item[1]) >= LLMS_MIN_FETCHES]
    lines = ["", "### llms.txt coverage", ""]
    if not frequent:
        lines.append("No fetched URL had a host to check.")
        return lines
    for domain, items in sorted(frequent, key=lambda item: tokens(item[1]), reverse=True):
        state, detail = check_llms_txt(domain)
        if state == "present":
            seen = "the session fetched it" if any(is_llms_txt(record.get("url")) for record in items) else "the session never fetched it"
            lines.append(f"- `{domain}` publishes llms.txt; {seen}.")
        elif state == "unknown":
            lines.append(f"- `{domain}`: llms.txt unknown ({detail}), {cost(items)}.")
        else:
            lines.append(f"- `{domain}` has no llms.txt: {cost(items)}.")
            lines.append("  - An index file would let an agent resolve this domain in fewer requests.")
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="")
    parser.add_argument("--session", default="")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    path = log_path(args.data)
    if not os.path.exists(path):
        out(f"No docs fetches logged yet. Log file: {path}\n")
        return

    records = read_records(path)
    by_session = bool(args.session) and not args.all
    if by_session:
        records = [record for record in records if record.get("session_id") == args.session]
    scope = f"session {args.session}" if by_session else "all sessions"
    if not records:
        out(f"No docs fetches logged for {scope}. Log file: {path}\n")
        return

    lines = summary(records, scope)

    if not by_session:
        sessions = group(records, lambda record: record.get("session_id") or "(unknown)")
        rows = [
            (session, items[-1].get("cwd") or "", len(items), f"{tokens(items):,}")
            for session, items in sorted(sessions.items(), key=lambda item: tokens(item[1]), reverse=True)
        ]
        lines += ["", "### By session", "", table(["Session", "Project", "Fetches", "Est. tokens"], rows)]

    domains = group(records, lambda record: urlparse(record.get("url") or "").netloc or "(unknown)")
    rows = [
        (domain, len(items), f"{tokens(items):,}")
        for domain, items in sorted(domains.items(), key=lambda item: tokens(item[1]), reverse=True)
    ]
    lines += ["", "### By domain", "", table(["Domain", "Fetches", "Est. tokens"], rows)]

    urls = group(records, lambda record: record.get("url") or "(unknown)")
    ranked = sorted(urls.items(), key=lambda item: tokens(item[1]), reverse=True)
    rows = [
        (url, len(items), f"{byte_total(items):,}", f"{tokens(items):,}")
        for url, items in ranked[: args.top]
    ]
    lines += ["", "### URLs by estimated tokens", "", table(["URL", "Fetches", "Bytes", "Est. tokens"], rows)]

    try:
        lines += llms_lines(records)
    except Exception as error:
        lines += ["", "### llms.txt coverage", "", f"Check unavailable ({type(error).__name__})."]

    out("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
