import os


def data_dir(override=""):
    return override or os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.join(os.path.expanduser("~"), ".claude", "agentic-seo-meter")


def log_path(override=""):
    return os.path.normpath(os.path.join(data_dir(override), "fetches.jsonl"))
