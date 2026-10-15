#!/usr/bin/env python3
"""Unit tests for scripts/update_adblock_rules.py and scripts/adblock_modules.py (stdlib only).

    python3 -m unittest scripts/test_adblock_rules.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adblock_modules as am  # noqa: E402
import update_adblock_rules as u  # noqa: E402

PSL_TEXT = "com\nnet\ncn\ncom.cn\n*.ck\n!www.ck\ngithub.io\nsquare.site\n"


def rs_from(text: str) -> u.RuleSet:
    rs = u.RuleSet()
    u.parse_surge(text, rs)
    return rs


class MatchingTests(unittest.TestCase):
    def test_keyword_tree(self):
        self.assertTrue(u.keyword_hits_tree("abchina", "abchina.com"))
        self.assertTrue(u.keyword_hits_tree("-tracker.biliapi.net", "biliapi.net"))
        self.assertTrue(u.keyword_hits_tree("adjust.", "adjust.com"))
        self.assertFalse(u.keyword_hits_tree("umeng", "engage.com"))
        self.assertFalse(u.keyword_hits_tree("xadjust.", "adjust.com"))

    def test_wildcard_tree(self):
        self.assertTrue(u.wildcard_hits_tree("beacons*.gvt?.com", "gvt2.com"))
        self.assertTrue(u.wildcard_hits_tree("*.apple.com", "apple.com"))
        self.assertTrue(u.wildcard_hits_tree("ads-*.tiktok.com", "tiktok.com"))
        self.assertFalse(u.wildcard_hits_tree("ads-*.xhscdn.com", "tiktok.com"))

    def test_logical(self):
        rule = "AND,((DOMAIN-KEYWORD,-ad-),(DOMAIN-SUFFIX,byteimg.com))"
        self.assertTrue(u.logical_eval_host(rule, "p3-ad-sign.byteimg.com"))
        self.assertFalse(u.logical_eval_host(rule, "p3-sign.byteimg.com"))
        self.assertFalse(u.logical_hits_tree(rule, "abchina.com"))
        self.assertTrue(u.logical_hits_tree(rule, "byteimg.com"))
        self.assertFalse(u.logical_hits_tree("AND,((DOMAIN-KEYWORD,ads),(DOMAIN-KEYWORD,-normal.x.com))",
                                             "abchina.com"))

    def test_psl(self):
        psl = u.PSL(PSL_TEXT)
        self.assertTrue(psl.is_suffix("square.site"))
        self.assertTrue(psl.is_suffix("foo.ck"))
        self.assertFalse(psl.is_suffix("www.ck"))
        self.assertEqual(psl.registrable("a.b.example.com.cn"), "example.com.cn")
        rs = rs_from(".square.site\n.ads.square.site\ngithub.io\nads.example.com\n")
        self.assertEqual(u.drop_public_suffixes(rs, psl), [".square.site", "github.io"])
        self.assertIn("ads.square.site", rs.suffix)


class ProtectorTests(unittest.TestCase):
    def protector(self, lines: str) -> u.Protector:
        path = Path(self._testMethodName + ".tmp")
        path.write_text(lines, encoding="utf-8")
        try:
            return u.Protector(u.parse_rule_file(path, ("DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD",
                                                        "DOMAIN-WILDCARD", "URL-REGEX", "IP-CIDR")))
        finally:
            path.unlink()

    def test_host_keeps_subdomain_blocks(self):
        p = self.protector("DOMAIN,apple.com\n")
        rs = rs_from(".apple.com\nmetrics.apple.com\n.metrics.icloud.com\n.com\n")
        p.apply(rs)
        self.assertEqual(rs.suffix, {"metrics.icloud.com"})
        self.assertEqual(rs.full, {"metrics.apple.com"})

    def test_tree_removes_everything_inside_and_above(self):
        p = self.protector(".abchina.com\n")
        rs = rs_from(".ad.abchina.com\nabchina.com\n.ad.example.com\n"
                     "DOMAIN-KEYWORD,abchina\nDOMAIN-KEYWORD,ads\nDOMAIN-WILDCARD,*.abchina.com\n")
        p.apply(rs)
        self.assertEqual(rs.suffix, {"ad.example.com"})
        self.assertEqual(rs.full, set())
        self.assertEqual(rs.keyword, {"ads"})
        self.assertEqual(rs.wildcard, set())

    def test_wildcard_exclude_spares_siblings(self):
        p = self.protector("DOMAIN-WILDCARD,tnc*.isnssdk.com\n")
        rs = rs_from(".tnc16-alisg.isnssdk.com\n.log.isnssdk.com\n.isnssdk.com\n")
        p.apply(rs)
        self.assertEqual(rs.suffix, {"log.isnssdk.com"})

    def test_regex_and_ip(self):
        p = self.protector("URL-REGEX,/\\d+/resolve\nIP-CIDR,10.0.0.0/8\n")
        rs = rs_from("URL-REGEX,/\\d+/resolve\nURL-REGEX,^http://cdn.wup.huya.com/x$\n"
                     "IP-CIDR,10.1.0.0/16\nIP-CIDR,1.2.3.4/32\n")
        p.apply(rs)
        self.assertEqual(rs.regex, {"^http://cdn.wup.huya.com/x$"})
        self.assertEqual(rs.ip, {"1.2.3.4/32"})

    def test_dedupe_and_core_subtraction(self):
        core = rs_from(".example.com\na.example.com\n.b.example.com\nx.org\n")
        u.dedupe(core)
        self.assertEqual(core.suffix, {"example.com"})
        self.assertEqual(core.full, {"x.org"})
        extra = rs_from(".c.example.com\nx.org\n.y.org\n")
        self.assertEqual(u.subtract_core(extra, core), 2)
        self.assertEqual(extra.suffix, {"y.org"})


class ModuleTests(unittest.TestCase):
    def test_regex_host(self):
        self.assertEqual(am.regex_host(r"^https?:\/\/api\.zhihu\.com\/topstory")[0], ["api.zhihu.com"])
        self.assertEqual(am.regex_host(r"^https?:\/\/.*\.amap\.com\/ws")[0], ["*.amap.com"])
        hosts, port, https = am.regex_host(r"^https?:\/\/(ipv4|interface\d?)\.music\.163\.com\/eapi")
        self.assertEqual(sorted(hosts), ["interface*.music.163.com", "ipv4.music.163.com"])
        self.assertIsNone(am.regex_host(r"^https?:\/\/[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+){1,3}\/api\/v\d\/advert"))
        self.assertEqual(am.regex_host(r"^https?:\/\/m\.x\.com\.cn:441\/mgw")[1], 441)
        self.assertFalse(am.regex_host(r"^http:\/\/cdn\.x\.com\/a")[2])

    def test_host_wide_reject(self):
        e = am.Entry("URL Rewrite", r"^https?:\/\/adapi\.izuiyou\.com\/ - reject", r"^https?:\/\/adapi\.izuiyou\.com\/", "t")
        self.assertEqual(am.host_wide_reject_domain(e), ("adapi.izuiyou.com", False))
        e = am.Entry("URL Rewrite", r"^https?:\/\/.+\.pglstatp-toutiao\.com - reject", r"^https?:\/\/.+\.pglstatp-toutiao\.com", "t")
        self.assertEqual(am.host_wide_reject_domain(e), ("pglstatp-toutiao.com", True))
        e = am.Entry("URL Rewrite", r"^https?:\/\/a\.b\.com\/ad\/ - reject", r"^https?:\/\/a\.b\.com\/ad\/", "t")
        self.assertIsNone(am.host_wide_reject_domain(e))

    def test_lint_quotes(self):
        bad = r'http-response ^https?:\/\/beta-api\.crunchyroll\.com\/cms offset_ms":\d+ offset_ms":99999999999999'
        self.assertIn("quot", am.lint_line("Body Rewrite", bad))
        self.assertIsNone(am.surge_tokens("http-response ^x a\"b"))
        ok = [
            r'http-response ^https?:\/\/m\.lkcoffee\.com\/capi "popTitle":".+?" "popTitle":""',
            r'http-response ^https?:\/\/x\.yangkeduo\.com\/goods "list":\[.+\] "list":[]',
            r"""http-response-jq ^https?:\/\/acs\.x\.com\/gw '.data |= map(select(.name | contains("营销") | not))'""",
        ]
        for line in ok:
            self.assertIsNone(am.lint_line("Body Rewrite", line), line)
        self.assertIsNone(am.lint_line("Map Local", r'^https?:\/\/a\.b\.com\/x data-type=text data=" " status-code=200'))
        self.assertIsNotNone(am.lint_line("Map Local", r'^https?:\/\/a\.b\.com\/x data-type=json data="{}"'))
        self.assertIsNotNone(am.lint_line("URL Rewrite", r"^https?:\/\/a\.b\.com\/x -"))
        self.assertIsNotNone(am.lint_line("Script", "s = type=http-response,pattern=^x,script-path="))
        self.assertIsNotNone(am.lint_line("Script", "s = type=http-response,pattern=^x,script-path=u,foo=1"))
        probs = am.lint_module("#!name=t\n[Rewrite]\n^a reject\n[MITM]\nhostname = %APPEND% a.com, ,b.com\n")
        self.assertEqual([p[1] for p in probs], ["unknown section [Rewrite]", "empty or malformed MITM hostname"])

    def test_mitm_blocked(self):
        never = ["*bank*", "*.apple.com", "apple.com", "acs.m.taobao.com"]
        self.assertEqual(am.mitm_blocked("creditcardapp.bankcomm.com", never), "*bank*")
        self.assertEqual(am.mitm_blocked("buy.itunes.apple.com", never), "*.apple.com")
        self.assertIsNotNone(am.mitm_blocked("*.com", never))
        self.assertEqual(am.mitm_blocked("*.co", []), "(over-broad wildcard)")
        self.assertIsNone(am.mitm_blocked("api.weibo.*", never))
        self.assertIsNone(am.mitm_blocked("api.zhihu.com", never))

    def test_glob_under_suffix(self):
        self.assertTrue(am.glob_under_suffix("api.weibo.*", "weibo.cn"))
        self.assertTrue(am.glob_under_suffix("*.xima*.*", "ximalaya.com"))
        self.assertFalse(am.glob_under_suffix("*.com", "weibo.cn"))

    def test_build_entries_and_lite_budget(self):
        text = "\n".join([
            "#!name=t",
            "[URL Rewrite]",
            r"^https?:\/\/a\.example\.com\/ad - reject",
            "[Map Local]",
            r'^https?:\/\/b\.example\.com\/x data="https://raw.githubusercontent.com/deezertidal/Surge_Module/master/files/reject-dict.json"',
            "[Script]",
            r"s1 = type=http-response,pattern=^https?:\/\/a\.example\.com\/feed,requires-body=1,script-path=https://raw.githubusercontent.com/x/y/main/a.js",
            r"s2 = type=http-response,pattern=^https?:\/\/a\.example\.com\/splash,requires-body=1,script-path=https://evil.workers.dev/a.js",
            "[MITM]",
            "hostname = %APPEND% a.example.com, b.example.com",
        ])
        psl = u.PSL(PSL_TEXT)
        entries, mitm, dropped = am.build_entries("t", text, psl)
        self.assertEqual(len(entries), 3)
        self.assertIn('data="{}"', entries[1].line)
        self.assertTrue(any("workers.dev" in k for k in dropped))
        lite = am.select_lite(entries, [("Example", ["example.com"])], max_scripts=0, max_mitm=1,
                              max_body_rewrite=0)
        self.assertLessEqual(len(lite.mitm), 1)
        self.assertFalse(any(e.section == "Script" for e in lite.entries))


if __name__ == "__main__":
    unittest.main()
