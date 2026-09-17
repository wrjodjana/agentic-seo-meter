# agentic-seo-meter

A Claude Code plugin that logs the documentation your coding agent fetches and reports the token cost.

Agents read docs before they write code. agentic-seo-meter shows you which docs they read, what those reads cost, whether they looked the URL up or typed it from memory, and whether the domain publishes an `llms.txt` index.

## Install

```
/plugin marketplace add wrjodjana/agentic-seo-meter
/plugin install agentic-seo-meter@agentic-seo-meter
```

To install from a local clone instead:

```
/plugin marketplace add ./agentic-seo-meter
/plugin install agentic-seo-meter@agentic-seo-meter
```

To update later:

```
/plugin marketplace update agentic-seo-meter
```

## Use

Work normally. A hook records every `WebFetch`, every `WebSearch`, and every fetch/scrape/crawl/search MCP tool call.

A second hook runs before each `WebFetch`. If the URL appears in no search result and on no page fetched earlier in the session, it prints a warning to the agent. It never blocks the call.

Then run:

```
/docs-report          # this session
/docs-report --all    # every session
```

## Output

```
## Docs fetch report (session 8f2c...)

- Fetches: 14 (1 failed)
- Searches: 2
- Bytes: 812,004
- Estimated tokens: 203,001
- Fetch time: 9.4 s

### By domain
| Domain | Fetches | Est. tokens |
| --- | --- | --- |
| docs.example.com | 9 | 151,220 |
| api.other.dev | 5 | 51,781 |

### URLs by estimated tokens
...

### Unsourced URLs

No search result or earlier fetched page contained these paths, so they were
written from the model's own memory:

| URL | Est. tokens |
| --- | --- |
| https://docs.example.com/api/tour | 2,118 |

1 of 14 fetches unsourced, 2,118 est. tokens, against 2 searches.

### llms.txt coverage
- `docs.example.com` publishes llms.txt; the session never fetched it.
- `api.other.dev` has no llms.txt: 5 fetches, 51,781 est. tokens.
  - An index file would let an agent resolve this domain in fewer requests.
```

## Notes

- Tokens are estimated at 4 bytes per token.
- A URL counts as unsourced when its path is two or more segments deep and it appears in no search result and on no page fetched earlier in the same session. Site roots and one-segment entry points are never flagged.
- Unsourced proves only that the log holds no source. A URL you paste yourself, or one read from a file, also counts as unsourced.
- The log keeps at most 500 links per page. Past that the report says so, because a path it flags may still have been linked.
- The log is a JSONL file at `~/.claude/agentic-seo-meter/fetches.jsonl`, or at `$CLAUDE_PLUGIN_DATA` when set.
- Nothing leaves your machine except the `llms.txt` probe that `/docs-report` sends to each domain.

## License

MIT
