"""Surge module parsing / selection helpers for scripts/update_adblock_rules.py.

Standard library only. Turns maintained upstream app-ad modules into two generated modules:
a full Mac variant and a budgeted iOS Lite variant. Entries are grouped per app (registrable
domain of the request host), filtered against the never-MITM list and checked for MITM coverage.
"""

from __future__ import annotations

import fnmatch
import re
from collections import defaultdict
from dataclasses import dataclass, field

SECTIONS = ("Rule", "URL Rewrite", "Map Local", "Header Rewrite", "Body Rewrite", "Script", "MITM")
EMITTED_SECTIONS = ("URL Rewrite", "Map Local", "Header Rewrite", "Body Rewrite", "Script")
SCRIPT_HOST_ALLOW = ("raw.githubusercontent.com", "github.com", "gist.githubusercontent.com",
                     "cdn.jsdelivr.net", "kelee.one")

# Remote "reject" payloads used by yfamilys/ddgksf2013 Map Local lines, replaced by inline data
# so the module does not depend on a third-party file at request time.
INLINE_DATA = {
    "reject-200.txt": 'data-type=text data=" " status-code=200',
    "reject-dict.json": 'data-type=text data="{}" status-code=200 header="Content-Type:application/json"',
    "reject-array.json": 'data-type=text data="[]" status-code=200 header="Content-Type:application/json"',
    "reject-img.gif": "data-type=tiny-gif status-code=200",
}

@dataclass
class Entry:
    section: str
    line: str                 # line as emitted (script name is assigned at render time)
    pattern: str
    source: str
    label: str = ""           # upstream app label (fmz200 `# > name`), if any
    hosts: list[str] = field(default_factory=list)   # host globs taken from the pattern
    port: int | None = None
    https: bool = True
    app: str = ""             # registrable domain, used for grouping
    mitm: set[str] = field(default_factory=set)      # upstream MITM entries this entry needs
    body: bool = False        # buffers the body (requires-body script or body rewrite)
    script_name: str = ""


# ---------------------------------------------------------------- tokenising helpers

def split_top(s: str, sep: str = ",") -> list[str]:
    """Split on `sep` outside quotes and parentheses."""
    out, buf, depth, quote = [], [], 0, ""
    for ch in s:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = ""
            continue
        if ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth -= 1
            buf.append(ch)
        elif ch == sep and depth == 0:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    out.append("".join(buf))
    return out


def unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def parse_kv(s: str) -> list[tuple[str, str]]:
    pairs = []
    for part in split_top(s):
        part = part.strip()
        if not part:
            continue
        k, _, v = part.partition("=")
        pairs.append((k.strip(), v.strip()))
    return pairs


# ---------------------------------------------------------------- module text parsing

def iter_sections(text: str):
    """Yield (section, line, label, hostname_comment) for every non-comment line."""
    section = None
    label = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^\[([^\]]+)\]$", line)
        if m:
            section = m.group(1).strip()
            label = ""
            continue
        if line.startswith("#"):
            lm = re.match(r"^#\s*>\s*(.+)$", line)
            if lm:
                label = lm.group(1).strip()
            continue
        if section is None or line.startswith("//") or line.startswith(";"):
            continue
        yield section, line, label


def module_meta(text: str) -> dict[str, str]:
    meta = {}
    for line in text.splitlines():
        m = re.match(r"^#!([\w-]+)\s*=\s*(.*)$", line.strip())
        if m:
            meta.setdefault(m.group(1), m.group(2).strip())
    return meta


def parse_arguments(meta: dict[str, str]) -> dict[str, str]:
    args = {}
    for part in split_top(meta.get("arguments", "")):
        k, _, v = part.partition(":")
        if k.strip():
            args[k.strip()] = unquote(v)
    return args


def mitm_hosts(text: str) -> list[str]:
    hosts: list[str] = []
    for section, line, _ in iter_sections(text):
        if section != "MITM":
            continue
        key, _, value = line.partition("=")
        if key.strip() != "hostname":
            continue
        value = value.replace("%APPEND%", "").replace("%INSERT%", "")
        hosts += [h.strip().lower() for h in value.split(",") if h.strip()]
    return hosts


