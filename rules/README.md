# Rules for Surge

Two daily-merged rule families, each built by a standard-library Python script and a GitHub Action:

| Family | Script | Workflow | Schedule |
|---|---|---|---|
| AI routing | [`scripts/update_ai_rules.py`](../scripts/update_ai_rules.py) | [`update-ai-rules.yml`](../.github/workflows/update-ai-rules.yml) | 20:17 UTC (04:17 Singapore) |
| Ad blocking | [`scripts/update_adblock_rules.py`](../scripts/update_adblock_rules.py) | [`update-adblock-rules.yml`](../.github/workflows/update-adblock-rules.yml) | 20:47 UTC (04:47 Singapore), and on pushes that edit its config |

# AI routing rules

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

# Ad-blocking rules

Three layers plus generated modules (see [`modules/adblock/README.md`](../modules/adblock/README.md)).

## Use in Surge (Mac mini, MacBook, iPhone)

Replace the two blackmatrix7 `Advertising` lines in `[Rule]` (Shared.dconf) with:

```
DOMAIN-SET,https://raw.githubusercontent.com/hqy-cmd/useformyself/main/rules/Reject_Domain.list,REJECT,pre-matching
RULE-SET,https://raw.githubusercontent.com/hqy-cmd/useformyself/main/rules/Reject.list,REJECT
DOMAIN-SET,https://raw.githubusercontent.com/hqy-cmd/useformyself/main/rules/Reject_Extra_Domain.list,Advertising
```

Keep the existing switchable group `Advertising = select, REJECT, DIRECT, hidden=true`; switching it to DIRECT
turns off only the aggressive layer when something breaks. Put the two non-pre-matching lines where the bm7
lines were: after your LAN / bank DIRECT exceptions and before the AI, Apple, Google and other proxy groups.

The hand-written rejects that were in the profile (`business.msstatic.com`, `v1d.szbdyd.com`, the Huya
HTTPDNS `URL-REGEX` and `IP-CIDR,0.0.0.0/32`) are now in `adblock-include.txt`, so those `[Rule]` lines can be
removed. The `AND,((PROTOCOL,UDP),(DEST-PORT,443)),REJECT-NO-DROP` QUIC block is not ad blocking; leave it.

Optional: append `,extended-matching` to the first line to also match TLS SNI / Host headers of apps that connect
by IP address.

### `pre-matching` on Surge Mac 6.4.4

`pre-matching` exists since Surge Mac 5.9.0 / iOS 5.14.0, so it is valid on Mac 6.4.4 and current iOS Surge 5.
It only works with REJECT-family policies (REJECT, REJECT-DROP, REJECT-NO-DROP...), never with a policy group,
which is why:

- `Reject_Domain.list` uses `REJECT,pre-matching`: matched names are refused at DNS (no record) / TCP SYN (RST),
  the cheapest possible reject. Pre-matching rules run before every other rule, which is why exceptions such
  as the AI group or banks are removed inside the generator instead of relying on rule order.
- `Reject.list` stays plain `REJECT`: it contains a URL-REGEX, which pre-matching cannot evaluate, and
  `pre-matching` is not allowed inside rule-set files.
- `Reject_Extra_Domain.list` goes to the `Advertising` group so it can be switched off, so no pre-matching.

Other syntax used: DOMAIN-SET with `.suffix` lines, DOMAIN-WILDCARD (iOS 5.11.0+), AND rules and `IP-CIDR ...,no-resolve`
in the rule set. Nothing needs Surge 6.9+. Surge itself was not available in CI or in the build VM; run
`surge-cli --check` once on the Mac mini after switching.

## Files

