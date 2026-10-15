#!/usr/bin/env python3
"""Merge upstream AI routing rules into Surge DOMAIN-SET / RULE-SET files.

Standard library only. Run from the repository root:

    python3 scripts/update_ai_rules.py [--force] [--dry-run]

Exit codes: 0 = success (changed or unchanged), 1 = aborted by a safety check.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import ipaddress
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "rules"
CACHE = RULES / "upstream-cache"
DOMAIN_OUT = RULES / "AI_Domain.list"
RULESET_OUT = RULES / "AI.list"
EXCLUDE_FILE = RULES / "ai-exclude.txt"
INCLUDE_FILE = RULES / "ai-include.txt"
STATE_FILE = RULES / "ai-state.json"
CHANGELOG = RULES / "ai-changelog.md"
REPORT = RULES / "ai-report.md"

UPSTREAMS = [
    {
        "name": "QuixoticHeart",
        "file": "quixoticheart-ai.list",
        "format": "surge",
        "url": "https://raw.githubusercontent.com/QuixoticHeart/rule-set/refs/heads/ruleset/surge/ai.list",
    },
    {
        "name": "VPSDance",
        "file": "vpsdance-global.list",
        "format": "surge",
        "url": "https://raw.githubusercontent.com/VPSDance/ai-proxy-rules/main/rules/surge/global.list",
    },
    {
        "name": "dler-io",
        "file": "dler-io-ai-suite.list",
        "format": "surge",
        "url": "https://raw.githubusercontent.com/dler-io/Rules/main/Surge/Surge%203/Provider/AI%20Suite.list",
    },
    {
        "name": "v2fly category-ai-!cn (MetaCubeX)",
        "file": "metacubex-category-ai-not-cn.list",
        "format": "clash-domain",
        "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-ai-!cn.list",
    },
]

MIN_UPSTREAM_RATIO = 0.5   # upstream must keep >= 50% of its last good entry count
MIN_UPSTREAM_ENTRIES = 10  # floor used when no previous count is known
MAX_OUTPUT_SHRINK = 0.30   # abort if total output shrinks by more than 30%
CHANGELOG_MAX_ITEMS = 100  # per added/removed list in one changelog entry
CHANGELOG_MAX_RUNS = 60

DOMAIN_RE = re.compile(r"^(?=.{1,253}$)([a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?\.)+[a-z0-9-]{2,63}$")

SURGE_TYPES = {
    "DOMAIN": "full",
    "HOST": "full",
    "DOMAIN-SUFFIX": "suffix",
    "HOST-SUFFIX": "suffix",
    "DOMAIN-KEYWORD": "keyword",
    "HOST-KEYWORD": "keyword",
    "IP-CIDR": "ip",
    "IP-CIDR6": "ip",
    "IP6-CIDR": "ip",
    "IP-ASN": "asn",
    "DOMAIN-WILDCARD": "wildcard",
}


class Abort(Exception):
    pass


def log(msg: str) -> None:
    print(msg, flush=True)


def gh_annotation(level: str, msg: str) -> None:
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::{level}::{msg}", flush=True)


# ---------------------------------------------------------------- parsing

class RuleSet:
    def __init__(self) -> None:
        self.full: set[str] = set()
        self.suffix: set[str] = set()
        self.keyword: set[str] = set()
        self.ip: set[str] = set()
        self.asn: set[str] = set()
        self.wildcard: set[str] = set()
        self.dropped: dict[str, set[str]] = defaultdict(set)  # reason -> raw lines
        self.parsed_lines = 0

    def count(self) -> int:
        return len(self.full) + len(self.suffix) + len(self.keyword) + len(self.ip) + len(self.asn)


def norm_domain(value: str) -> str:
    return value.strip().strip("'\"").lower().rstrip(".")


def norm_ip(value: str) -> str | None:
    try:
        return str(ipaddress.ip_network(value.strip(), strict=False))
    except ValueError:
        return None


def norm_asn(value: str) -> str | None:
    v = value.strip().upper()
    if v.startswith("AS"):
        v = v[2:]
    return v if v.isdigit() else None


def add_rule(rs: RuleSet, kind: str, value: str, raw: str) -> None:
    if kind in ("full", "suffix"):
        d = norm_domain(value).lstrip(".")
        if not DOMAIN_RE.match(d):
            rs.dropped["invalid domain"].add(raw)
            return
        getattr(rs, kind).add(d)
    elif kind == "keyword":
        k = value.strip().lower()
        if k:
            rs.keyword.add(k)
    elif kind == "ip":
        n = norm_ip(value)
        if n is None:
            rs.dropped["invalid IP-CIDR"].add(raw)
        else:
            rs.ip.add(n)
    elif kind == "asn":
        a = norm_asn(value)
        if a is None:
            rs.dropped["invalid IP-ASN"].add(raw)
        else:
            rs.asn.add(a)
    elif kind == "wildcard":
        rs.wildcard.add(value.strip().lower())


def parse_surge(text: str, rs: RuleSet, allow_wildcard: bool = False) -> None:
    """Surge RULE-SET lines; bare lines are treated as DOMAIN-SET entries."""
    for line in text.splitlines():
        line = line.strip()
        if not line or line[0] in "#;!" or line.startswith("//") or line.startswith("["):
            continue
        rs.parsed_lines += 1
        if "," not in line:
            if line.startswith("."):
                add_rule(rs, "suffix", line[1:], line)
            elif line.startswith("+."):
                add_rule(rs, "suffix", line[2:], line)
            else:
                add_rule(rs, "full", line, line)
            continue
        parts = [p.strip() for p in line.split(",")]
        rtype = parts[0].upper()
        kind = SURGE_TYPES.get(rtype)
        if kind is None or len(parts) < 2:
            rs.dropped[rtype or "unknown"].add(line)
            continue
        if kind == "wildcard" and not allow_wildcard:
            rs.dropped[rtype].add(line)
            continue
        add_rule(rs, kind, parts[1], line)


def parse_clash_domain(text: str, rs: RuleSet) -> None:
    """Clash/mihomo domain text: `+.x` = suffix, `.x` = suffix, bare = full."""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- "):
            line = line[2:].strip().strip("'\"")
        if not line or line[0] in "#;!" or line.startswith("payload"):
            continue
        rs.parsed_lines += 1
        if line.startswith("+."):
            add_rule(rs, "suffix", line[2:], line)
        elif line.startswith("."):
            add_rule(rs, "suffix", line[1:], line)
        elif "*" in line or line.startswith("regexp:"):
            rs.dropped["wildcard/regex (domain text)"].add(line)
        else:
            add_rule(rs, "full", line, line)


def parse_upstream(fmt: str, text: str) -> RuleSet:
    rs = RuleSet()
    if fmt == "surge":
        parse_surge(text, rs)
    else:
        parse_clash_domain(text, rs)
    return rs


# ---------------------------------------------------------------- exclude / include files

class Rule:
    def __init__(self, category: str, rtype: str, value: str, raw: str) -> None:
        self.category = category
        self.rtype = rtype
        self.value = value
        self.raw = raw
        self.hits: list[str] = []


def parse_rule_file(path: Path) -> list[Rule]:
    rules: list[Rule] = []
    if not path.exists():
        return rules
    category = "uncategorised"
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.split(" #", 1)[0].strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            category = line[1:-1].strip()
            continue
        if "," in line:
            rtype, value = (p.strip() for p in line.split(",", 1))
            value = value.split(",", 1)[0].strip()
            rtype = rtype.upper()
        elif line.startswith("."):
            rtype, value = "DOMAIN-SUFFIX", line[1:]
        else:
            rtype, value = "DOMAIN", line
        rtype = {"HOST": "DOMAIN", "HOST-SUFFIX": "DOMAIN-SUFFIX", "HOST-KEYWORD": "DOMAIN-KEYWORD",
                 "IP6-CIDR": "IP-CIDR6"}.get(rtype, rtype)
        if rtype in ("DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-WILDCARD", "DOMAIN-KEYWORD"):
            value = norm_domain(value).lstrip(".") if rtype != "DOMAIN-WILDCARD" else value.lower()
        elif rtype in ("IP-CIDR", "IP-CIDR6"):
            n_ = norm_ip(value)
            if n_ is None:
                raise Abort(f"{path.name}:{n}: invalid CIDR {value!r}")
            value = n_
        elif rtype == "IP-ASN":
            a = norm_asn(value)
            if a is None:
                raise Abort(f"{path.name}:{n}: invalid ASN {value!r}")
            value = a
        else:
            raise Abort(f"{path.name}:{n}: unsupported rule type {rtype!r}")
        rules.append(Rule(category, rtype, value, line))
    return rules


def parents(domain: str):
    parts = domain.split(".")
    for i in range(len(parts) - 1):
        yield ".".join(parts[i:])


def domain_excluded(name: str, rule: Rule) -> bool:
    if rule.rtype == "DOMAIN":
        return name == rule.value
    if rule.rtype == "DOMAIN-SUFFIX":
        return name == rule.value or name.endswith("." + rule.value)
    if rule.rtype == "DOMAIN-WILDCARD":
        return any(fnmatch.fnmatchcase(p, rule.value) for p in parents(name))
    return False


def apply_excludes(rs: RuleSet, rules: list[Rule]) -> None:
    def first_match(pred):
        for r in rules:
            if pred(r):
                return r
        return None

    for attr, label in (("full", "DOMAIN"), ("suffix", "DOMAIN-SUFFIX")):
        for name in sorted(getattr(rs, attr)):
            r = first_match(lambda r: domain_excluded(name, r))
            if r:
                getattr(rs, attr).discard(name)
                r.hits.append(f"{label},{name}")
    for kw in sorted(rs.keyword):
        r = first_match(lambda r: r.rtype == "DOMAIN-KEYWORD" and kw == r.value)
        if r:
            rs.keyword.discard(kw)
            r.hits.append(f"DOMAIN-KEYWORD,{kw}")
    for cidr in sorted(rs.ip):
        net = ipaddress.ip_network(cidr)
        r = first_match(lambda r: r.rtype in ("IP-CIDR", "IP-CIDR6")
                        and ipaddress.ip_network(r.value).version == net.version
                        and net.subnet_of(ipaddress.ip_network(r.value)))
        if r:
            rs.ip.discard(cidr)
            r.hits.append(f"IP-CIDR,{cidr}")
    for asn in sorted(rs.asn):
        r = first_match(lambda r: r.rtype == "IP-ASN" and asn == r.value)
        if r:
            rs.asn.discard(asn)
            r.hits.append(f"IP-ASN,{asn}")


def apply_includes(rs: RuleSet, rules: list[Rule]) -> None:
    kinds = {"DOMAIN": "full", "DOMAIN-SUFFIX": "suffix", "DOMAIN-KEYWORD": "keyword",
             "IP-CIDR": "ip", "IP-CIDR6": "ip", "IP-ASN": "asn"}
    for r in rules:
        kind = kinds.get(r.rtype)
        if kind is None:
            raise Abort(f"ai-include.txt: {r.rtype} is not supported for includes")
        if kind in ("full", "suffix") and not DOMAIN_RE.match(r.value):
            raise Abort(f"ai-include.txt: invalid domain {r.value!r}")
        getattr(rs, kind).add(r.value)
        r.hits.append(r.raw)


# ---------------------------------------------------------------- normalisation

def dedupe(rs: RuleSet) -> dict[str, int]:
    removed = defaultdict(int)

    def broader_suffix(name: str, strict: bool) -> bool:
        for p in parents(name):
            if strict and p == name:
                continue
            if p in rs.suffix:
                return True
        return False

    for name in list(rs.full):
        if broader_suffix(name, strict=False):
            rs.full.discard(name)
            removed["DOMAIN covered by DOMAIN-SUFFIX"] += 1
    for name in list(rs.suffix):
        if broader_suffix(name, strict=True):
            rs.suffix.discard(name)
            removed["DOMAIN-SUFFIX covered by broader DOMAIN-SUFFIX"] += 1
    for kw in list(rs.keyword):
        if any(other != kw and other in kw for other in rs.keyword):
            rs.keyword.discard(kw)
            removed["DOMAIN-KEYWORD covered by shorter keyword"] += 1
    nets = [ipaddress.ip_network(c) for c in rs.ip]
    for net in nets:
        if any(o != net and o.version == net.version and net.subnet_of(o) for o in nets):
            rs.ip.discard(str(net))
            removed["IP-CIDR covered by broader CIDR"] += 1
    return dict(removed)


def domain_lines(rs: RuleSet) -> list[str]:
    entries = [(n, "." + n) for n in rs.suffix] + [(n, n) for n in rs.full]
    return [line for _, line in sorted(entries, key=lambda e: (e[0].split(".")[::-1], e[1]))]


def ruleset_lines(rs: RuleSet) -> list[str]:
    out = [f"DOMAIN-KEYWORD,{k}" for k in sorted(rs.keyword)]
    nets = sorted((ipaddress.ip_network(c) for c in rs.ip), key=lambda n: (n.version, n))
    for n in nets:
        out.append(f"{'IP-CIDR' if n.version == 4 else 'IP-CIDR6'},{n},no-resolve")
    out += [f"IP-ASN,{a},no-resolve" for a in sorted(rs.asn, key=int)]
    return out


# ---------------------------------------------------------------- io helpers

def fetch(url: str, attempts: int = 4) -> str:
    last: Exception | None = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ai-rules-merger/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = e
            if i < attempts - 1:
                time.sleep(2 ** (i + 2))
    raise RuntimeError(f"download failed after {attempts} attempts: {last}")


def read_body(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [l.strip() for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.lstrip().startswith("#")]


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"upstreams": {}}


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="skip shrink safety checks")
    ap.add_argument("--dry-run", action="store_true", help="do not write any files")
    args = ap.parse_args()

    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    stamp = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    state = load_state()
    prev_up = state.get("upstreams", {})

    merged = RuleSet()
    up_status: list[dict] = []
    new_cache: dict[str, str] = {}
    warnings: list[str] = []

    for up in UPSTREAMS:
        name = up["name"]
        cache_path = CACHE / up["file"]
        prev = prev_up.get(name, {})
        prev_count = prev.get("count")
        status = {"name": name, "url": up["url"], "source": "fresh"}
        text = None
        problem = None
        try:
            text = fetch(up["url"])
            rs = parse_upstream(up["format"], text)
            floor = max(MIN_UPSTREAM_ENTRIES, int((prev_count or 0) * MIN_UPSTREAM_RATIO))
            if rs.count() < floor:
                problem = f"parsed only {rs.count()} entries (previous good: {prev_count}, floor {floor})"
        except Exception as e:  # noqa: BLE001
            problem = str(e)
        if problem:
            msg = f"{name}: {problem}"
            if not cache_path.exists():
                raise Abort(msg + "; no cached snapshot available")
            msg += "; using last good snapshot"
            warnings.append(msg)
            gh_annotation("warning", msg)
            log("WARN " + msg)
            text = cache_path.read_text(encoding="utf-8")
            rs = parse_upstream(up["format"], text)
            status["source"] = f"cached snapshot ({prev.get('fetched_at', 'unknown date')})"
            status["fetched_at"] = prev.get("fetched_at")
        else:
            new_cache[up["file"]] = text
            status["fetched_at"] = (prev.get("fetched_at") if prev.get("sha256") == sha256(text)
                                    else stamp)
        status.update(count=rs.count(), sha256=sha256(text), lines=rs.parsed_lines,
                      dropped={k: sorted(v) for k, v in rs.dropped.items()},
                      breakdown={"DOMAIN": len(rs.full), "DOMAIN-SUFFIX": len(rs.suffix),
                                 "DOMAIN-KEYWORD": len(rs.keyword), "IP-CIDR": len(rs.ip),
                                 "IP-ASN": len(rs.asn)})
        up_status.append(status)
        log(f"{name}: {status['count']} entries [{status['source']}]")
        for attr in ("full", "suffix", "keyword", "ip", "asn"):
            getattr(merged, attr).update(getattr(rs, attr))
        for k, v in rs.dropped.items():
            merged.dropped[k].update(v)

    raw_union = merged.count()
    excludes = parse_rule_file(EXCLUDE_FILE)
    includes = parse_rule_file(INCLUDE_FILE)
    apply_excludes(merged, excludes)
    apply_includes(merged, includes)
    dedupe_stats = dedupe(merged)

    new_domains = domain_lines(merged)
    new_rules = ruleset_lines(merged)
    old_domains = read_body(DOMAIN_OUT)
    old_rules = read_body(RULESET_OUT)

    old_total = len(old_domains) + len(old_rules)
    new_total = len(new_domains) + len(new_rules)
    if old_total and new_total < old_total * (1 - MAX_OUTPUT_SHRINK) and not args.force:
        raise Abort(f"output would shrink from {old_total} to {new_total} entries "
                    f"(>{int(MAX_OUTPUT_SHRINK * 100)}%); refusing to publish")
    if not new_domains:
        raise Abort("domain output is empty")

    added = sorted(set(new_domains) - set(old_domains)) + sorted(set(new_rules) - set(old_rules))
    removed = sorted(set(old_domains) - set(new_domains)) + sorted(set(old_rules) - set(new_rules))
    changed = new_domains != old_domains or new_rules != old_rules
    summary = f"AI rules: +{len(added)} -{len(removed)} ({len(new_domains)} domains, {len(new_rules)} rules)"
    log(summary)

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"changed={'true' if changed else 'false'}\n")
            f.write(f"commit_message={summary}\n")

    if not changed:
        log("Outputs unchanged; nothing written.")
        return 0
    if args.dry_run:
        log("Dry run; nothing written.")
        return 0

    counts_line = ", ".join(f"{s['name']}={s['count']}" for s in up_status)
    up_header = [f"#   - {s['name']}: {s['count']} entries [{s['source']}]\n#     {s['url']}"
                 for s in up_status]

    def header(title: str, body_desc: str) -> str:
        return "\n".join([
            f"# {title}",
            f"# Generated: {stamp}",
            f"# {body_desc}",
            "# Upstreams:",
            *up_header,
            f"# Exclude rules: {len(excludes)}, include rules: {len(includes)}",
            "# Source: https://github.com/hqy-cmd/useformyself/tree/main/rules",
            "",
        ])

    RULES.mkdir(exist_ok=True)
    CACHE.mkdir(exist_ok=True)
    n_kw, n_ip, n_asn = len(merged.keyword), len(merged.ip), len(merged.asn)
    DOMAIN_OUT.write_text(header(
        "AI_Domain.list - Surge DOMAIN-SET (merged AI domains)",
        f"Entries: {len(new_domains)} ({len(merged.suffix)} suffix '.x', {len(merged.full)} exact)",
    ) + "\n".join(new_domains) + "\n", encoding="utf-8")
    RULESET_OUT.write_text(header(
        "AI.list - Surge RULE-SET (merged AI keyword / IP / ASN rules)",
        f"Rules: {len(new_rules)} (DOMAIN-KEYWORD {n_kw}, IP-CIDR/IP-CIDR6 {n_ip}, IP-ASN {n_asn})",
    ) + "\n".join(new_rules) + "\n", encoding="utf-8")

    for fname, text in new_cache.items():
        (CACHE / fname).write_text(text, encoding="utf-8")

    state = {
        "generated": stamp,
        "output": {"AI_Domain.list": len(new_domains), "AI.list": len(new_rules)},
        "upstreams": {
            s["name"]: {"count": s["count"], "sha256": s["sha256"], "fetched_at": s["fetched_at"],
                        "source": "fresh" if s["source"] == "fresh" else "cached"}
            for s in up_status
        },
    }
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    write_changelog(stamp, added, removed, len(new_domains), len(new_rules), counts_line)
    write_report(stamp, up_status, raw_union, excludes, includes, merged, dedupe_stats,
                 len(new_domains), len(new_rules), warnings)
    log("Files written.")
    return 0


def write_changelog(stamp, added, removed, n_dom, n_rules, counts_line) -> None:
    def capped(items):
        shown = [f"- `{i}`" for i in items[:CHANGELOG_MAX_ITEMS]]
        if len(items) > CHANGELOG_MAX_ITEMS:
            shown.append(f"- ... and {len(items) - CHANGELOG_MAX_ITEMS} more")
        return shown or ["- (none)"]

    entry = "\n".join([
        f"## {stamp}",
        "",
        f"+{len(added)} / -{len(removed)}; now {n_dom} domains, {n_rules} rules. Upstreams: {counts_line}",
        "",
        "<details><summary>Added</summary>",
        "",
        *capped(added),
        "",
        "</details>",
        "",
        "<details><summary>Removed</summary>",
        "",
        *capped(removed),
        "",
        "</details>",
        "",
    ])
    title = "# AI rules changelog\n\nNewest first. Generated by `scripts/update_ai_rules.py`.\n\n"
    old_entries: list[str] = []
    if CHANGELOG.exists():
        parts = re.split(r"(?m)^(?=## )", CHANGELOG.read_text(encoding="utf-8"))
        old_entries = [p.rstrip("\n") + "\n" for p in parts[1:]]
    entries = [entry] + old_entries
    CHANGELOG.write_text(title + "\n".join(entries[:CHANGELOG_MAX_RUNS]), encoding="utf-8")


def write_report(stamp, up_status, raw_union, excludes, includes, merged, dedupe_stats,
                 n_dom, n_rules, warnings) -> None:
    L = [f"# AI rules report", "", f"Generated: {stamp}", ""]
    L += ["## Upstreams", "", "| Upstream | Entries | DOMAIN | SUFFIX | KEYWORD | IP-CIDR | IP-ASN | Source |",
          "|---|---|---|---|---|---|---|---|"]
    for s in up_status:
        b = s["breakdown"]
        L.append(f"| [{s['name']}]({s['url']}) | {s['count']} | {b['DOMAIN']} | {b['DOMAIN-SUFFIX']} | "
                 f"{b['DOMAIN-KEYWORD']} | {b['IP-CIDR']} | {b['IP-ASN']} | {s['source']} |")
    L += ["", f"Raw union before exclusions: {raw_union}", ""]
    if warnings:
        L += ["### Upstream warnings", ""] + [f"- {w}" for w in warnings] + [""]

    L += ["## Output", "",
          f"- `AI_Domain.list`: {n_dom} ({len(merged.suffix)} suffix, {len(merged.full)} exact)",
          f"- `AI.list`: {n_rules} (DOMAIN-KEYWORD {len(merged.keyword)}, IP-CIDR/IP-CIDR6 {len(merged.ip)}, "
          f"IP-ASN {len(merged.asn)})", ""]

    L += ["## Dropped rule types (unsupported in DOMAIN-SET / not wanted)", ""]
    if merged.dropped:
        for reason, lines in sorted(merged.dropped.items()):
            L.append(f"- **{reason}** ({len(lines)}): " + ", ".join(f"`{l}`" for l in sorted(lines)))
    else:
        L.append("- (none)")
    L.append("")

    L += ["## Exclusions by category", "", "| Category | Removed |", "|---|---|"]
    cats: dict[str, list[Rule]] = defaultdict(list)
    for r in excludes:
        cats[r.category].append(r)
    for cat, rules in cats.items():
        L.append(f"| {cat} | {sum(len(r.hits) for r in rules)} |")
    L.append("")
    for cat, rules in cats.items():
        hits = [h for r in rules for h in r.hits]
        L.append(f"### {cat}")
        L.append("")
        L.append("Removed: " + (", ".join(f"`{h}`" for h in hits) if hits else "(none)"))
        unused = [r.raw for r in rules if not r.hits]
        if unused:
            L.append("")
            L.append("Exclude rules with no current match (kept for future upstream changes): "
                     + ", ".join(f"`{u}`" for u in unused))
        L.append("")

    L += ["## Manual includes", ""]
    L.append(", ".join(f"`{r.raw}`" for r in includes) if includes else "(none)")
    L += ["", "## Normalisation", ""]
    L += [f"- {k}: {v}" for k, v in sorted(dedupe_stats.items())] or ["- (nothing removed)"]
    L.append("")
    REPORT.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Abort as e:
        gh_annotation("error", str(e))
        log(f"ABORT: {e}")
        sys.exit(1)