def module_rule_lines(text: str) -> list[str]:
    return [line for section, line, _ in iter_sections(text) if section == "Rule"]


# ---------------------------------------------------------------- pattern -> host

SCHEME_RE = re.compile(r"^\^?(https?\??|http)(?::|\\?:)\\?/\\?/")


def regex_host(pattern: str) -> tuple[list[str], int | None, bool] | None:
    """Return ([host globs], port, https_possible) for a URL regex, or None if host-agnostic."""
    p = pattern.strip()
    if p.startswith('"') and p.endswith('"'):
        p = p[1:-1]
    m = re.match(r"^\^?(https\?|https|http\??)(?::)(?:\\/|/)(?:\\/|/)", p)
    if not m:
        return None
    scheme = m.group(1)
    rest = p[m.end():].replace("(?>", "(").replace("(?:", "(")
    # host runs until an (escaped) slash, port, end anchor, query or end of pattern
    hm = re.match(r"^(.*?)(?=\\/|/|\\?:\d|\(:\\d|\$|\\\?|$)", rest)
    host = hm.group(1) if hm else rest
    after = rest[len(host):]
    port = None
    pm = re.match(r"^\\?:(\d+)", after)
    if pm:
        port = int(pm.group(1))
    alts = expand_alternation(host)
    if alts is None:
        return None
    globs = []
    for h in alts:
        g = host_regex_to_glob(h)
        if g is None:
            return None
        globs.append(g)
    if not globs:
        return None
    return globs, port, scheme not in ("http", "http?")


def expand_alternation(h: str) -> list[str] | None:
    m = re.search(r"\(([^()]*)\)\??", h)
    if not m:
        return [h]
    if m.group(0).endswith("?"):
        options = m.group(1).split("|") + [""]
    else:
        options = m.group(1).split("|")
    out = []
    for opt in options:
        sub = expand_alternation(h[:m.start()] + opt + h[m.end():])
        if sub is None:
            return None
        out += sub
    return out if len(out) <= 16 else None


QUANT = r"(?:\{\d*,?\d*\}|[+*?])?\??"


def host_regex_to_glob(h: str) -> str | None:
    g = re.sub(r"\[[^\]]*\]" + QUANT, "*", h)
    g = re.sub(r"\\[wdWD]" + QUANT, "*", g)
    g = re.sub(r"(?<!\\)\.(?:\{\d*,?\d*\}|[+*])\??", "*", g)
    g = g.replace(r"\.", ".").replace(r"\-", "-")
    g = re.sub(r"[a-zA-Z0-9]\?", "*", g)
    g = re.sub(r"\*+", "*", g).lower()
    g = re.sub(r"(?<=[a-z0-9])\*$", "", g)
    if not re.fullmatch(r"[a-z0-9.*-]+", g) or "." not in g:
        return None
    labels = g.strip("*.").split(".")
    literal = re.sub(r"[^a-z0-9]", "", "".join(labels[:-1]).replace("*", ""))
    if len(literal) < 3:
        return None
    return g


def glob_is_specific(g: str) -> bool:
    """True if the part after the last wildcard is at least a registrable-looking name."""
    tail = g.rsplit("*", 1)[-1].strip(".")
    return len(tail.split(".")) >= 2


def glob_instances(g: str) -> list[str]:
    if "*" not in g and "?" not in g:
        return [g]
    out = set()
    for rep in ("", "a", "a.", "a.b."):
        out.add(g.replace("*", rep).replace("?", "a").replace("..", ".").lstrip("."))
    return sorted(out)


def globs_overlap(a: str, b: str) -> bool:
    if a == b:
        return True
    return (any(fnmatch.fnmatchcase(x, b) for x in glob_instances(a))
            or any(fnmatch.fnmatchcase(x, a) for x in glob_instances(b)))


def split_port(h: str) -> tuple[str, int | None]:
    m = re.match(r"^(.*?):(\d+)$", h)
    if m:
        return m.group(1), int(m.group(2))
    return h, None


