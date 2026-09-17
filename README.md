# agentic-seo-meter

A Claude Code plugin that logs the documentation your coding agent fetches and reports the token cost.

Agents read docs before they write code. agentic-seo-meter shows you which docs they read, what those reads cost, and whether the domain publishes an `llms.txt` index that would make the next read cheaper.

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

Work normally. A hook records every `WebFetch` and every fetch/scrape/crawl MCP tool call.

Then run:

```
/docs-report          # this session
/docs-report --all    # every session
```

## Output

```
## Docs fetch report (session 8f2c...)

- Fetches: 14 (1 failed)
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

### llms.txt coverage
- `docs.example.com` publishes llms.txt; the session never fetched it.
- `api.other.dev` has no llms.txt: 5 fetches, 51,781 est. tokens.
  - An index file would let an agent resolve this domain in fewer requests.
```

## Notes

- Tokens are estimated at 4 bytes per token.
- The log is a JSONL file at `~/.claude/agentic-seo-meter/fetches.jsonl`, or at `$CLAUDE_PLUGIN_DATA` when set.
- Nothing leaves your machine except the `llms.txt` probe that `/docs-report` sends to each domain.

## License

MIT
