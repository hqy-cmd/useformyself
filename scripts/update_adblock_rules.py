#!/usr/bin/env python3
"""Merge upstream ad-blocking lists and app-ad modules into Surge rule sets and modules.

Standard library only. Run from the repository root:

    python3 scripts/update_adblock_rules.py [--force] [--dry-run] [--cache-dir DIR]

Outputs (see rules/README.md and modules/adblock/README.md):
    rules/Reject_Domain.list        DOMAIN-SET, core layer
    rules/Reject.list               RULE-SET, keyword / wildcard / logical / URL-REGEX / IP rules
    rules/Reject_Extra_Domain.list  DOMAIN-SET, aggressive layer (entries not already in core)
    modules/adblock/AdBlock.sgmodule, modules/adblock/AdBlock-iOS-Lite.sgmodule

Upstream snapshots live in --cache-dir (default .cache/adblock-upstream, not committed; the
workflow persists it on the `adblock-upstream-cache` branch). An upstream that fails to download
or shrinks below half its last good size falls back to its snapshot, then to rules/adblock-seed/.

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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adblock_modules as am  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "rules"
MODULES = ROOT / "modules" / "adblock"
SEED = RULES / "adblock-seed"
DEFAULT_CACHE = ROOT / ".cache" / "adblock-upstream"
DOMAIN_OUT = RULES / "Reject_Domain.list"
RULESET_OUT = RULES / "Reject.list"
EXTRA_OUT = RULES / "Reject_Extra_Domain.list"
MAC_MODULE = MODULES / "AdBlock.sgmodule"
LITE_MODULE = MODULES / "AdBlock-iOS-Lite.sgmodule"
GUARD_MODULE = MODULES / "MITM-Guard.sgmodule"
EXCLUDE_FILE = RULES / "adblock-exclude.txt"
INCLUDE_FILE = RULES / "adblock-include.txt"
GUARD_FILE = RULES / "adblock-guard.txt"
AI_DOMAIN_FILE = RULES / "AI_Domain.list"
NEVER_MITM_FILE = MODULES / "never-mitm.txt"
APPS_FILE = MODULES / "apps.txt"
STATE_FILE = RULES / "adblock-state.json"
CHANGELOG = RULES / "adblock-changelog.md"
REPORT = RULES / "adblock-report.md"
REPO_RAW = "https://raw.githubusercontent.com/hqy-cmd/useformyself/main"

LIST_UPSTREAMS = [
    {"key": "sukka-reject", "name": "Sukka reject (domainset)", "layer": "core", "format": "domainset",
     "urls": ["https://ruleset.skk.moe/List/domainset/reject.conf"]},
    {"key": "sukka-reject-non-ip", "name": "Sukka reject (non_ip)", "layer": "core", "format": "surge",
     "urls": ["https://ruleset.skk.moe/List/non_ip/reject.conf"]},
    {"key": "sukka-reject-ip", "name": "Sukka reject (ip)", "layer": "core", "format": "surge",
     "urls": ["https://ruleset.skk.moe/List/ip/reject.conf"]},
    {"key": "awavenue", "name": "AWAvenue-Ads-Rule (秋风)", "layer": "core", "format": "surge",
     "urls": ["https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main/Filters/"
              "AWAvenue-Ads-Rule-Surge-RULE-SET.list"]},
    {"key": "heidai-lite", "name": "217heidai adblockfilters lite", "layer": "core", "format": "domainset",
     "urls": ["https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblocksurgelite.list"]},
    {"key": "v2fly-ads-all", "name": "v2fly category-ads-all (MetaCubeX)", "layer": "core",
     "format": "clash-domain",
     "urls": ["https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-ads-all.list"]},
    # kelee.one and yfamilys.com sit behind Cloudflare bot checks (curl gets a challenge page; the
    # urllib client here currently passes). Mirrors: zwjtano's Script-Hub conversion of the same
    # plugin, then QingRex (the URL the Mac mini module was installed from, stale since 2026-03).
    {"key": "kelee-blockadvertisers", "name": "kelee 广告平台拦截器 [Rule]", "layer": "core",
     "format": "module-rules",
     "urls": ["https://kelee.one/Tool/Loon/Lpx/BlockAdvertisers.lpx",
              "https://raw.githubusercontent.com/zwjtano/kelee-loon-surge-modules/master/modules/"
              "BlockAdvertisers.sgmodule",
              "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/"
              "%E5%B9%BF%E5%91%8A%E5%B9%B3%E5%8F%B0%E6%8B%A6%E6%88%AA%E5%99%A8.beta.sgmodule"]},
    {"key": "sukka-reject-extra", "name": "Sukka reject_extra (domainset)", "layer": "extra",
     "format": "domainset", "urls": ["https://ruleset.skk.moe/List/domainset/reject_extra.conf"]},
    {"key": "hagezi-pro", "name": "HaGeZi Multi PRO (wildcard domains)", "layer": "extra",
     "format": "wildcard-domains",
     "urls": ["https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/pro-onlydomains.txt"]},
]

MODULE_UPSTREAMS = [
    # Only published on yfamilys.com (the GitHub copies stopped in 2023). If the Cloudflare check
    # rejects the runner, the snapshot, then rules/adblock-seed/ (the 2026-10 build) is used.
    {"key": "ddgksf2013-startingad", "name": "ddgksf2013 APP启动页去广告 (yfamilys)", "format": "module",
     "urls": ["https://yfamilys.com/module/startingad.sgmodule"],
     "seed": "ddgksf2013-startingad.sgmodule"},
    {"key": "fmz200-blockads", "name": "fmz200 wool_scripts blockAds", "format": "module",
     "urls": ["https://raw.githubusercontent.com/fmz200/wool_scripts/main/Surge/module/blockAds.module"]},
    {"key": "kelee-blockadvertisers-module", "name": "kelee 广告平台拦截器 (URL Rewrite)", "format": "module",
     "urls": ["https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/"
              "%E5%B9%BF%E5%91%8A%E5%B9%B3%E5%8F%B0%E6%8B%A6%E6%88%AA%E5%99%A8.beta.sgmodule"]},
]

AUX_UPSTREAMS = [
    {"key": "public-suffix-list", "name": "Public Suffix List", "format": "psl",
     "urls": ["https://publicsuffix.org/list/public_suffix_list.dat",
              "https://raw.githubusercontent.com/publicsuffix/list/main/public_suffix_list.dat"]},
]

MIN_UPSTREAM_RATIO = 0.5   # upstream must keep >= 50% of its last good entry count
MIN_UPSTREAM_ENTRIES = 3   # floor used when no previous count is known
MAX_OUTPUT_SHRINK = 0.30   # abort if an output shrinks by more than 30%
CHANGELOG_MAX_ITEMS = 100  # per added/removed list per output in one changelog entry
CHANGELOG_MAX_RUNS = 60
REPORT_MAX_ITEMS = 60      # hits listed per report category
LITE_MAX_SCRIPTS = 30
LITE_MAX_MITM = 100
LITE_MAX_BODY_REWRITE = 30
LITE_MAX_SCRIPTS_PER_APP = 6
MAX_RULESET_RULES = 1500

DOMAIN_RE = re.compile(r"^(?=.{1,253}$)([a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?\.)+[a-z0-9-]{2,63}$")
REJECT_POLICIES = {"REJECT", "REJECT-DROP", "REJECT-NO-DROP", "REJECT-TINYGIF", "REJECT-200"}

SURGE_TYPES = {
    "DOMAIN": "full", "HOST": "full",
    "DOMAIN-SUFFIX": "suffix", "HOST-SUFFIX": "suffix",
    "DOMAIN-KEYWORD": "keyword", "HOST-KEYWORD": "keyword",
    "DOMAIN-WILDCARD": "wildcard", "HOST-WILDCARD": "wildcard",
    "IP-CIDR": "ip", "IP-CIDR6": "ip", "IP6-CIDR": "ip",
    "URL-REGEX": "regex",
    "AND": "logical", "OR": "logical", "NOT": "logical",
}


class Abort(Exception):
    pass


def log(msg: str) -> None:
    print(msg, flush=True)


def gh_annotation(level: str, msg: str) -> None:
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::{level}::{msg}", flush=True)


# ---------------------------------------------------------------- public suffix list

class PSL:
    def __init__(self, text: str) -> None:
        self.rules: set[str] = set()
        self.wild: set[str] = set()
        self.exc: set[str] = set()
        for line in text.splitlines():
            line = line.strip().lower()
            if not line or line.startswith("//"):
                continue
            line = line.split()[0]
            try:
                line = line.encode("idna").decode("ascii") if not line.isascii() else line
            except UnicodeError:
                continue
            if line.startswith("!"):
                self.exc.add(line[1:])
            elif line.startswith("*."):
                self.wild.add(line[2:])
            else:
                self.rules.add(line)

    def count(self) -> int:
        return len(self.rules) + len(self.wild) + len(self.exc)

    def is_suffix(self, name: str) -> bool:
        if name in self.exc:
            return False
        if name in self.rules:
            return True
        parent = name.split(".", 1)[1] if "." in name else ""
        return bool(parent) and parent in self.wild

    def registrable(self, name: str) -> str | None:
        parts = name.split(".")
        for i in range(len(parts)):
            # longest matching public suffix wins; an unknown TLD counts as a suffix ("*" rule)
            if self.is_suffix(".".join(parts[i:])) or i == len(parts) - 1:
                return ".".join(parts[i - 1:]) if i > 0 else None
        return None


# ---------------------------------------------------------------- rule sets

class RuleSet:
    ATTRS = ("full", "suffix", "keyword", "wildcard", "regex", "logical", "ip")

    def __init__(self) -> None:
        for a in self.ATTRS:
            setattr(self, a, set())
        self.origin: dict[tuple[str, str], str] = {}
        self.dropped: dict[str, set[str]] = defaultdict(set)
        self.parsed_lines = 0

    def count(self) -> int:
        return sum(len(getattr(self, a)) for a in self.ATTRS)

    def domain_count(self) -> int:
        return len(self.full) + len(self.suffix)

    def update(self, other: "RuleSet") -> None:
        for a in self.ATTRS:
            getattr(self, a).update(getattr(other, a))
        for k, v in other.dropped.items():
            self.dropped[k].update(v)

    def breakdown(self) -> dict[str, int]:
        return {"DOMAIN": len(self.full), "DOMAIN-SUFFIX": len(self.suffix),
                "DOMAIN-KEYWORD": len(self.keyword), "DOMAIN-WILDCARD": len(self.wildcard),
                "URL-REGEX": len(self.regex), "AND/OR/NOT": len(self.logical), "IP-CIDR": len(self.ip)}


def norm_domain(value: str) -> str:
    return value.strip().strip("'\"").lower().rstrip(".")


def norm_ip(value: str) -> str | None:
    try:
        return str(ipaddress.ip_network(value.strip(), strict=False))
    except ValueError:
        return None


def strip_flags(s: str) -> str:
    return re.sub(r",\s*(extended-matching|pre-matching|no-resolve)\b", "", s)


def norm_logical(value: str) -> str:
    v = strip_flags(value)
    return re.sub(r"\s+", "", v)


def add_rule(rs: RuleSet, kind: str, value: str, raw: str) -> None:
    if kind in ("full", "suffix"):
        d = norm_domain(value).lstrip(".")
        if d.startswith("*."):
            d, kind = d[2:], "suffix"
        if not DOMAIN_RE.match(d):
            rs.dropped["invalid domain"].add(raw)
            return
        getattr(rs, kind).add(d)
    elif kind == "keyword":
        k = value.strip().lower()
        if k:
            rs.keyword.add(k)
    elif kind == "wildcard":
        w = value.strip().lower()
        if w:
            rs.wildcard.add(w)
    elif kind == "regex":
        r = am.unquote(value)
        try:
            re.compile(r)
        except re.error:
            rs.dropped["invalid URL-REGEX"].add(raw)
            return
        rs.regex.add(r)
    elif kind == "logical":
        rs.logical.add(value)
    elif kind == "ip":
        n = norm_ip(value)
        if n is None:
            rs.dropped["invalid IP-CIDR"].add(raw)
        else:
            rs.ip.add(n)


def parse_rule_line(line: str, rs: RuleSet, policy_required: bool) -> None:
    parts = [p.strip() for p in am.split_top(line)]
    rtype = parts[0].upper()
    kind = SURGE_TYPES.get(rtype)
    if kind is None or len(parts) < 2:
        rs.dropped[rtype or "unknown"].add(line)
        return
    rest = [p for p in parts[2:] if p.lower() not in ("extended-matching", "pre-matching", "no-resolve")]
    policy = rest[0].upper() if rest else ""
    if policy_required and policy not in REJECT_POLICIES:
        rs.dropped[f"non-reject policy ({policy or 'none'})"].add(line)
        return
    if kind == "logical":
        add_rule(rs, kind, f"{rtype},{norm_logical(parts[1])}", line)
    else:
        add_rule(rs, kind, parts[1], line)


def parse_surge(text: str, rs: RuleSet, policy_required: bool = False) -> None:
    for line in text.splitlines():
        line = line.strip()
        if not line or line[0] in "#;!" or line.startswith("//") or line.startswith("["):
            continue
        rs.parsed_lines += 1
        if "," not in line:
            if line.startswith("+."):
                add_rule(rs, "suffix", line[2:], line)
            elif line.startswith("."):
                add_rule(rs, "suffix", line[1:], line)
            else:
                add_rule(rs, "full", line, line)
            continue
        parse_rule_line(line, rs, policy_required)


def parse_clash_domain(text: str, rs: RuleSet) -> None:
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
        elif "*" in line or ":" in line:
            rs.dropped["wildcard/regex (domain text)"].add(line)
        else:
            add_rule(rs, "full", line, line)


def parse_wildcard_domains(text: str, rs: RuleSet) -> None:
    """HaGeZi `wildcard/*-onlydomains.txt`: every entry also covers its subdomains."""
    for line in text.splitlines():
        line = line.strip()
        if not line or line[0] in "#!;":
            continue
        rs.parsed_lines += 1
        add_rule(rs, "suffix", line.lstrip("*").lstrip("."), line)


def parse_list(fmt: str, text: str) -> RuleSet:
    rs = RuleSet()
    if fmt == "domainset" or fmt == "surge":
        parse_surge(text, rs)
    elif fmt == "clash-domain":
        parse_clash_domain(text, rs)
    elif fmt == "wildcard-domains":
        parse_wildcard_domains(text, rs)
    elif fmt == "module-rules":
        parse_surge("\n".join(am.module_rule_lines(text)), rs, policy_required=True)
    else:
        raise ValueError(fmt)
    return rs


# ---------------------------------------------------------------- matching helpers

def parents(domain: str):
    parts = domain.split(".")
    for i in range(len(parts)):
        yield ".".join(parts[i:])


def keyword_hits_tree(k: str, s: str) -> bool:
    """Does keyword `k` deliberately target names under suffix `s` (or `s` itself)?"""
    if k in s or s in k:
        return True
    labels = s.split(".")
    for i in range(1, len(labels)):
        prefix = ".".join(labels[:i]) + "."
        if k.endswith(prefix):
            before = k[: -len(prefix)]
            if before == "" or before.endswith("."):
                return True
    return False


def wildcard_hits_tree(pattern: str, s: str) -> bool:
    """Can the Surge wildcard match `s` or any name ending in `.s`?"""
    if fnmatch.fnmatchcase(s, pattern):
        return True
    p, t = pattern, "." + s
    memo: dict[tuple[int, int], bool] = {}

    def rec(i: int, j: int) -> bool:
        # match p[:i] (right-to-left) against a string ending with t[:j]... consumed from right
        key = (i, j)
        if key in memo:
            return memo[key]
        if j == 0:
            res = True
        elif i == 0:
            res = False
        else:
            c = p[i - 1]
            if c == "*":
                res = rec(i - 1, j) or rec(i, j - 1)
            elif c == "?":
                res = rec(i - 1, j - 1)
            elif c == "]" and "[" in p[:i]:
                start = p.rfind("[", 0, i)
                cls = p[start:i]
                res = fnmatch.fnmatchcase(t[j - 1], cls) and rec(start, j - 1)
            else:
                res = c == t[j - 1] and rec(i - 1, j - 1)
        memo[key] = res
        return res

    return rec(len(p), len(t))


def logical_eval_host(rule: str, host: str) -> bool:
    """Evaluate an AND/OR/NOT rule for a hostname; non-domain sub-rules are treated as true."""
    rtype, _, body = rule.partition(",")
    rtype = rtype.upper()
    if rtype in ("AND", "OR", "NOT"):
        inner = body.strip()
        if inner.startswith("(") and inner.endswith(")"):
            inner = inner[1:-1]
        subs = [s.strip() for s in am.split_top(inner)]
        subs = [s[1:-1] if s.startswith("(") and s.endswith(")") else s for s in subs]
        vals = [logical_eval_host(s, host) for s in subs if s]
        if rtype == "AND":
            return all(vals)
        if rtype == "OR":
            return any(vals)
        return True
    value = am.split_top(body)[0].strip().lower()
    if rtype in ("DOMAIN", "HOST"):
        return host == value
    if rtype in ("DOMAIN-SUFFIX", "HOST-SUFFIX"):
        return host == value or host.endswith("." + value)
    if rtype in ("DOMAIN-KEYWORD", "HOST-KEYWORD"):
        return value in host
    if rtype in ("DOMAIN-WILDCARD",):
        return fnmatch.fnmatchcase(host, value)
    return True


def logical_hits_tree(rule: str, s: str) -> bool:
    return _logical_tree(rule, s) is True


def _logical_tree(rule: str, s: str) -> bool | None:
    """True = deliberately targets the tree, False = cannot match it, None = generic condition."""
    rtype, _, body = rule.partition(",")
    rtype = rtype.upper()
    if rtype in ("AND", "OR", "NOT"):
        inner = body.strip()
        if inner.startswith("(") and inner.endswith(")"):
            inner = inner[1:-1]
        subs = [x.strip() for x in am.split_top(inner)]
        subs = [x[1:-1] if x.startswith("(") and x.endswith(")") else x for x in subs]
        vals = [_logical_tree(x, s) for x in subs if x]
        if rtype == "AND":
            return False if False in vals else (True if True in vals else None)
        if rtype == "OR":
            return True if True in vals else (None if None in vals else False)
        return None
    value = am.split_top(body)[0].strip().lower()
    if rtype in ("DOMAIN", "HOST"):
        return value == s or value.endswith("." + s)
    if rtype in ("DOMAIN-SUFFIX", "HOST-SUFFIX"):
        return value == s or value.endswith("." + s) or s.endswith("." + value)
    if rtype in ("DOMAIN-KEYWORD", "HOST-KEYWORD"):
        return True if keyword_hits_tree(value, s) else None
    if rtype == "DOMAIN-WILDCARD":
        return wildcard_hits_tree(value, s)
    return None


def regex_hits_host(r: str, host: str) -> bool:
    try:
        return any(re.search(r, f"{scheme}://{host}/") for scheme in ("http", "https"))
    except re.error:
        return False


# ---------------------------------------------------------------- protect rules (exclude / guard)

class Rule:
    def __init__(self, category: str, rtype: str, value: str, raw: str) -> None:
        self.category = category
        self.rtype = rtype
        self.value = value
        self.raw = raw
        self.hits: list[str] = []


def parse_rule_file(path: Path, allow: tuple[str, ...]) -> list[Rule]:
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
            rtype = rtype.upper()
            if rtype not in ("URL-REGEX", "AND", "OR", "NOT"):
                value = value.split(",", 1)[0].strip()
        elif line.startswith("."):
            rtype, value = "DOMAIN-SUFFIX", line[1:]
        else:
            rtype, value = "DOMAIN", line
        rtype = {"HOST": "DOMAIN", "HOST-SUFFIX": "DOMAIN-SUFFIX", "HOST-KEYWORD": "DOMAIN-KEYWORD",
                 "IP6-CIDR": "IP-CIDR6", "HOST-WILDCARD": "DOMAIN-WILDCARD"}.get(rtype, rtype)
        if rtype not in allow:
            raise Abort(f"{path.name}:{n}: unsupported rule type {rtype!r}")
        if rtype in ("DOMAIN", "DOMAIN-SUFFIX"):
            value = norm_domain(value).lstrip(".")
            if not DOMAIN_RE.match(value):
                raise Abort(f"{path.name}:{n}: invalid domain {value!r}")
        elif rtype in ("DOMAIN-KEYWORD", "DOMAIN-WILDCARD"):
            value = value.lower()
        elif rtype in ("IP-CIDR", "IP-CIDR6"):
            n_ = norm_ip(value)
            if n_ is None:
                raise Abort(f"{path.name}:{n}: invalid CIDR {value!r}")
            value = n_
        elif rtype == "URL-REGEX":
            value = am.unquote(strip_flags(value).rsplit(",REJECT", 1)[0])
            try:
                re.compile(value)
            except re.error as e:
                raise Abort(f"{path.name}:{n}: invalid URL-REGEX ({e})") from e
        elif rtype in ("AND", "OR", "NOT"):
            body = norm_logical(value)
            body = re.sub(r",(REJECT[-A-Z0-9]*)$", "", body)
            value = f"{rtype},{body}"
        rules.append(Rule(category, rtype, value, line))
    return rules


class Protector:
    """Removes entries that would block protected names; also used as the final guard."""

    def __init__(self, rules: list[Rule]) -> None:
        self.rules = rules
        self.hosts: dict[str, Rule] = {}
        self.trees: dict[str, Rule] = {}
        for r in rules:
            if r.rtype == "DOMAIN":
                self.hosts.setdefault(r.value, r)
            elif r.rtype == "DOMAIN-SUFFIX":
                self.trees.setdefault(r.value, r)
        self.host_parents: dict[str, Rule] = {}
        for h, r in self.hosts.items():
            for p in parents(h):
                self.host_parents.setdefault(p, r)
        self.tree_parents: dict[str, Rule] = {}
        for s, r in self.trees.items():
            for p in parents(s):
                self.tree_parents.setdefault(p, r)
        self.keywords = {r.value: r for r in rules if r.rtype == "DOMAIN-KEYWORD"}
        self.wildcards = [r for r in rules if r.rtype == "DOMAIN-WILDCARD"]
        self.regexes = {r.value: r for r in rules if r.rtype == "URL-REGEX"}
        self.logicals = {r.value: r for r in rules if r.rtype in ("AND", "OR", "NOT")}
        self.cidrs = [r for r in rules if r.rtype in ("IP-CIDR", "IP-CIDR6")]

    def domain_rule(self, name: str, is_suffix: bool) -> Rule | None:
        if name in self.hosts:
            return self.hosts[name]
        if is_suffix and name in self.host_parents:
            return self.host_parents[name]
        for p in parents(name):
            if p in self.trees:
                return self.trees[p]
        if is_suffix and name in self.tree_parents:
            return self.tree_parents[name]
        for w in self.wildcards:
            if fnmatch.fnmatchcase(name, w.value):
                return w
            tail = re.split(r"[*?\]]", w.value)[-1]
            if is_suffix and tail.startswith(".") and (tail == "." + name or tail.endswith("." + name)):
                return w
        return None

    def keyword_rule(self, k: str) -> Rule | None:
        if k in self.keywords:
            return self.keywords[k]
        for h, r in self.hosts.items():
            if k in h:
                return r
        for s, r in self.trees.items():
            if keyword_hits_tree(k, s):
                return r
        return None

    def wildcard_rule(self, w: str) -> Rule | None:
        for r in self.wildcards:
            if r.value == w:
                return r
        for h, r in self.hosts.items():
            if fnmatch.fnmatchcase(h, w):
                return r
        for s, r in self.trees.items():
            if wildcard_hits_tree(w, s):
                return r
        return None

    def logical_rule(self, rule: str) -> Rule | None:
        if rule in self.logicals:
            return self.logicals[rule]
        for h, r in self.hosts.items():
            if logical_eval_host(rule, h):
                return r
        for s, r in self.trees.items():
            if logical_hits_tree(rule, s):
                return r
        return None

    def regex_rule(self, rx: str) -> Rule | None:
        if rx in self.regexes:
            return self.regexes[rx]
        for h, r in self.hosts.items():
            if regex_hits_host(rx, h):
                return r
        for s, r in self.trees.items():
            if regex_hits_host(rx, s) or regex_hits_host(rx, "www." + s):
                return r
        return None

    def ip_rule(self, cidr: str) -> Rule | None:
        net = ipaddress.ip_network(cidr)
        for r in self.cidrs:
            o = ipaddress.ip_network(r.value)
            if o.version == net.version and (net.subnet_of(o) or o.subnet_of(net)):
                return r
        return None

    def apply(self, rs: RuleSet, record: bool = True) -> list[tuple[Rule, str]]:
        """Remove protected entries from `rs`; return (rule, removed entry) pairs."""
        hits: list[tuple[Rule, str]] = []

        def hit(r: Rule, entry: str) -> None:
            hits.append((r, entry))
            if record:
                r.hits.append(entry)

        for name in sorted(rs.full):
            r = self.domain_rule(name, False)
            if r:
                rs.full.discard(name)
                hit(r, name)
        for name in sorted(rs.suffix):
            r = self.domain_rule(name, True)
            if r:
                rs.suffix.discard(name)
                hit(r, "." + name)
        for k in sorted(rs.keyword):
            r = self.keyword_rule(k)
            if r:
                rs.keyword.discard(k)
                hit(r, f"DOMAIN-KEYWORD,{k}")
        for w in sorted(rs.wildcard):
            r = self.wildcard_rule(w)
            if r:
                rs.wildcard.discard(w)
                hit(r, f"DOMAIN-WILDCARD,{w}")
        for lg in sorted(rs.logical):
            r = self.logical_rule(lg)
            if r:
                rs.logical.discard(lg)
                hit(r, lg)
        for rx in sorted(rs.regex):
            r = self.regex_rule(rx)
            if r:
                rs.regex.discard(rx)
                hit(r, f"URL-REGEX,{rx}")
        for c in sorted(rs.ip):
            r = self.ip_rule(c)
            if r:
                rs.ip.discard(c)
                hit(r, f"IP-CIDR,{c}")
        return hits


def ai_protect_rules() -> list[Rule]:
    rules = []
    if not AI_DOMAIN_FILE.exists():
        return rules
    for line in AI_DOMAIN_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("."):
            rules.append(Rule("AI group (rules/AI_Domain.list)", "DOMAIN-SUFFIX", line[1:], line))
        else:
            rules.append(Rule("AI group (rules/AI_Domain.list)", "DOMAIN", line, line))
    return rules


def apply_includes(rs: RuleSet, rules: list[Rule]) -> None:
    kinds = {"DOMAIN": "full", "DOMAIN-SUFFIX": "suffix", "DOMAIN-KEYWORD": "keyword",
             "DOMAIN-WILDCARD": "wildcard", "URL-REGEX": "regex", "IP-CIDR": "ip", "IP-CIDR6": "ip",
             "AND": "logical", "OR": "logical", "NOT": "logical"}
    for r in rules:
        getattr(rs, kinds[r.rtype]).add(r.value)
        r.hits.append(r.raw)


# ---------------------------------------------------------------- normalisation

def drop_public_suffixes(rs: RuleSet, psl: PSL) -> list[str]:
    removed = []
    for attr, prefix in (("full", ""), ("suffix", ".")):
        for name in list(getattr(rs, attr)):
            if psl.is_suffix(name):
                getattr(rs, attr).discard(name)
                removed.append(prefix + name)
    return sorted(removed)


def dedupe(rs: RuleSet) -> dict[str, int]:
    removed: dict[str, int] = defaultdict(int)

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


def subtract_core(extra: RuleSet, core: RuleSet) -> int:
    n = 0

    def covered(name: str) -> bool:
        if name in core.full:
            return True
        return any(p in core.suffix for p in parents(name))

    for name in list(extra.full):
        if covered(name):
            extra.full.discard(name)
            n += 1
    for name in list(extra.suffix):
        if any(p in core.suffix for p in parents(name)):
            extra.suffix.discard(name)
            n += 1
    return n


def domain_lines(rs: RuleSet) -> list[str]:
    entries = [(n, "." + n) for n in rs.suffix] + [(n, n) for n in rs.full]
    return [line for _, line in sorted(entries, key=lambda e: (e[0].split(".")[::-1], e[1]))]


def format_regex(r: str) -> str:
    return f'URL-REGEX,"{r}"' if "," in r or " " in r else f"URL-REGEX,{r}"


def ruleset_lines(rs: RuleSet) -> list[str]:
    out = [f"DOMAIN-KEYWORD,{k}" for k in sorted(rs.keyword)]
    out += [f"DOMAIN-WILDCARD,{w}" for w in sorted(rs.wildcard)]
    out += sorted(rs.logical)
    out += [format_regex(r) for r in sorted(rs.regex)]
    nets = sorted((ipaddress.ip_network(c) for c in rs.ip), key=lambda n: (n.version, n))
    for n in nets:
        out.append(f"{'IP-CIDR' if n.version == 4 else 'IP-CIDR6'},{n},no-resolve")
    return out


# ---------------------------------------------------------------- io helpers

def fetch(url: str, attempts: int = 3) -> str:
    last: Exception | None = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Surge Mac/2994 adblock-rules-merger/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                text = resp.read().decode("utf-8", errors="replace")
            head = text.lstrip()[:200].lower()
            if head.startswith("<!doctype html") or head.startswith("<html"):
                raise RuntimeError("got an HTML page (challenge or error page), not a list")
            return text
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (403, 404, 410):
                break
        except (urllib.error.URLError, TimeoutError, ConnectionError, RuntimeError) as e:
            last = e
            if isinstance(e, RuntimeError):
                break
        if i < attempts - 1:
            time.sleep(2 ** (i + 2))
    raise RuntimeError(f"download failed: {last}")


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


def count_for(up: dict, text: str) -> int:
    fmt = up["format"]
    if fmt == "psl":
        return PSL(text).count()
    if fmt == "module":
        return sum(1 for s, _, _ in am.iter_sections(text) if s in am.EMITTED_SECTIONS)
    return parse_list(fmt, text).count()


def get_upstream(up: dict, cache: Path, prev: dict, stamp: str, warnings: list[str]) -> tuple[str, dict]:
    """Fetch with per-upstream fallback: fresh -> cache-dir snapshot -> committed seed."""
    name = up["name"]
    prev_count = prev.get("count")
    status = {"key": up["key"], "name": name, "url": up["urls"][0], "source": "fresh"}
    problems = []
    text = None
    for url in up["urls"]:
        try:
            t = fetch(url)
            n = count_for(up, t)
            floor = max(MIN_UPSTREAM_ENTRIES, int((prev_count or 0) * MIN_UPSTREAM_RATIO))
            if n < floor:
                raise RuntimeError(f"parsed only {n} entries (previous good: {prev_count}, floor {floor})")
            text = t
            status["url"] = url
            if url != up["urls"][0]:
                status["source"] = "fresh (mirror)"
            break
        except Exception as e:  # noqa: BLE001
            problems.append(f"{url}: {e}")
    snap = cache / f"{up['key']}.txt"
    if text is None:
        msg = f"{name}: " + "; ".join(problems)
        if snap.exists():
            text = snap.read_text(encoding="utf-8")
            status["source"] = f"cached snapshot ({prev.get('fetched_at', 'unknown date')})"
            status["fetched_at"] = prev.get("fetched_at")
        elif up.get("seed") and (SEED / up["seed"]).exists():
            text = (SEED / up["seed"]).read_text(encoding="utf-8")
            status["source"] = f"committed seed (rules/adblock-seed/{up['seed']})"
            status["fetched_at"] = prev.get("fetched_at") or "seed"
        else:
            raise Abort(msg + "; no snapshot available")
        msg += f"; using {status['source']}"
        warnings.append(msg)
        gh_annotation("warning", msg)
        log("WARN " + msg)
        status["fresh_text"] = None
    else:
        status["fresh_text"] = text
        status["fetched_at"] = prev.get("fetched_at") if prev.get("sha256") == sha256(text) else stamp
    status["sha256"] = sha256(text)
    status["count"] = count_for(up, text)
    return text, status


def read_never_mitm_file(sections: tuple[str, ...] = ("guard", "adblock-only")) -> list[str]:
    out = []
    section = "guard"
    if NEVER_MITM_FILE.exists():
        for line in NEVER_MITM_FILE.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip().lower()
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1]
                continue
            if section not in sections or not line:
                continue
            if line.startswith("."):
                out += [line[1:], "*" + line]
            else:
                out.append(line)
    return out


def read_never_mitm() -> list[str]:
    out = read_never_mitm_file()
    for line in read_body(AI_DOMAIN_FILE):
        if line.startswith("."):
            out += [line[1:], "*." + line[1:]]
        else:
            out.append(line)
    return out


def read_apps_block(block: str) -> list[tuple[str, list[str]]]:
    """`name: suffix, suffix` lines from one `[block]` of modules/adblock/apps.txt."""
    out, on = [], False
    if APPS_FILE.exists():
        for line in APPS_FILE.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.startswith("[") and s.endswith("]"):
                on = s == f"[{block}]"
                continue
            s = s.split("#", 1)[0].strip()
            if on and ":" in s:
                name, _, doms = s.partition(":")
                out.append((name.strip(), [d.strip().lower() for d in doms.split(",") if d.strip()]))
    return out


def read_delegated() -> list[tuple[str, list[str]]]:
    return read_apps_block("delegated")


def read_lite_apps() -> list[tuple[str, list[str]]]:
    return read_apps_block("lite")


# ---------------------------------------------------------------- module pipeline

def build_modules(mod_texts: dict[str, str], mod_status: dict[str, dict], psl: PSL, guard: Protector,
                  never: list[str]) -> dict:
    """Return dict with per-source entries, host-wide reject domains, variants and drop stats."""
    dropped: dict[str, list[str]] = defaultdict(list)
    per_source: dict[str, list[am.Entry]] = {}
    for key, text in mod_texts.items():
        entries, _, dr = am.build_entries(key, text, psl)
        per_source[key] = entries
        for k, v in dr.items():
            dropped[f"{key}: {k}"] += v

    # Host-wide rejects become DOMAIN-SET entries instead of module lines.
    hostwide = RuleSet()
    for key, entries in per_source.items():
        keep = []
        for e in entries:
            d = am.host_wide_reject_domain(e)
            if d:
                (hostwide.suffix if d[1] else hostwide.full).add(d[0])
                hostwide.origin[(d[0], "s" if d[1] else "f")] = key
            else:
                keep.append(e)
        per_source[key] = keep

    delegated = read_delegated()
    merged: list[am.Entry] = []
    seen_patterns: set[tuple[str, str]] = set()
    # Two sources' scripts / body rewrites on one host would rewrite the same responses twice,
    # so body processors of a host come from the first source that has any.
    claimed_hosts: set[str] = set()
    for key in mod_texts:  # source order = precedence
        hosts_here: set[str] = set()
        for e in per_source[key]:
            deleg = next((n for n, sfx in delegated if am.matches_suffixes(e, sfx)), None)
            if deleg:
                dropped[f"{key}: delegated to dedicated module ({deleg})"].append(e.pattern)
                continue
            is_body = e.section in ("Script", "Body Rewrite")
            if is_body and any(h in claimed_hosts for h in e.hosts):
                dropped[f"{key}: body processor on a host already scripted by a higher-precedence source"
                        ].append(e.pattern)
                continue
            if (e.section, e.pattern) in seen_patterns:
                dropped[f"{key}: duplicate pattern"].append(e.pattern)
                continue
            bad = next(((h, am.mitm_blocked(h, never)) for h in sorted(e.mitm) if am.mitm_blocked(h, never)), None)
            if bad:
                dropped[f"{key}: never-MITM host {bad[0]} (matches {bad[1]})"].append(e.pattern)
                continue
            if e.section == "URL Rewrite" and e.line.endswith(" - reject"):
                hit = next((h for h in list(guard.hosts) + list(guard.trees)
                            if any(am.globs_overlap(g, h) for g in e.hosts) and regex_hits_host(e.pattern, h)),
                           None)
                if hit:
                    dropped[f"{key}: reject would hit must-not-block host {hit}"].append(e.pattern)
                    continue
            seen_patterns.add((e.section, e.pattern))
            if is_body:
                hosts_here.update(e.hosts)
            merged.append(e)
        claimed_hosts |= hosts_here

    mac = am.select_mac(merged)
    lite = am.select_lite(merged, read_lite_apps(), LITE_MAX_SCRIPTS, LITE_MAX_MITM, LITE_MAX_BODY_REWRITE,
                          LITE_MAX_SCRIPTS_PER_APP)
    return {"hostwide": hostwide, "mac": mac, "lite": lite, "dropped": dropped, "merged": merged}


def module_guard(variants: list[am.Variant], never: list[str]) -> None:
    for v in variants:
        for h in v.mitm:
            hit = am.mitm_blocked(h, never)
            if hit:
                raise Abort(f"GUARD: {v.name} module would MITM {h} (never-MITM {hit})")
        for e in v.entries:
            if e.section == "Script" and re.search(r"script-path=\"?https?://(?!(%s)/)" % "|".join(
                    re.escape(x) for x in am.SCRIPT_HOST_ALLOW), e.line):
                raise Abort(f"GUARD: {v.name} script outside allowed hosts: {e.line[:120]}")
    lite = next(v for v in variants if v.name == "iOS Lite")
    n_scripts = sum(1 for e in lite.entries if e.section == "Script")
    if n_scripts > LITE_MAX_SCRIPTS or len(lite.mitm) > LITE_MAX_MITM:
        raise Abort(f"GUARD: iOS Lite over budget ({n_scripts} scripts, {len(lite.mitm)} MITM hosts)")


def module_header(variant: am.Variant, stamp: str, mod_status: dict[str, dict], desc: str, name: str,
                  url: str) -> list[str]:
    counts = am.count_sections(variant.entries)
    n_body = sum(1 for e in variant.entries if e.body)
    lines = [
        f"#!name={name}",
        f"#!desc={desc}",
        "#!author=hqy-cmd (generated from ddgksf2013 / fmz200 / kelee upstream modules)",
        "#!homepage=https://github.com/hqy-cmd/useformyself/tree/main/modules/adblock",
        f"# Install URL: {url}",
        "#!category=AdBlock",
        f"# Generated: {stamp} by scripts/update_adblock_rules.py - do not edit by hand.",
        "# Domain rejects are NOT in this module (module [Rule] lines run before profile rules);",
        "# use rules/Reject_Domain.list + rules/Reject.list in the profile. Needs MITM enabled.",
        f"# Sections: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
        + f"; body-buffering entries {n_body}; MITM hosts {len(variant.mitm)}",
        "# Upstreams:",
    ]
    for s in mod_status.values():
        lines.append(f"#   - {s['name']} [{s['source']}] {s['url']}")
    lines.append("# Apps: " + ", ".join(a.split(" (partial")[0] for a in variant.apps[:400]))
    return lines


def guard_module_text(stamp: str) -> str:
    hosts = ["-" + h for h in read_never_mitm_file(("guard",))]
    return "\n".join([
        "#!name=MITM Guard (never decrypt bank / payment / App Store purchase hosts)",
        "#!desc=Puts exclusions at the FRONT of the MITM hostname list with %INSERT%, so no other "
        "module (e.g. App unlock collections) can decrypt these hosts. Generated; optional.",
        "#!author=hqy-cmd",
        "#!category=AdBlock",
        f"# Generated: {stamp} from the [guard] section of modules/adblock/never-mitm.txt",
        "",
        "[MITM]",
        "hostname = %INSERT% " + ", ".join(hosts),
        "",
    ])


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="skip shrink safety checks")
    ap.add_argument("--dry-run", action="store_true", help="do not write any files")
    ap.add_argument("--cache-dir", default=str(DEFAULT_CACHE), help="upstream snapshot directory")
    args = ap.parse_args()
    cache = Path(args.cache_dir)

    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    stamp = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    state = load_state()
    prev_up = state.get("upstreams", {})
    warnings: list[str] = []
    statuses: list[dict] = []

    # Public suffix list first: needed for module grouping and eTLD filtering.
    texts: dict[str, str] = {}
    for up in AUX_UPSTREAMS + MODULE_UPSTREAMS + LIST_UPSTREAMS:
        text, st = get_upstream(up, cache, prev_up.get(up["key"], {}), stamp, warnings)
        st["kind"] = "aux" if up in AUX_UPSTREAMS else ("module" if up in MODULE_UPSTREAMS else up["layer"])
        texts[up["key"]] = text
        statuses.append(st)
        log(f"{up['name']}: {st['count']} entries [{st['source']}]")
    status_by_key = {s["key"]: s for s in statuses}
    psl = PSL(texts["public-suffix-list"])

    # Protection rules: exclude file, AI group, must-not-block guard.
    allow_ex = ("DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-WILDCARD", "URL-REGEX", "AND", "OR",
                "NOT", "IP-CIDR", "IP-CIDR6")
    excludes = parse_rule_file(EXCLUDE_FILE, allow_ex)
    includes = parse_rule_file(INCLUDE_FILE, allow_ex)
    guard_rules = parse_rule_file(GUARD_FILE, ("DOMAIN", "DOMAIN-SUFFIX"))
    for r in guard_rules:
        r.category = f"must-not-block: {r.category}"
    ai_rules = ai_protect_rules()
    exclude_p = Protector(excludes)
    ai_p = Protector(ai_rules)
    guard_p = Protector(guard_rules)
    never = read_never_mitm()

    # Modules (also yields host-wide reject domains for the core DOMAIN-SET).
    mod_keys = [u["key"] for u in MODULE_UPSTREAMS]
    mod_texts = {k: texts[k] for k in mod_keys}
    mods = build_modules(mod_texts, {k: status_by_key[k] for k in mod_keys}, psl, guard_p, never)

    # Lists.
    layers = {"core": RuleSet(), "extra": RuleSet()}
    for up in LIST_UPSTREAMS:
        rs = parse_list(up["format"], texts[up["key"]])
        st = status_by_key[up["key"]]
        st["breakdown"] = rs.breakdown()
        st["dropped"] = {k: sorted(v) for k, v in rs.dropped.items()}
        layers[up["layer"]].update(rs)
    hw = mods["hostwide"]
    layers["core"].update(hw)
    raw_counts = {k: v.count() for k, v in layers.items()}

    psl_dropped = {k: drop_public_suffixes(v, psl) for k, v in layers.items()}
    removed: dict[str, dict[str, list[str]]] = {"exclude": defaultdict(list), "ai": defaultdict(list),
                                                "guard": defaultdict(list)}
    for lname, rs in layers.items():
        for label, prot in (("exclude", exclude_p), ("ai", ai_p), ("guard", guard_p)):
            for r, entry in prot.apply(rs):
                removed[label][r.category].append(f"{entry} [{lname}]")
    core, extra = layers["core"], layers["extra"]
    # Extra layer is domain-only; non-domain rules from extra upstreams are not carried.
    for a in ("keyword", "wildcard", "regex", "logical", "ip"):
        getattr(extra, a).clear()
    apply_includes(core, includes)
    dedupe_stats = {"core": dedupe(core), "extra": dedupe(extra)}
    in_core = subtract_core(extra, core)

    # Final guard: nothing in any output may match a must-not-block name or the AI group.
    for lname, rs in layers.items():
        for prot, what in ((guard_p, "must-not-block"), (ai_p, "AI_Domain.list")):
            probe = RuleSet()
            probe.update(rs)
            hits = prot.apply(probe, record=False)
            if hits:
                r, entry = hits[0]
                raise Abort(f"GUARD: {lname} output would block {what} entry {r.raw!r} via {entry!r} "
                            f"({len(hits)} hits; check adblock-include.txt)")
    module_guard([mods["mac"], mods["lite"]], never)

    new = {
        "Reject_Domain.list": domain_lines(core),
        "Reject.list": ruleset_lines(core),
        "Reject_Extra_Domain.list": domain_lines(extra),
    }
    if len(new["Reject.list"]) > MAX_RULESET_RULES:
        msg = f"Reject.list has {len(new['Reject.list'])} rules (> {MAX_RULESET_RULES}); review upstream growth"
        warnings.append(msg)
        gh_annotation("warning", msg)
    mod_header_common = {k: status_by_key[k] for k in mod_keys}
    mac_text = am.render(mods["mac"], module_header(
        mods["mac"], stamp, mod_header_common,
        "Splash / in-app ad removal for Mac (URL Rewrite, Map Local, Body/Header Rewrite, Scripts). "
        "Generated from ddgksf2013, fmz200 and kelee modules; bank/payment/Apple/AI hosts never decrypted.",
        "AdBlock (Mac)", f"{REPO_RAW}/modules/adblock/AdBlock.sgmodule"))
    lite_text = am.render(mods["lite"], module_header(
        mods["lite"], stamp, mod_header_common,
        f"iPhone budget version: <= {LITE_MAX_SCRIPTS} scripts, <= {LITE_MAX_MITM} MITM hosts, "
        "non-body scripts preferred. Same sources as the Mac module, limited to modules/adblock/apps.txt [lite].",
        "AdBlock (iOS Lite)", f"{REPO_RAW}/modules/adblock/AdBlock-iOS-Lite.sgmodule"))
    new_modules = {"AdBlock.sgmodule": mac_text, "AdBlock-iOS-Lite.sgmodule": lite_text,
                   "MITM-Guard.sgmodule": guard_module_text(stamp)}
    for k, text in new_modules.items():
        problems = am.lint_module(text)
        if problems:
            n, why, line = problems[0]
            raise Abort(f"LINT: {k} line {n}: {why}: {line[:160]} ({len(problems)} problems)")
    paths = {"Reject_Domain.list": DOMAIN_OUT, "Reject.list": RULESET_OUT,
             "Reject_Extra_Domain.list": EXTRA_OUT, "AdBlock.sgmodule": MAC_MODULE,
             "AdBlock-iOS-Lite.sgmodule": LITE_MODULE, "MITM-Guard.sgmodule": GUARD_MODULE}

    def module_body(text: str) -> list[str]:
        return [l for l in text.splitlines() if l.strip() and not l.startswith("#")]

    old = {k: read_body(p) for k, p in paths.items() if k in new}
    old.update({k: module_body(p.read_text(encoding="utf-8")) if p.exists() else []
                for k, p in paths.items() if k in new_modules})
    new_bodies = dict(new)
    new_bodies.update({k: module_body(v) for k, v in new_modules.items()})

    for k, lines in new_bodies.items():
        o = len(old[k])
        if o and len(lines) < o * (1 - MAX_OUTPUT_SHRINK) and not args.force:
            raise Abort(f"{k} would shrink from {o} to {len(lines)} lines "
                        f"(>{int(MAX_OUTPUT_SHRINK * 100)}%); refusing to publish (re-run with --force)")
    if not new["Reject_Domain.list"]:
        raise Abort("Reject_Domain.list output is empty")

    diffs = {k: (sorted(set(new_bodies[k]) - set(old[k])), sorted(set(old[k]) - set(new_bodies[k])))
             for k in new_bodies}
    changed = any(new_bodies[k] != old[k] for k in new_bodies)
    snapshots_changed = any(s.get("fresh_text") is not None and
                            not ((cache / f"{s['key']}.txt").exists() and
                                 sha256((cache / f"{s['key']}.txt").read_text(encoding="utf-8")) == s["sha256"])
                            for s in statuses)
    summary = ("AdBlock rules: " + ", ".join(f"{k.split('.')[0]} {len(new_bodies[k])} "
                                             f"(+{len(diffs[k][0])}/-{len(diffs[k][1])})" for k in new_bodies))
    log(summary)

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"changed={'true' if changed else 'false'}\n")
            f.write(f"snapshots_changed={'true' if snapshots_changed and not args.dry_run else 'false'}\n")
            f.write(f"commit_message={summary}\n")

    if args.dry_run:
        log("Dry run; nothing written.")
        return 0

    cache.mkdir(parents=True, exist_ok=True)
    for s in statuses:
        if s.get("fresh_text") is not None:
            (cache / f"{s['key']}.txt").write_text(s["fresh_text"], encoding="utf-8")
    if not changed:
        log("Outputs unchanged; nothing written.")
        return 0

    list_status = [s for s in statuses if s["kind"] in ("core", "extra")]
    up_header = [f"#   - {s['name']}: {s['count']} entries [{s['source']}]\n#     {s['url']}"
                 for s in list_status]
    total_excl = sum(len(v) for d in removed.values() for v in d.values())

    def header(title: str, desc: str, layer: str) -> str:
        return "\n".join([
            f"# {title}",
            f"# Generated: {stamp}",
            f"# {desc}",
            "# Upstreams:",
            *[h for s, h in zip(list_status, up_header) if s["kind"] == layer],
            *([f"#   - module host-wide rejects (ddgksf2013 / fmz200 / kelee): {hw.domain_count()} entries"]
              if layer == "core" else []),
            f"# Protected / excluded entries removed this run: {total_excl} (see rules/adblock-report.md)",
            "# Source: https://github.com/hqy-cmd/useformyself/tree/main/rules",
            "",
        ])

    RULES.mkdir(exist_ok=True)
    MODULES.mkdir(parents=True, exist_ok=True)
    DOMAIN_OUT.write_text(header(
        "Reject_Domain.list - Surge DOMAIN-SET (ad-block core layer)",
        f"Entries: {len(new['Reject_Domain.list'])} ({len(core.suffix)} suffix '.x', {len(core.full)} exact)",
        "core") + "\n".join(new["Reject_Domain.list"]) + "\n", encoding="utf-8")
    RULESET_OUT.write_text(header(
        "Reject.list - Surge RULE-SET (ad-block keyword / wildcard / logical / URL-REGEX / IP rules)",
        f"Rules: {len(new['Reject.list'])} (DOMAIN-KEYWORD {len(core.keyword)}, DOMAIN-WILDCARD "
        f"{len(core.wildcard)}, AND/OR {len(core.logical)}, URL-REGEX {len(core.regex)}, "
        f"IP-CIDR/IP-CIDR6 {len(core.ip)})", "core") + "\n".join(new["Reject.list"]) + "\n", encoding="utf-8")
    EXTRA_OUT.write_text(header(
        "Reject_Extra_Domain.list - Surge DOMAIN-SET (aggressive layer, entries not already in core)",
        f"Entries: {len(new['Reject_Extra_Domain.list'])} ({len(extra.suffix)} suffix, {len(extra.full)} exact)",
        "extra") + "\n".join(new["Reject_Extra_Domain.list"]) + "\n", encoding="utf-8")
    for k, text in new_modules.items():
        paths[k].write_text(text, encoding="utf-8")

    state = {
        "generated": stamp,
        "output": {k: len(v) for k, v in new_bodies.items()},
        "upstreams": {
            s["key"]: {"name": s["name"], "count": s["count"], "sha256": s["sha256"],
                       "fetched_at": s["fetched_at"], "url": s["url"],
                       "source": "fresh" if s["source"].startswith("fresh") else "fallback"}
            for s in statuses
        },
    }
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_changelog(stamp, diffs, new_bodies)
    write_report(stamp, statuses, raw_counts, removed, excludes, includes, guard_rules, ai_rules,
                 psl_dropped, dedupe_stats, in_core, layers, new_bodies, mods, hw, warnings)
    log("Files written.")
    return 0


def write_changelog(stamp, diffs, new_bodies) -> None:
    def capped(items):
        shown = [f"- `{i}`" for i in items[:CHANGELOG_MAX_ITEMS]]
        if len(items) > CHANGELOG_MAX_ITEMS:
            shown.append(f"- ... and {len(items) - CHANGELOG_MAX_ITEMS} more")
        return shown or ["- (none)"]

    L = [f"## {stamp}", ""]
    L.append("; ".join(f"`{k}` {len(new_bodies[k])} (+{len(a)}/-{len(r)})" for k, (a, r) in diffs.items()))
    L.append("")
    for k, (a, r) in diffs.items():
        if not a and not r:
            continue
        L += [f"<details><summary>{k}: +{len(a)} / -{len(r)}</summary>", "", "Added:", "", *capped(a), "",
              "Removed:", "", *capped(r), "", "</details>", ""]
    entry = "\n".join(L)
    title = "# Ad-block rules changelog\n\nNewest first. Generated by `scripts/update_adblock_rules.py`.\n\n"
    old_entries: list[str] = []
    if CHANGELOG.exists():
        parts = re.split(r"(?m)^(?=## )", CHANGELOG.read_text(encoding="utf-8"))
        old_entries = [p.rstrip("\n") + "\n" for p in parts[1:]]
    CHANGELOG.write_text(title + "\n".join([entry] + old_entries[:CHANGELOG_MAX_RUNS - 1]), encoding="utf-8")


def fmt_items(items: list[str], limit: int = REPORT_MAX_ITEMS) -> str:
    shown = ", ".join(f"`{i}`" for i in items[:limit])
    if len(items) > limit:
        shown += f", ... and {len(items) - limit} more"
    return shown or "(none)"


def write_report(stamp, statuses, raw_counts, removed, excludes, includes, guard_rules, ai_rules,
                 psl_dropped, dedupe_stats, in_core, layers, new_bodies, mods, hw, warnings) -> None:
    L = ["# Ad-block rules report", "", f"Generated: {stamp}", ""]
    L += ["## Upstreams", "", "| Upstream | Layer | Entries | Source | Fetched | URL used |", "|---|---|---|---|---|---|"]
    for s in statuses:
        L.append(f"| {s['name']} | {s['kind']} | {s['count']} | {s['source']} | {s['fetched_at']} | {s['url']} |")
    L += ["", "List upstream breakdown:", "",
          "| Upstream | DOMAIN | SUFFIX | KEYWORD | WILDCARD | URL-REGEX | AND/OR | IP-CIDR |",
          "|---|---|---|---|---|---|---|---|"]
    for s in statuses:
        b = s.get("breakdown")
        if b:
            L.append(f"| {s['name']} | {b['DOMAIN']} | {b['DOMAIN-SUFFIX']} | {b['DOMAIN-KEYWORD']} | "
                     f"{b['DOMAIN-WILDCARD']} | {b['URL-REGEX']} | {b['AND/OR/NOT']} | {b['IP-CIDR']} |")
    L += ["", f"- Module host-wide rejects moved into the core DOMAIN-SET: {hw.domain_count()} "
          f"({fmt_items(sorted(hw.full) + ['.' + s for s in sorted(hw.suffix)])})",
          f"- Raw union before filtering: core {raw_counts['core']}, extra {raw_counts['extra']}", ""]
    if warnings:
        L += ["### Upstream warnings", ""] + [f"- {w}" for w in warnings] + [""]

    L += ["## Outputs", ""]
    for k, v in new_bodies.items():
        L.append(f"- `{k}`: {len(v)} lines")
    c = layers["core"]
    L += [f"- Reject.list breakdown: DOMAIN-KEYWORD {len(c.keyword)}, DOMAIN-WILDCARD {len(c.wildcard)}, "
          f"AND/OR {len(c.logical)}, URL-REGEX {len(c.regex)}, IP-CIDR {len(c.ip)}",
          f"- Extra-layer entries dropped because core already covers them: {in_core}", ""]

    L += ["## Removed by category", "", "| Category | Removed |", "|---|---|"]
    groups = [("exclude", "adblock-exclude.txt"), ("ai", "AI group"), ("guard", "must-not-block guard")]
    for label, _ in groups:
        for cat, items in sorted(removed[label].items()):
            L.append(f"| {cat} | {len(items)} |")
    L.append(f"| public suffix / bare eTLD | {sum(len(v) for v in psl_dropped.values())} |")
    L.append("")
    for label, title in groups:
        L += [f"### {title}", ""]
        if not removed[label]:
            L += ["(nothing removed)", ""]
        for cat, items in sorted(removed[label].items()):
            L += [f"**{cat}** ({len(items)}): " + fmt_items(sorted(items)), ""]
    unused = [r.raw for r in excludes if not r.hits]
    if unused:
        L += ["Exclude rules with no current match (kept for future upstream changes): " + fmt_items(unused, 200), ""]
    L += ["### Public suffix / eTLD entries", ""]
    for k, v in psl_dropped.items():
        L.append(f"- {k}: {len(v)}: {fmt_items(v)}")
    L += ["", "## Manual includes", "", fmt_items([r.raw for r in includes], 200), ""]
    L += ["## Dropped rule types", ""]
    dropped: dict[str, set[str]] = defaultdict(set)
    for s in statuses:
        for k, v in (s.get("dropped") or {}).items():
            dropped[k].update(v)
    for k, v in sorted(dropped.items()):
        L.append(f"- **{k}** ({len(v)}): {fmt_items(sorted(v), 20)}")
    L += ["", "## Normalisation", ""]
    for lname, st in dedupe_stats.items():
        L += [f"- {lname}: {k}: {v}" for k, v in sorted(st.items())]
    L.append("")

    L += ["## Modules", ""]
    for v in (mods["mac"], mods["lite"]):
        cnt = am.count_sections(v.entries)
        n_body = sum(1 for e in v.entries if e.section == "Script" and e.body)
        L += [f"### {v.name}", "",
              f"- Sections: " + ", ".join(f"{k} {n}" for k, n in sorted(cnt.items())),
              f"- Scripts: {cnt.get('Script', 0)} ({n_body} requires-body); MITM hosts: {len(v.mitm)}",
              f"- Apps ({len(v.apps)}): " + ", ".join(v.apps), ""]
        if v.skipped_apps:
            L += [f"- Skipped: " + ", ".join(v.skipped_apps), ""]
    L += ["### Module entries dropped", "", "| Reason | Count | Examples |", "|---|---|---|"]
    for k, items in sorted(mods["dropped"].items()):
        ex = ", ".join(f"`{i[:80]}`" for i in items[:3]).replace("|", "\\|")
        L.append(f"| {k} | {len(items)} | {ex} |")
    L.append("")
    REPORT.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Abort as e:
        gh_annotation("error", str(e))
        log(f"ABORT: {e}")
        sys.exit(1)