# ---------------------------------------------------------------- entry construction

def build_entries(source: str, text: str, psl) -> tuple[list[Entry], list[str], dict[str, list[str]]]:
    """Parse one module; return (entries, upstream MITM hosts, dropped{reason: [lines]})."""
    meta = module_meta(text)
    args = parse_arguments(meta)
    upstream_mitm = mitm_hosts(text)
    entries: list[Entry] = []
    dropped: dict[str, list[str]] = defaultdict(list)

    def subst(line: str) -> str | None:
        def rep(m):
            k = m.group(1)
            return args[k] if k in args else m.group(0)
        out = re.sub(r"\{\{\{([^}]+)\}\}\}", rep, line)
        return None if "{{{" in out else out

    for section, line, label in iter_sections(text):
        if section in ("Rule", "MITM", "General", "Host"):
            continue
        if section not in EMITTED_SECTIONS:
            dropped[f"unsupported section [{section}]"].append(line)
            continue
        line2 = subst(line)
        if line2 is None:
            dropped["unresolved {{{argument}}} placeholder"].append(line)
            continue
        e = make_entry(section, line2, source, label, dropped)
        if e is None:
            continue
        info = regex_host(e.pattern)
        if info is None:
            dropped["host-agnostic or unparseable URL pattern"].append(line)
            continue
        e.hosts, e.port, e.https = info
        if e.https:
            for h in upstream_mitm:
                mh, mp = split_port(h)
                if mh.startswith("-"):
                    continue
                if (mp or 443) != (e.port or 443) and not (mp == 0):
                    continue
                if any(globs_overlap(g, mh) for g in e.hosts):
                    e.mitm.add(h)
            if not e.mitm:
                dropped["inactive upstream (no matching MITM hostname)"].append(line)
                continue
        specific = [g for g in e.hosts if glob_is_specific(g)]
        if specific:
            e.app = app_key(specific[0], psl)
        elif e.mitm:
            e.app = app_key(split_port(sorted(e.mitm)[0])[0], psl)
        else:
            dropped["host-agnostic or unparseable URL pattern"].append(line)
            continue
        entries.append(e)
    return entries, upstream_mitm, dropped


def make_entry(section: str, line: str, source: str, label: str, dropped) -> Entry | None:
    if section == "URL Rewrite":
        parts = line.split()
        if len(parts) < 3:
            dropped["malformed URL Rewrite"].append(line)
            return None
        pattern, mode = parts[0], parts[-1].lower()
        if mode == "reject" or (len(parts) == 2 and parts[1].lower() == "reject"):
            return Entry(section, f"{pattern} - reject", pattern, source, label)
        if mode in ("302", "307", "header"):
            return Entry(section, line, pattern, source, label)
        dropped[f"URL Rewrite type {mode!r}"].append(line)
        return None
    if section == "Map Local":
        pattern, _, rest = line.partition(" ")
        rest = rest.strip()
        dm = re.search(r'data="(https?://[^"]+)"', rest)
        if dm:
            fname = dm.group(1).rsplit("/", 1)[-1]
            if fname in INLINE_DATA and "deezertidal/Surge_Module" in dm.group(1):
                rest = INLINE_DATA[fname]
        if " url " in f" {line} " and "data" not in rest:
            dropped["malformed Map Local"].append(line)
            return None
        return Entry(section, f"{pattern} {rest}".strip(), pattern, source, label)
    if section == "Header Rewrite":
        parts = line.split(None, 2)
        if len(parts) < 3 or parts[0] not in ("http-request", "http-response"):
            dropped["malformed Header Rewrite"].append(line)
            return None
        return Entry(section, line, parts[1], source, label)
    if section == "Body Rewrite":
        parts = line.split(None, 2)
        if len(parts) < 3 or parts[0] not in ("http-request", "http-response",
                                              "http-request-jq", "http-response-jq"):
            dropped["malformed Body Rewrite"].append(line)
            return None
        return Entry(section, line, parts[1], source, label, body=True)
    if section == "Script":
        name, _, params = line.partition("=")
        kv = parse_kv(params)
        d = {k: v for k, v in kv}
        stype = d.get("type", "")
        if stype not in ("http-request", "http-response"):
            dropped[f"script type {stype or '?'!r} (only http-request/response kept)"].append(line)
            return None
        if " url script-" in line or "pattern" not in d or "script-path" not in d:
            dropped["malformed Script (QX syntax / missing pattern or script-path)"].append(line)
            return None
        path = unquote(d["script-path"])
        host = re.sub(r"^https?://", "", path).split("/", 1)[0].lower()
        if host not in SCRIPT_HOST_ALLOW:
            dropped[f"script hosted outside GitHub/jsDelivr ({host})"].append(line)
            return None
        body = d.get("requires-body", "").lower() in ("1", "true")
        e = Entry(section, params.strip(), unquote(d["pattern"]), source, label, body=body)
        e.script_name = name.strip()
        return e
    return None


