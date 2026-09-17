import re
from urllib.parse import urljoin, urlparse

ABSOLUTE = re.compile(r"https?://[^\s\"'<>)\]}\\]+", re.I)
MARKDOWN = re.compile(r"\]\(\s*<?([^)\s>]+)")
ATTRIBUTE = re.compile(r"(?:href|src)=[\"']([^\"']+)[\"']", re.I)
TRAILING = ".,;:!?'\"*_"
MAX_LINKS = 500
MIN_DEPTH = 2


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            for text in strings(item):
                yield text
    elif isinstance(value, list):
        for item in value:
            for text in strings(item):
                yield text


def key(url):
    parts = urlparse((url or "").strip())
    if parts.scheme not in ("http", "https"):
        return ""
    host = (parts.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if not host:
        return ""
    return host + parts.path.rstrip("/").lower()


def depth(url):
    return len([part for part in urlparse(url or "").path.split("/") if part])


def links(value, base):
    found = set()
    for text in strings(value):
        for match in ABSOLUTE.findall(text):
            found.add(match.rstrip(TRAILING))
        for pattern in (MARKDOWN, ATTRIBUTE):
            for match in pattern.findall(text):
                found.add(urljoin(base or "", match.strip()))
    keys = sorted({item for item in (key(url) for url in found) if item})
    return keys[:MAX_LINKS], len(keys) > MAX_LINKS


def recalled(url, seen):
    target = key(url)
    return bool(target) and depth(url) >= MIN_DEPTH and target not in seen


def absorb(record, seen):
    seen.update(record.get("links") or [])
    target = key(record.get("url"))
    if target:
        seen.add(target)
