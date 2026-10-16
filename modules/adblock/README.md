# AdBlock modules for Surge

Generated daily by [`scripts/update_adblock_rules.py`](../../scripts/update_adblock_rules.py) together with the
ad-block rule sets (see [`rules/README.md`](../../rules/README.md)). Do not edit the `.sgmodule` files by hand;
edit `apps.txt` / `never-mitm.txt` (or the rules whitelist) and let the workflow regenerate them.

Goal: remove splash (开屏) ads, in-app banner / feed ads (牛皮癣) and ad click-through chains in apps. Pure
domain blocking is **not** in these modules: module `[Rule]` lines are inserted above every profile rule
(including your DIRECT exceptions), so all domain rejects live in `rules/Reject_Domain.list` and
`rules/Reject.list` instead. Every whole-host reject found in the upstream modules was moved there too, which
also makes it work without MITM.

## Install

| Device | Module | URL |
|---|---|---|
| Mac mini, MacBook | AdBlock (Mac) | `https://raw.githubusercontent.com/hqy-cmd/useformyself/main/modules/adblock/AdBlock.sgmodule` |
| iPhone | AdBlock (iOS Lite) | `https://raw.githubusercontent.com/hqy-cmd/useformyself/main/modules/adblock/AdBlock-iOS-Lite.sgmodule` |
| any (deprecated, optional) | MITM Guard | `https://raw.githubusercontent.com/hqy-cmd/useformyself/main/modules/adblock/MITM-Guard.sgmodule` |

Install only one of Mac / Lite per device. They replace the ddgksf2013 "APP启动页去广告" module and the old
fmz200 `test.sgmodule` snapshot (running both would apply the same scripts twice). The kelee "广告平台拦截器" module
can be disabled too: its domains are in `Reject_Domain.list`, and its `AND,(tnc ...),DIRECT` rule, which sent
TikTok's network-config requests around your TikTok→SG group, is intentionally not carried over.

These modules only act on HTTPS when MITM is enabled with a trusted CA (MITM is currently off on the Mac mini;
there only the rule sets work). Consider `skip-server-cert-verify = false` in `[MITM]`.

## What is inside