def app_key(host_glob: str, psl) -> str:
    h = split_port(host_glob)[0]
    tail = h.rsplit("*", 1)[-1].strip(".")
    if re.fullmatch(r"[\d.]+", tail) and tail.count(".") == 3:
        return tail
    if len(tail.split(".")) >= 2:
        return psl.registrable(tail) or tail
    # wildcard TLD such as api.weibo.* or *.xima*.*: group by the last literal label
    literal = [l.replace("*", "") for l in h.split(".") if l.replace("*", "")]
    return (literal[-2] if len(literal) >= 2 and len(literal[-1]) <= 3 else literal[-1]) + ".*" if literal else h


# ---------------------------------------------------------------- domains from host-wide rejects

def host_wide_reject_domain(e: Entry) -> tuple[str, bool] | None:
    """URL Rewrite rejects that cover a whole host -> (domain, is_suffix)."""
    if e.section != "URL Rewrite" or not e.line.endswith(" - reject") or e.port:
        return None
    p = e.pattern
    m = re.match(r"^\^?https?\??:(?:\\/|/)(?:\\/|/)(.*)$", p)
    if not m:
        return None
    rest = m.group(1)
    hm = re.match(r"^((?:\.\*|\.\+\??|\[\^\\?/\]\+)\\\.)?((?:[a-zA-Z0-9-]+\\?\.)+[a-zA-Z0-9-]+)"
                  r"(\\/|/)?(\.\*|\.\+)?\$?$", rest)
    if not hm:
        return None
    suffix = bool(hm.group(1))
    domain = hm.group(2).replace("\\.", ".").lower()
    if not re.fullmatch(r"[a-z0-9-]+(\.[a-z0-9-]+)+", domain):
        return None
    return domain, suffix


# ---------------------------------------------------------------- MITM safety

def mitm_blocked(host: str, never: list[str]) -> str | None:
    """Return the never-MITM pattern that conflicts with `host` (a MITM glob), if any."""
    h, _ = split_port(host.lower())
    for n in never:
        if globs_overlap(h, n):
            return n
    if "*" in h or "?" in h:
        labels = h.split(".")[:-1]
        if not any(re.search(r"[a-z][a-z0-9-]{3,}", l.replace("*", "").replace("?", "")) for l in labels):
            return "(over-broad wildcard)"
    return None


# ---------------------------------------------------------------- selection and rendering

@dataclass
class Variant:
    name: str
    entries: list[Entry]
    mitm: list[str]
    apps: list[str]
    skipped_apps: list[str]
    notes: list[str]


def select_mac(entries: list[Entry]) -> Variant:
    apps = sorted({e.app for e in entries})
    return Variant("Mac", entries, sorted({h for e in entries for h in e.mitm}), apps, [], [])


def glob_under_suffix(g: str, s: str) -> bool:
    """Label-wise: can host glob `g` (e.g. api.weibo.*, *.zdmimg.com) name a host at or under `s`?"""
    gl, sl = split_port(g)[0].split("."), s.split(".")
    if len(gl) < len(sl):
        return False
    return all(fnmatch.fnmatchcase(sl[-i], gl[-i]) for i in range(1, len(sl) + 1))


