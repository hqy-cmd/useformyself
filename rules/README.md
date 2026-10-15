# AI routing rules for Surge

A merged AI rule set, rebuilt daily at 20:17 UTC (04:17 Singapore) by
[`.github/workflows/update-ai-rules.yml`](../.github/workflows/update-ai-rules.yml) using
[`scripts/update_ai_rules.py`](../scripts/update_ai_rules.py) (Python standard library only).

## Use in Surge (Mac and iPhone)

Add both lines to `[Rule]`, pointing at your AI policy group (here `AI`). Put them before
Apple, Microsoft, Google and other broad proxy rules so they take priority.

```
DOMAIN-SET,https://raw.githubusercontent.com/hqy-cmd/useformyself/main/rules/AI_Domain.list,AI
RULE-SET,https://raw.githubusercontent.com/hqy-cmd/useformyself/main/rules/AI.list,AI
```

## Files

| File | Purpose |
|---|---|
| `AI_Domain.list` | Surge DOMAIN-SET. `.example.com` matches the domain and all subdomains, `example.com` matches exactly. All DOMAIN / DOMAIN-SUFFIX entries live here. |
| `AI.list` | Surge RULE-SET with only DOMAIN-KEYWORD, IP-CIDR / IP-CIDR6 and IP-ASN rules (IP rules carry `no-resolve`). |
| `ai-exclude.txt` | Hand-edited exclusions (exact domain, suffix, wildcard, keyword, CIDR, ASN), grouped into report categories. |
| `ai-include.txt` | Hand-edited additions; applied after exclusions, so they always win. |
| `ai-report.md` | Latest run: upstream counts, dropped rule types (PROCESS-NAME etc.), what each exclusion category removed. |
| `ai-changelog.md` | Added / removed entries per update, newest first. |
| `ai-state.json` | Last good entry count and hash of each upstream, used by the safety checks. |
| `upstream-cache/` | Last good snapshot of each upstream. |

## Upstreams

1. [QuixoticHeart `ai.list`](https://raw.githubusercontent.com/QuixoticHeart/rule-set/refs/heads/ruleset/surge/ai.list)
2. [VPSDance `global.list`](https://raw.githubusercontent.com/VPSDance/ai-proxy-rules/main/rules/surge/global.list)
3. [dler-io `AI Suite.list`](https://raw.githubusercontent.com/dler-io/Rules/main/Surge/Surge%203/Provider/AI%20Suite.list)
4. [v2fly `category-ai-!cn` via MetaCubeX](https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-ai-!cn.list)

## Processing and safety

- Entries are lowercased, trimmed and deduplicated. An exact domain or suffix that is already covered by a
  broader suffix is dropped, as is a keyword that contains a shorter keyword and a CIDR inside a broader one.
- Rule types Surge DOMAIN-SET / this RULE-SET don't carry (PROCESS-NAME, USER-AGENT, URL-REGEX, wildcards, ...)
  are dropped and listed in `ai-report.md`.
- If an upstream fails to download, or parses to fewer than 50% of its last good entry count, the
  last good snapshot from `upstream-cache/` is used instead. With no snapshot available the run aborts.
- The run aborts without committing if the total output would shrink by more than 30%. After reviewing,
  run the workflow manually with `force` enabled to accept it.
- A commit is made only when `AI_Domain.list` or `AI.list` content changes.

Run locally from the repository root: `python3 scripts/update_ai_rules.py` (add `--dry-run` to preview).