| File | Purpose |
|---|---|
| `Reject_Domain.list` | Core DOMAIN-SET (~144k). Sukka reject, AWAvenue (秋风), 217heidai lite, v2fly category-ads-all, kelee 广告平台拦截器 domains, plus whole-host rejects found in the ddgksf2013 / fmz200 modules. |
| `Reject.list` | RULE-SET (~1k): DOMAIN-KEYWORD, DOMAIN-WILDCARD, AND, URL-REGEX and `IP-CIDR,...,no-resolve` rules from Sukka / kelee / AWAvenue and your includes. |
| `Reject_Extra_Domain.list` | Aggressive DOMAIN-SET (~185k): Sukka reject_extra + HaGeZi Multi PRO, minus everything the core layer already covers. |
| `adblock-exclude.txt` | Whitelist, removed from all three layers (Statsig, Sentry, gvt2, GTM, Branch / OneLink / Adjust deep links, over-broad keywords and regexes, TikTok network config). |
| `adblock-include.txt` | Manual additions (applied after the whitelist, still checked by the guard). |
| `adblock-guard.txt` | Must-not-block names (Apple, iCloud, GitHub, Google, Microsoft core hosts; bank and payment domains as whole trees). Removed from input and re-checked against the outputs: a match fails the run. |
| `adblock-report.md` | Latest run: upstream status, every removal per category, public-suffix drops, module selection. |
| `adblock-changelog.md` | Added / removed lines per output, newest first. |
| `adblock-state.json` | Last good count, hash and fetch time of each upstream (feeds the safety checks). |
| `adblock-seed/` | Last-resort copy of the ddgksf2013 module (only published on Cloudflare-protected yfamilys.com). |

Everything in `rules/AI_Domain.list` is protected automatically: an ad entry equal to, above or below an AI
domain is removed (for example `statsigapi.net`, `featuregates.org`, `*.ingest.sentry.io`,
`copilot-telemetry.githubusercontent.com`). Apple and Firebase telemetry (`metrics.icloud.com`,
`api-adservices.apple.com`, `iadsdk.apple.com`, `app-measurement.com`, `firebaselogging-pa.googleapis.com`) stays
blocked on purpose.

## Upstreams

| Upstream | Layer | URL |
|---|---|---|
| Sukka reject (domainset / non_ip / ip) | core | `https://ruleset.skk.moe/List/{domainset,non_ip,ip}/reject.conf` |
| AWAvenue-Ads-Rule (秋风) | core | `https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main/Filters/AWAvenue-Ads-Rule-Surge-RULE-SET.list` |
| 217heidai adblockfilters lite | core | `https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblocksurgelite.list` |
| v2fly category-ads-all (MetaCubeX) | core | `https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-ads-all.list` |
| kelee 广告平台拦截器 `[Rule]` | core | `https://kelee.one/Tool/Loon/Lpx/BlockAdvertisers.lpx`, mirrors: zwjtano/kelee-loon-surge-modules, QingRex/LoonKissSurge (the installed copy) |
| Sukka reject_extra | extra | `https://ruleset.skk.moe/List/domainset/reject_extra.conf` |
| HaGeZi Multi PRO | extra | `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/pro-onlydomains.txt` |
| Public Suffix List | filter | `https://publicsuffix.org/list/public_suffix_list.dat` |

Licences: Sukka's ruleset is AGPL-3.0 and HaGeZi's lists GPL-3.0; the generated lists are derived from them.

## Processing and safety

- Lowercase, trim, dedupe; a parent `.suffix` absorbs its children; entries that are themselves a public suffix
  (`.square.site`, `.dkonto.pl`, bare TLDs, ...) are dropped.
- Whitelist semantics follow Surge matching: `DOMAIN,x` keeps `x` reachable (drops `x`, `.x` and broader
  suffixes but not `tracker.x`); `DOMAIN-SUFFIX,x` keeps the whole tree reachable and also drops keywords,
  wildcards and AND rules aimed at it.
- Per upstream: download failure, a Cloudflare challenge page, or fewer than 50% of the last good entry
  count falls back to the last snapshot, then to `adblock-seed/`; with neither the run aborts.
- Per output: more than 30% shrink aborts the run (re-run the workflow with `force` after reviewing).
- Raw upstream copies are **not** committed to `main`. The workflow keeps them on the single-commit orphan
  branch `adblock-upstream-cache` (force-pushed when an upstream changes), so `main` only receives the
  generated outputs when they change.

Run locally from the repository root: `python3 scripts/update_adblock_rules.py --dry-run`; tests:
`python3 scripts/test_adblock_rules.py`.