def matches_suffixes(e: Entry, suffixes: list[str]) -> bool:
    hosts = [g for g in e.hosts if glob_is_specific(g)] or e.hosts + sorted(e.mitm)
    return any(glob_under_suffix(g, s) for g in hosts for s in suffixes)


SPLASH_HINT = re.compile(r"splash|launch|startup|start_?up|loading|open_?ad|openscreen|kaiping|"
                         r"advert|adv?\b|/ad/|ads|boot|welcome|screen", re.I)


def script_priority(e: Entry) -> tuple[int, int]:
    return (1 if e.body else 0, 0 if SPLASH_HINT.search(e.pattern) else 1)


def select_lite(entries: list[Entry], app_order: list[tuple[str, list[str]]], max_scripts: int,
                max_mitm: int, max_body_rewrite: int, max_scripts_per_app: int = 6) -> Variant:
    chosen: list[Entry] = []
    taken_ids: set[int] = set()
    mitm: set[str] = set()
    n_scripts = n_body = 0
    apps, skipped, notes = [], [], []
    for name, suffixes in app_order:
        group = [e for e in entries if id(e) not in taken_ids and matches_suffixes(e, suffixes)]
        if not group:
            skipped.append(f"{name} (no entries upstream)")
            continue
        plain = [e for e in group if e.section not in ("Script", "Body Rewrite")]
        bodyrw = [e for e in group if e.section == "Body Rewrite"]
        scripts = sorted((e for e in group if e.section == "Script"), key=script_priority)
        taken = []
        cur_mitm = set(mitm)
        dropped_here = 0
        # entries whose hosts are already decrypted cost nothing; then cheapest first
        for e in sorted(plain, key=lambda e: len(e.mitm - cur_mitm)):
            if len(cur_mitm | e.mitm) <= max_mitm:
                taken.append(e)
                cur_mitm |= e.mitm
            else:
                dropped_here += 1
        for e in bodyrw:
            if n_body < max_body_rewrite and len(cur_mitm | e.mitm) <= max_mitm:
                taken.append(e)
                cur_mitm |= e.mitm
                n_body += 1
            else:
                dropped_here += 1
        app_scripts = 0
        for e in scripts:
            if (n_scripts < max_scripts and app_scripts < max_scripts_per_app
                    and len(cur_mitm | e.mitm) <= max_mitm):
                taken.append(e)
                cur_mitm |= e.mitm
                n_scripts += 1
                app_scripts += 1
            else:
                dropped_here += 1
        if not taken:
            skipped.append(f"{name} (budget)")
            continue
        chosen += taken
        taken_ids |= {id(e) for e in taken}
        mitm = cur_mitm
        apps.append(name + (f" (partial: {len(taken)} of {len(taken) + dropped_here} entries)"
                            if dropped_here else ""))
    order = {id(e): i for i, e in enumerate(entries)}
    chosen.sort(key=lambda e: order[id(e)])
    return Variant("iOS Lite", chosen, sorted(mitm), apps, skipped, notes)


def render(variant: Variant, header: list[str]) -> str:
    out = list(header)
    used_names: dict[str, int] = defaultdict(int)
    for section in EMITTED_SECTIONS:
        items = [e for e in variant.entries if e.section == section]
        if not items:
            continue
        out += ["", f"[{section}]"]
        last_app = None
        for e in items:
            tag = e.label or e.app
            if e.app != last_app:
                out.append(f"# > {tag}  [{e.source}]")
                last_app = e.app
            if section == "Script":
                base = re.sub(r"[^A-Za-z0-9]+", "-", e.app).strip("-") or "app"
                used_names[base] += 1
                out.append(f"ab-{base}-{used_names[base]} = {e.line}")
            else:
                out.append(e.line)
    if variant.mitm:
        out += ["", "[MITM]", "hostname = %APPEND% " + ", ".join(variant.mitm)]
    return "\n".join(out) + "\n"


def count_sections(entries: list[Entry]) -> dict[str, int]:
    c: dict[str, int] = defaultdict(int)
    for e in entries:
        c[e.section] += 1
    return dict(c)