Sources, in precedence order (the first source that scripts a host owns that host's body processing):

1. **ddgksf2013 APP启动页去广告** — `https://yfamilys.com/module/startingad.sgmodule` (2026-10 build; published only
   there, the GitHub copies stopped in 2023). Cloudflare-protected: if CI is challenged, the snapshot or
   `rules/adblock-seed/` copy is used.
2. **fmz200 wool_scripts blockAds** — `https://raw.githubusercontent.com/fmz200/wool_scripts/main/Surge/module/blockAds.module`
   (maintained, 2026-09-10).
3. **kelee 广告平台拦截器** URL rewrites (Pinduoduo DSP ad chains) — QingRex/LoonKissSurge copy.

Per run (counts as of 2026-10-15):

| | Mac | iOS Lite |
|---|---|---|
| URL Rewrite (reject) | 480 | 73 |
| Map Local | 1047 | 170 |
| Body Rewrite (mostly `http-response-jq`) | 59 | 10 |
| Script | 264 (262 requires-body) | 30 (all requires-body) |
| MITM hosts (positive, after the guard exclusions) | 970 | 100 |
| Apps | ~650 app domains | 17 apps from `apps.txt` |

The iOS Lite budget is ≤ 30 scripts (at most 6 per app), ≤ 100 MITM hosts, ≤ 30 body rewrites. It walks
`apps.txt [lite]` in order: 高德地图, 小红书, 微博, 知乎, 网易云音乐, 喜马拉雅, 微信公众号, 拼多多 ad chains, 菜鸟, 美团/大众点评,
饿了么, 京东 (non-payment hosts), 百度地图/网盘, 爱奇艺, 优酷, 芒果TV, 腾讯视频/新闻; later entries (12306, 什么值得买, 彩云天气, 酷安,
携程, 滴滴, 顺丰, 中国移动) did not fit. Non-body scripts are preferred but none of these apps has one. **Reorder
`apps.txt` to the apps you actually use**; `rules/adblock-report.md` shows what was taken and skipped.

### Safety filters

- Never decrypted (entries needing them are dropped; the run fails if one slips through): App Store purchase /
  Apple ID / Apple system / iCloud hosts, every host in `rules/AI_Domain.list`, GitHub, Google, Microsoft,
  shared clouds (`*.cloudfront.net`, `*.amazonaws.com`, ...), bank hosts (anything containing `bank` plus the
  bank domains) and payment / order gateways (`*.alipay.com`, `*.tenpay.com`, `*.95516.com`, `acs.m.taobao.com`,
  `api.m.jd.com`, `*.pay.meituan.com`, ...). The generated MITM list holds only hosts that a kept entry
  needs, so upstream MITM entries such as ddgksf2013's `mobilepaas.abchina.com.cn` (农行) are not carried; its
  `creditcardapp.bankcomm.com` rewrites, 47 fmz200 bank-app rules and 57 entries on Taobao's
  `acs` / `guide-acs.m.taobao.com` order gateways were dropped (counts as of 2026-10-15).
- Scripts must load from GitHub / jsDelivr / kelee.one (16 ddgksf2013 Xiaohongshu scripts served from an
  anonymous `workers.dev` endpoint were dropped). Script URLs point at the upstream, nothing is vendored.
- Host-agnostic patterns (`^https?://[^/]+/.../v\d/version$` style) and wildcard MITM entries without a
  distinctive name are dropped.
- Map Local lines that fetched `deezertidal/Surge_Module/files/reject-*.{txt,json,gif}` are inlined
  (`data-type=text` / `tiny-gif`), so nothing is downloaded per request.
- Bilibili and YouTube are delegated to their dedicated, frequently updated modules (subscribe directly):
  - Bilibili: `https://raw.githubusercontent.com/kokoryh/Sparkle/master/release/surge/module/bilibili.sgmodule`
  - YouTube: `https://raw.githubusercontent.com/Maasea/sgmodule/master/YouTube.Enhance.sgmodule`

### MITM Guard

`%APPEND%` adds hostnames to the end of the list, and Surge stops at the first matching entry, so a `-host` at the
end cannot stop another module (for example the chxm1023 unlock collection, which decrypts
`buy.itunes.apple.com`) from decrypting a host. The guard is therefore built into **both** AdBlock modules: their
line is `hostname = %INSERT% -<guard hosts>, <own hosts>`, which puts the `[guard]` hosts of `never-mitm.txt`
(App Store purchases / Apple ID / Apple Pay, banks, payments) first. The run fails if an exclusion would cancel
one of the module's own hosts. The iOS Lite budget of 100 counts only the positive hosts. The guard deliberately
does not exclude all of `*.apple.com`, Google or YouTube, so WLoc (`gs-loc.apple.com`) and the YouTube module keep
working.

`MITM-Guard.sgmodule` (the same exclusions alone) is still generated for compatibility but is deprecated: a module
with only a `[MITM]` section cannot be enabled in Surge Mac (6.4.4, 6.10.0), and you no longer need it.

## Surge Mac 6.4.4 compatibility

All syntax predates Mac 6.4.4 / current iOS Surge 5: `[URL Rewrite] ... - reject`, Map Local `data-type=text` /
`tiny-gif` with `status-code` and `header` (Mac 5.5.1+), Body Rewrite (Mac 5.6.0+) and `http-response-jq`
(Mac 5.9.0+ / iOS 5.14.0+), `[Script]` `http-request` / `http-response` with `requires-body`, `[MITM] hostname =
%APPEND%` / `%INSERT%`. No `#!arguments` placeholders are used (fmz200 lines with unresolved `{{{...}}}` are
dropped). iOS limits body rewriting to 1 MB responses. Validate once with `surge-cli --check` on the Mac mini.

## Files

| File | Purpose |
|---|---|
| `AdBlock.sgmodule` / `AdBlock-iOS-Lite.sgmodule` / `MITM-Guard.sgmodule` | Generated modules. |
| `apps.txt` | `[lite]` app priority list for the iPhone module; `[delegated]` apps left to dedicated modules. |
| `never-mitm.txt` | Hosts never decrypted; `[guard]` part also exported as `-host` exclusions in both AdBlock modules (and the deprecated MITM Guard). |
