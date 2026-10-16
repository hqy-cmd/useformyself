# Ad-block rules report

Generated: 2026-10-16 15:59:46 UTC

## Upstreams

| Upstream | Layer | Entries | Source | Fetched | URL used |
|---|---|---|---|---|---|
| Public Suffix List | aux | 10336 | fresh | 2026-10-15 20:51:11 UTC | https://publicsuffix.org/list/public_suffix_list.dat |
| ddgksf2013 APP启动页去广告 (yfamilys) | module | 741 | fresh | 2026-10-15 20:51:11 UTC | https://yfamilys.com/module/startingad.sgmodule |
| fmz200 wool_scripts blockAds | module | 1725 | fresh | 2026-10-15 20:51:11 UTC | https://raw.githubusercontent.com/fmz200/wool_scripts/main/Surge/module/blockAds.module |
| kelee 广告平台拦截器 (URL Rewrite) | module | 4 | fresh | 2026-10-15 20:51:11 UTC | https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E5%B9%BF%E5%91%8A%E5%B9%B3%E5%8F%B0%E6%8B%A6%E6%88%AA%E5%99%A8.beta.sgmodule |
| Sukka reject (domainset) | core | 140726 | fresh | 2026-10-16 15:59:46 UTC | https://ruleset.skk.moe/List/domainset/reject.conf |
| Sukka reject (non_ip) | core | 369 | fresh | 2026-10-15 20:51:11 UTC | https://ruleset.skk.moe/List/non_ip/reject.conf |
| Sukka reject (ip) | core | 765 | fresh | 2026-10-15 20:51:11 UTC | https://ruleset.skk.moe/List/ip/reject.conf |
| AWAvenue-Ads-Rule (秋风) | core | 965 | fresh | 2026-10-15 20:51:11 UTC | https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main/Filters/AWAvenue-Ads-Rule-Surge-RULE-SET.list |
| 217heidai adblockfilters lite | core | 8258 | fresh | 2026-10-16 15:59:46 UTC | https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblocksurgelite.list |
| v2fly category-ads-all (MetaCubeX) | core | 902 | fresh | 2026-10-16 04:04:28 UTC | https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-ads-all.list |
| kelee 广告平台拦截器 [Rule] | core | 324 | fresh | 2026-10-15 20:51:11 UTC | https://kelee.one/Tool/Loon/Lpx/BlockAdvertisers.lpx |
| Sukka reject_extra (domainset) | extra | 78082 | fresh | 2026-10-16 15:59:46 UTC | https://ruleset.skk.moe/List/domainset/reject_extra.conf |
| HaGeZi Multi PRO (wildcard domains) | extra | 200444 | fresh | 2026-10-16 15:59:46 UTC | https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/pro-onlydomains.txt |

List upstream breakdown:

| Upstream | DOMAIN | SUFFIX | KEYWORD | WILDCARD | URL-REGEX | AND/OR | IP-CIDR |
|---|---|---|---|---|---|---|---|
| Sukka reject (domainset) | 1158 | 139568 | 0 | 0 | 0 | 0 | 0 |
| Sukka reject (non_ip) | 71 | 89 | 144 | 15 | 3 | 0 | 47 |
| Sukka reject (ip) | 1 | 0 | 0 | 0 | 0 | 0 | 764 |
| AWAvenue-Ads-Rule (秋风) | 949 | 12 | 4 | 0 | 0 | 0 | 0 |
| 217heidai adblockfilters lite | 0 | 8258 | 0 | 0 | 0 | 0 | 0 |
| v2fly category-ads-all (MetaCubeX) | 158 | 744 | 0 | 0 | 0 | 0 | 0 |
| kelee 广告平台拦截器 [Rule] | 113 | 195 | 12 | 0 | 0 | 3 | 1 |
| Sukka reject_extra (domainset) | 16 | 78066 | 0 | 0 | 0 | 0 | 0 |
| HaGeZi Multi PRO (wildcard domains) | 0 | 200444 | 0 | 0 | 0 | 0 | 0 |

- Module host-wide rejects moved into the core DOMAIN-SET: 7 (`adapi.izuiyou.com`, `api.htp.ad-scope.com.cn`, `fc-video.cdn.bcebos.com`, `sdk1xyajs.data.kuiniuca.com`, `stat.peopleapp.com`, `.kingsoft-office-service.com`, `.pglstatp-toutiao.com`)
- Raw union before filtering: core 147152, extra 236020

## Outputs

- `Reject_Domain.list`: 144327 lines
- `Reject.list`: 966 lines
- `Reject_Extra_Domain.list`: 186957 lines
- `AdBlock.sgmodule`: 1855 lines
- `AdBlock-iOS-Lite.sgmodule`: 289 lines
- `MITM-Guard.sgmodule`: 2 lines
- Reject.list breakdown: DOMAIN-KEYWORD 136, DOMAIN-WILDCARD 14, AND/OR 3, URL-REGEX 1, IP-CIDR 812
- Extra-layer entries dropped because core already covers them: 46721

## Removed by category

| Category | Removed |
|---|---|
| AI feature flags (Statsig) | 10 |
| Crash reporting used by apps you sign in to (Sentry) | 7 |
| Deep links (keep the app links in SMS / mail working) | 4 |
| Device fingerprinting for bot / fraud checks (FingerprintJS) | 25 |
| Google infrastructure | 6 |
| Noise | 2 |
| Over-broad URL-REGEX | 3 |
| Over-broad keywords | 10 |
| TikTok / ByteDance network config and IM | 41 |
| AI group (rules/AI_Domain.list) | 69 |
| must-not-block: Banks (whole tree) | 36 |
| must-not-block: Payments (whole tree) | 43 |
| public suffix / bare eTLD | 100 |

### adblock-exclude.txt

**AI feature flags (Statsig)** (10): `.api.statsigcdn.com [core]`, `.api.statsigcdn.com [extra]`, `.assetsconfigcdn.org [core]`, `.assetsconfigcdn.org [extra]`, `.events.statsigapi.net [core]`, `.featuregates.org [core]`, `.statsig.anthropic.com [core]`, `.statsigapi.net [extra]`, `api.statsig.com [core]`, `statsigapi.net [core]`

**Crash reporting used by apps you sign in to (Sentry)** (7): `.sentry-cdn.com [core]`, `.sentry-cdn.com [extra]`, `.sentry.io [core]`, `.sentry.io [extra]`, `disney.my.sentry.io [core]`, `o33249.ingest.sentry.io [core]`, `o4504926511693824.ingest.sentry.io [core]`

**Deep links (keep the app links in SMS / mail working)** (4): `.adc0219647979.page.link [extra]`, `.branch.io [extra]`, `.dtminwrj.page.link [extra]`, `.impressions.onelink.me [extra]`

**Device fingerprinting for bot / fraud checks (FingerprintJS)** (25): `.analytics.dashboard.fingerprint.com [core]`, `.api.fpjs.com [extra]`, `.c.fingerprint.com [core]`, `.fingerprintjs.com [extra]`, `.fpapi.io [core]`, `.fpapi.io [extra]`, `.fpc.fingerprint.com [core]`, `.fpcdn.io [core]`, `.fpcdn.io [extra]`, `.fpjs.io [core]`, `.fpjs.io [extra]`, `.fpjscdn.net [core]`, `.fpjscdn.net [extra]`, `.fpnpmcdn.net [core]`, `.fpnpmcdn.net [extra]`, `.fptls.com [core]`, `.fptls.com [extra]`, `.fptls2.com [core]`, `.fptls2.com [extra]`, `.fptls3.com [core]`, `.fptls3.com [extra]`, `.fptls4.com [core]`, `.fptls4.com [extra]`, `.openfpcdn.io [core]`, `.openfpcdn.io [extra]`

**Google infrastructure** (6): `.googletagmanager.com [core]`, `.gvt2.com [core]`, `.gvt2.com [extra]`, `.gvt3.com [extra]`, `DOMAIN-WILDCARD,beacons*.gvt?.com [core]`, `beacons.gvt2.com [core]`

**Noise** (2): `7h15.ru1353t.1s.m4d3.by.5ukk4w.skk.moe [core]`, `7h15.ru1353t.1s.m4d3.by.5ukk4w.skk.moe [extra]`

**Over-broad URL-REGEX** (3): `URL-REGEX,/\d+/resolve [core]`, `URL-REGEX,/\d+/sign_d [core]`, `URL-REGEX,/igd\.xml [core]`

**Over-broad keywords** (10): `DOMAIN-KEYWORD,-fin.meituan.com [core]`, `DOMAIN-KEYWORD,.bitiba. [core]`, `DOMAIN-KEYWORD,.footlocker. [core]`, `DOMAIN-KEYWORD,.stenaline. [core]`, `DOMAIN-KEYWORD,.zoohit. [core]`, `DOMAIN-KEYWORD,.zooplus. [core]`, `DOMAIN-KEYWORD,dolce-gusto. [core]`, `DOMAIN-KEYWORD,marketing.net [core]`, `DOMAIN-KEYWORD,seniorliving. [core]`, `DOMAIN-KEYWORD,this_rule_set_is_made_by_sukkaw [core]`

**TikTok / ByteDance network config and IM** (41): `.imapi-sg.isnssdk.com [core]`, `.isnssdk.com [extra]`, `.tnc-boot.tiktokv.com [extra]`, `.tnc0-normal-alisg.tiktokv.com [extra]`, `.tnc0-normal-my.tiktokv.com [extra]`, `.tnc0-normal-sg1.tiktokv.com [extra]`, `.tnc0-normal-useast1a.tiktokv.com [extra]`, `.tnc100-alisg.tiktokv.com [extra]`, `.tnc100-my.tiktokv.com [extra]`, `.tnc100-useast1a.tiktokv.com [extra]`, `.tnc100-useast2a.tiktokv.com [extra]`, `.tnc16-alisg.byteoversea.com [extra]`, `.tnc16-alisg.isnssdk.com [core]`, `.tnc16-normal-useast5.tiktokv.us [extra]`, `.tnc16-normal-useast8.tiktokv.us [extra]`, `.tnc16-normal-useast8.us.tiktokv.com [extra]`, `.tnc16-normal-zr-alisg.tiktokv.com [extra]`, `.tnc16-normal-zr-useast1a.tiktokv.com [extra]`, `.tnc16-platform-alisg.tiktokv.com [extra]`, `.tnc16-platform-my.tiktokv.com [extra]`, `.tnc16-platform-useast1a.tiktokv.com [extra]`, `.tnc16-platform-useast2a.tiktokv.com [extra]`, `.tnc16-platform-useast5.us.tiktokv.com [extra]`, `.tnc16-useast1a.byteoversea.com [extra]`, `.tnc16-useast1a.isnssdk.com [core]`, `.tnc19-normal-useast5.tiktokv.us [extra]`, `.tnc19-normal-useast8.tiktokv.us [extra]`, `.tnc3-aliec2.snssdk.com [core]`, `.tnc3-aliec2.snssdk.com [extra]`, `.tnc3-alisc1.snssdk.com [core]`, `.tnc3-alisc1.snssdk.com [extra]`, `.tnc3-bjlgy.snssdk.com [core]`, `.tnc3-bjlgy.snssdk.com [extra]`, `.tnc31-normal-zr-useast1a.tiktokv.com [extra]`, `.tnc31-platform-alisg.tiktokv.com [extra]`, `.tnc31-platform-useast1a.tiktokv.com [extra]`, `.tnc31-platform-useast2a.tiktokv.com [extra]`, `.tnc58-platform-ycru.tiktokv.com [extra]`, `tnc3-aliec2.snssdk.com [core]`, `tnc3-alisc1.snssdk.com [core]`, `tnc3-bjlgy.snssdk.com [core]`

### AI group

**AI group (rules/AI_Domain.list)** (69): `.advertising.civitai.com [extra]`, `.analytics.zed.dev [extra]`, `.browser-intake-datadoghq.com [core]`, `.browser-intake-datadoghq.com [extra]`, `.browser-intake-us5-datadoghq.com [extra]`, `.bzr.openai.com [core]`, `.bzr.openai.com [extra]`, `.bzrcdn.openai.com [core]`, `.bzrcdn.openai.com [extra]`, `.cdn.usefathom.com [extra]`, `.client-telemetry.us-east-1.amazonaws.com [extra]`, `.cloudflareinsights.com [core]`, `.cloudflareinsights.com [extra]`, `.copilot-telemetry-service.githubusercontent.com [extra]`, `.copilot-telemetry.githubusercontent.com [core]`, `.copilot-telemetry.githubusercontent.com [extra]`, `.data.microsoft.com [core]`, `.dd.huggingface.co [core]`, `.default.exp-tas.com [extra]`, `.events.api.gamma.app [core]`, `.events.api.gamma.app [extra]`, `.events.character.ai [core]`, `.events.character.ai [extra]`, `.faro.civitai.com [extra]`, `.gemini.talkai.info [extra]`, `.global-user-tracker.replit.app [extra]`, `.gnar.grammarly.com [core]`, `.gnar.grammarly.com [extra]`, `.goto.suno.com [core]`, `.goto.suno.com [extra]`, `.in.appcenter.ms [extra]`, `.m-chromadrone.prod.suno.com [core]`, `.m-chromadrone.prod.suno.com [extra]`, `.m-stratovibe.prod.suno.com [core]`, `.m-stratovibe.prod.suno.com [extra]`, `.m-zephyrtone.prod.suno.com [extra]`, `.metrics-prod.suno.com [core]`, `.metrics-prod.suno.com [extra]`, `.metrics.cursor.sh [extra]`, `.metrics.manus.im [extra]`, `.openai.qualtrics.com [extra]`, `.presale-amswallet.replit.app [extra]`, `.prod.us-east-1.telemetry-v2.kiro.dev [extra]`, `.proxima.midjourney.com [core]`, `.proxima.midjourney.com [extra]`, `.r.openai.com [extra]`, `.sentry.otter.ai [extra]`, `.sgtm.replit.com [extra]`, `.sider.ai [extra]`, `.sst.coderabbit.ai [extra]`, `.t.jasper.ai [core]`, `.t.jasper.ai [extra]`, `.telemetry.business.githubcopilot.com [extra]`, `.telemetry.desktop.kiro.dev [extra]`, `.telemetry.enterprise.githubcopilot.com [extra]`, `.telemetry.eu-central-1.kiro.dev [extra]`, `.telemetry.factory.ai [extra]`, `.telemetry.individual.githubcopilot.com [core]`, `.telemetry.individual.githubcopilot.com [extra]`, `.telemetry.openclaw.ai [extra]`, ... and 9 more

### must-not-block guard

**must-not-block: Banks (whole tree)** (36): `.adv.ccb.com [core]`, `.adv.ccb.com [extra]`, `.analytics.chase.com [core]`, `.analytics.chase.com [extra]`, `.app.uob.com.sg [extra]`, `.cdntm.ciiom.hsbc.com [extra]`, `.cdntm.expat.hsbc.com [extra]`, `.cdntm.hsbc.com.hk [extra]`, `.cdntm.us.hsbc.com [extra]`, `.content22.citibank.com [extra]`, `.content22.online.citibank.com [extra]`, `.dbsa-digital-analytics.dbs.com [extra]`, `.experimentation.chase.com [extra]`, `.fraudandcyberawareness.safeguard.hsbc.com [core]`, `.images.cmbinsight.hsbc.com [core]`, `.insight.business.hsbc.com [core]`, `.insight.gbm.hsbc.com [core]`, `.jf365.boc.cn [extra]`, `.log.cmbchina.com [core]`, `.log.cmbchina.com [extra]`, `.measure.chase.com [core]`, `.measure.chase.com [extra]`, `.metrics.citibank.com [core]`, `.metrics1.citibank.com [core]`, `.midas.chase.com [core]`, `.midas.chase.com [extra]`, `.omtr.uob.com.sg [core]`, `.pafms.ocbc.com [extra]`, `.page-format.chase.com [extra]`, `.poirot.chase.com [extra]`, `.servicing.business.hsbc.com [core]`, `.tagmanager1.citibank.com [core]`, `.target.chase.com [core]`, `.tms.data.hsbc.com [core]`, `.uafms.ocbc.com [extra]`, `adv.ccb.com [core]`

**must-not-block: Payments (whole tree)** (43): `.ablink.info.wise.com [extra]`, `.ads.95516.com [core]`, `.ads.95516.com [extra]`, `.amdc-thirdparty.alipay.com [core]`, `.amdc.alipay.com [core]`, `.analytics.95516.com [core]`, `.analytics.95516.com [extra]`, `.business.visa.com [core]`, `.client-analytics.braintreegateway.com [core]`, `.client-analytics.braintreegateway.com [extra]`, `.collect.alipay.com [core]`, `.collect.alipay.com [extra]`, `.data.account.paypal.com [core]`, `.data.fastlane-email.paypal.com [core]`, `.data.messaging.paypal.com [core]`, `.data.news.paypal.com [core]`, `.data.news.paypal.com [extra]`, `.data.newsletter.paypal.com [core]`, `.data.zettleby.paypal.com [core]`, `.errors.stripe.com [extra]`, `.gtm.wise.com [core]`, `.gtm.wise.com [extra]`, `.i.paypal.com [core]`, `.images.globalempcomm.visa.com [core]`, `.loggw-ex.alipay.com [core]`, `.loggw-ex.alipay.com [extra]`, `.loggw-exsdk.alipay.com [core]`, `.loggw-exsdk.alipay.com [extra]`, `.loggw.alipay.com [core]`, `.loggw.alipay.com [extra]`, `.metrics.mastercard.com [core]`, `.openmonitor.alipay-eco.com [core]`, `.openmonitor.alipay-eco.com [extra]`, `.openmonitor.alipay.com [core]`, `.openmonitor.alipay.com [extra]`, `.sgtm.adyen.com [extra]`, `.smetrics.mastercard.com [extra]`, `.sst.wise.com [extra]`, `.stats.paypal.com [core]`, `.thm.visa.com [extra]`, `.thm12.visa.com [extra]`, `.tracking.cpa.qa.web.visa.com [core]`, `ads.95516.com [core]`

Exclude rules with no current match (kept for future upstream changes): `DOMAIN-SUFFIX,featureassets.org`, `DOMAIN-SUFFIX,prodregistryv2.org`, `DOMAIN-SUFFIX,oaistatsig.com`, `DOMAIN-KEYWORD,sentry`, `DOMAIN-SUFFIX,app.link`, `DOMAIN-SUFFIX,test-app.link`, `DOMAIN-SUFFIX,bnc.lt`, `DOMAIN-SUFFIX,adj.st`, `DOMAIN-SUFFIX,go.link`, `DOMAIN-KEYWORD,fenxi`, `DOMAIN-KEYWORD,advert`

### Public suffix / eTLD entries

- core: 39: `.16-b.it`, `.32-b.it`, `.3utilities.com`, `.64-b.it`, `.cfolks.pl`, `.cprapid.com`, `.dkonto.pl`, `.dnsking.ch`, `.dnsup.net`, `.dynserv.org`, `.forumz.info`, `.freeddns.us`, `.hicam.net`, `.ingress-alpha.ewp.live`, `.ingress-baronn.ewp.live`, `.ingress-bonde.ewp.live`, `.ingress-comporellon.ewp.live`, `.ingress-daribow.ewp.live`, `.ingress-earth.ewp.live`, `.ingress-erytho.ewp.live`, `.ingress-florina.ewp.live`, `.ingress-haven.ewp.live`, `.myiphost.com`, `.mypi.co`, `.now-dns.net`, `.now-dns.org`, `.ntdll.top`, `.ownip.net`, `.plesk.page`, `.servebbs.net`, `.soundcast.me`, `.square.site`, `.tcp4.me`, `.try-snowplow.com`, `.vpndns.net`, `.webadorsite.com`, `.webhop.net`, `.yolasite.com`, `.you2.pl`
- extra: 61: `.3utilities.com`, `.at-band-camp.net`, `.camdvr.org`, `.ccwu.cc`, `.dfirma.pl`, `.dkonto.pl`, `.dyndns-work.com`, `.dynuddns.net`, `.fastvps-server.com`, `.for-some.biz`, `.for-the.biz`, `.from-ak.com`, `.from-al.com`, `.from-az.net`, `.from-co.net`, `.from-ga.com`, `.from-hi.com`, `.from-ia.com`, `.from-me.org`, `.from-mn.com`, `.from-mo.com`, `.from-nd.com`, `.from-nv.com`, `.from-ok.com`, `.from-or.com`, `.from-sd.com`, `.from-wv.com`, `.groks-the.info`, `.hippo2.eth.limo`, `.iamallama.com`, `.is-a-chef.net`, `.is-a-conservative.com`, `.is-a-democrat.com`, `.is-a-designer.com`, `.is-a-financialadvisor.com`, `.is-a-knight.org`, `.is-a-socialist.com`, `.is-a-soxfan.org`, `.is-a-therapist.com`, `.is-an-anarchist.com`, `.is-found.org`, `.is-slick.com`, `.is-very-good.org`, `.ju.mp`, `.live-website.com`, `.misconfused.org`, `.myjino.ru`, `.mysecuritycamera.org`, `.nflfan.org`, `.on-fleek.app`, `.pisz.pl`, `.redirectme.net`, `.ru.com`, `.saves-the-whales.com`, `.sells-it.net`, `.servebbs.org`, `.serveftp.com`, `.servesarcasm.com`, `.theworkpc.com`, `.tornadoproxy.eth.limo`, ... and 1 more

## Manual includes

`DOMAIN,business.msstatic.com`, `DOMAIN-SUFFIX,v1d.szbdyd.com`, `URL-REGEX,^http://cdn.wup.huya.com/launch/queryHttpDns$`, `IP-CIDR,0.0.0.0/32`

## Dropped rule types

- **IP-ASN** (15): `IP-ASN,1012`, `IP-ASN,14651`, `IP-ASN,18044`, `IP-ASN,401111`, `IP-ASN,5111`, `IP-ASN,54625`, `IP-ASN,60539`, `IP-ASN,60842`, `IP-ASN,61302`, `IP-ASN,62489`, `IP-ASN,62853`, `IP-ASN,7257`, `IP-ASN,7480`, `IP-ASN,7719`, `IP-ASN,945`
- **invalid domain** (2): `.data`, `DOMAIN-SUFFIX,data`
- **non-reject policy (DIRECT)** (6): `AND, ((DOMAIN-KEYWORD, tnc), (OR, ((DOMAIN-SUFFIX, capcutapi.com), (DOMAIN-SUFFIX, zijieapi.com), (DOMAIN-SUFFIX, isnssdk.com), (DOMAIN-SUFFIX, toutiaoapi.com), (DOMAIN-SUFFIX, bytedance.com), (DOMAIN-SUFFIX, snssdk.com), (DOMAIN-SUFFIX, sgsnssdk.com)))), DIRECT`, `DOMAIN, code.sms.mob.com, DIRECT`, `DOMAIN, init.sms.mob.com, DIRECT`, `DOMAIN, sdk.verification.jiguang.cn, DIRECT`, `DOMAIN, sdkapi.sms.mob.com, DIRECT`, `DOMAIN, smartop-sdkapi.jiguang.cn, DIRECT`

## Normalisation

- core: DOMAIN covered by DOMAIN-SUFFIX: 1317
- core: DOMAIN-KEYWORD covered by shorter keyword: 10
- core: DOMAIN-SUFFIX covered by broader DOMAIN-SUFFIX: 380
- core: IP-CIDR covered by broader CIDR: 1
- extra: DOMAIN covered by DOMAIN-SUFFIX: 4
- extra: DOMAIN-SUFFIX covered by broader DOMAIN-SUFFIX: 2137

## Modules

### Mac

- Sections: Body Rewrite 58, Map Local 1047, Script 264, URL Rewrite 480
- Scripts: 264 (262 requires-body); MITM hosts: 969
- Apps (646): 00bang.cn, 01zhuanche.com, 10010.cn, 10010.com, 10086.cn, 10099.com.cn, 101.42.130.147, 10101111cdn.com, 103.37.155.60, 103.41.167.237, 106.55.220.18, 10jqka.com.cn, 11222.cn, 118.178.214.118, 118.89.204.198, 122.gov.cn, 12306.cn, 1234567.com.cn, 123pan.com, 125.215.147.40, 126.net, 127.net, 1314zhilv.com, 133.cn, 139.196.12.179, 139.com, 163.com, 17kjs.com, 17u.cn, 17usoft.com, 180.96.8.44, 182.92.244.70, 189.cn, 1jietu.com, 1qianbao.com, 1rtb.net, 203.107.1.97, 21ec74.com, 21jingji.com, 2345.com, 2bulu.com, 34580.com, 360.cn, 360buyimg.com, 369cx.cn, 36kr.com, 3hxq.cn, 47.110.187.87, 4gtv.tv, 4kya.com, 500.com, 51credit.com, 51fanli.net, 51jobapp.com, 52tt.com, 54.222.159.138, 58.com, 59.82.113.10, 5eplay.com, 5idream.net, 91160.com, 95504.net, 96225.com, aa-ab.com, abite.com, acfun.cn, admobile.top, adukwai.com, adview.cn, ahmobile.cn, ahzs10000.com, aia.com.cn, aihuishou.com, ailbaba.me, alibaba.com, alibabausercontent.com, alicdn.com, alipan.com, aliyuncs.com, allahall.com, amap.com, amazon.cn, amemv.com, anythinktech.com, aomiapp.com, appsimg.com, appvipshop.com, autohome.com.cn, autoimg.cn, awtmt.com, babytree.com, babytreeimg.com, badmintoncn.com, baicizhan.com, baidu.com, baidupcs.com, banyuetanapp.com, bcebos.com, bczeducation.cn, bdatu.com, bdstatic.com, beitaichufang.com, benewtech.cn, benlailife.com, bestv.cn, bestv.com.cn, bevol.com, biguotk.com, biligame.com, binance.com, bishijie.com, bitqiu.com, bjev.com.cn, bjxkhc.com, black-unique.com, blibee.com, blued.cn, boohee.com, bwton.com, bybutter.com, bydauto.com.cn, bytescm.com, caijingmobile.com, cainiao.com, caixin.com, caiyicloud.com, caiyunapp.com, camera360.com, caocaokeji.cn, cdnmama.com, cdtft.cn, ceair.com, cgmcare.cn, cgws.com, chaoxing.com, chelaile.net.cn, chelaileapp.cn, chengdu.gov.cn, chery.cn, chinafamilymart.com.cn, chinahxzq.com.cn, chinastock.com.cn, chuangkit.com, cibfintech.com, closeli.cn, cloudbae.cn, cls.cn, cmgadx.com, cmschina.com, cnki.net, cntaiping.com, cntv.cn, coolapk.com, cotticoffee.com, cp.com.cn, csair.com, csdn.net, ctaiot.com, ctm.net, ctobsnssdk.com, ctrip.com, cyapi.cn, d3yuiw4.com, dailmo.com, dangdang.com, daydaycook.com.cn, dcloud.net.cn, ddpai.com, ddrk.me, ddxq.mobi, dewu.com, dfcfw.com, dian.so, dianping.com, dianshihome.com, didapinche.com, didistatic.com, diditaxi.com.cn, djiits.com, dnurse.com, dongdianqiu.com, dongfeng-nissan.com.cn, douban.com, doubleclick.net, douyin.com, douyucdn.cn, dpfile.com, dsocial.xyz, dushu365.com, duxiaoman.com, dxy.cn, dxy.com, dyncdn.me, dzh.com.cn, eastmoney.com, echargenet.com, ecitic.com, ecoliving168.com, edaijia.cn, edifier.com, edit.sinaapp.com, ele.me, elecfans.com, elemecdn.com, elong.com, enmonster.com, eol.cn, epicc.com.cn, etnet.com.hk, faw-vw.com, fcbox.com, feidee.com, feidee.net, fenbi.com, fengshows.cn, fengshows.com, fenqile.com, fitdays.cn, flipchina.cn, flydigi.com, flymodem.com.cn, folidaymall.com, fosunhanig.com, freshippo.com, ftms.com.cn, futunn.com, gacmotor.com, gamer.com.tw, gamersky.com, gaoding.com, gaoqingdianshi.com, gcores.com, gdoil.cn, geely.com, gifshow.com, go189.cn, gome.com.cn, gongkaoleida.com, goofish.com, googleadservices.com, googlesyndication.com, gotokeep.com, gtimg.cn, gtimg.com, gtja.com, guahao.cn, guahao.com, guiderank-app.com, gwmapp-w.com, hafoo.com, haiersmarthomes.com, haixue.com, hannto.com, haohaozhu.cn, hbooker.com, hgold.cn, hilton.com.cn, hiyun.tv, homeinns.com, hongyibo.com.cn, hoopchina.com.cn, hpoi.net.cn, hpplay.cn, hstong.com, htsc.com, huachenjie.com, huami.com, huatu.com, huazhu.com, hubcloud.com.cn, huomao.com, hupu.com, hupucdn.com, huxiu.com, huya.com, hyhuo.com, i18n-pglstatp.com, i3zh.com, i4.cn, ibuscloud.com, icc.one, iciba.com, iconntech.com, icourse163.org, ictun.com, ifanr.com, igetcool.com, igetget.com, igpsport.com, imdada.cn, imlaidian.com, indeedpower.com, inke.cn, internetofcity.cn, iqihang.com, iqiyi.com, ireader.com, ireader.mobi, ireaderm.net, ithome.com, iyingdi.cn, iyunmai.com, izuiyou.com, jampp.com, jd.com, jdcloud.com, jetour.com.cn, jiantou8.com, jiediankeji.com, jiemian.com, jin10.com, jumpvg.com, juneyaoair.com, juxingclub.com, jxedt.com, kakamobi.cn, kaola.com, kaolacdn.com, ke.com, keepcdn.com, kfc.com.cn, kingsoft-office-service.com, kkmh.com, koudaibaobao.com, ksapisrv.com, ksedt.com, kuaidadi.com, kuaidi100.com, kuaishou.cn, kuaishou.com, kujiale.com, kurobbs.com, kuwo.cn, laichon.com, laifeng.com, lanjiyin.com.cn, lantouzi.com, lbdj.com, leapmotor.cn, lechange.cn, leisuapi.com, lenovo.cn, lenovoimage.com, leoao.com, lf127.net, liepin.com, lifeweek.com.cn, line-apps.com, line-scdn.net, line.me, linecorp.com, livelab.com.cn, lkcoffee.com, llsapp.com, lofter.com, longfor.com, luckincoffeecdn.com, lucklyworld.com, lvcchong.com, lz-qs.com, mafengwo.cn, manhuaren.*, manhuaren.com, manhuashe.com, markiapp.com, mcd.cn, mddcloud.com.cn, medlive.cn, medsci.cn, meitu.com, meituan.com, meituan.net, meitudata.com, meitun.com, merach.com, meruki.cn, mgtv.com, mgzf.com, mi.com, miaopai.com, midukanshu.com, migu.cn, miguvideo.com, mihoyo.com, missevan.com, missfresh.cn, mitvos.com, miyoushe.com, mob.com, moedot.net, msstatic.com, msyc.cc, mting.info, mucang.cn, mwee.cn, mxbc.net, my.com, myfriday.cn, mygolbs.com, mylyg.net, mypikpak.com, myusmile.online, narwaltech.com, naver.com, naver.jp, nbtv.cn, ncarzone.com, netease.com, nfmovies.com, ngchina.cn, nhsa.gov.cn, nilbt.com, niu.com, oclean.com, ofo.com, onethingpcs.com, onewo.com, onstar.com.cn, openspeech.cn, oray.com, oray.net, oschina.net, palmestore.com, panda.tv, pangolin-sdk-toutiao-b.com, pangolin-sdk-toutiao.*, pangolin-sdk-toutiao.com, pansearch.me, paojd.cn, pcauto.com.cn, pconline.com.cn, pddpic.com, peopleapp.com, perfectlingo.com, petkit.cn, pglstatp-toutiao.com, picooc.com, pinduoduo.com, pipi.cn, pixiv.net, pizzahut.com.cn, pocketuni.net, pstatp.com, psy-1.com, pupuapi.com, qbb6.com, qd-metro.com, qdaily.com, qeeniao.com, qidian.com, qingcdn.com, qinlinad.com, qiumibao.com, qjjfin.com, qmai.cn, qpic.cn, qq.com, qunar.com, qweather.net, qyer.com, radio.cn, ranfenghd.com, realtech-inc.com, rfsvr.net, rr.tv, rsscc.com, sdb.com.cn, sdo.com, seewo.com, seeyouyima.com, sensorsdata.cn, sf-express.com, sfacg.com, sfbest.com, shanghaionstar.com, shenyin.name, shenzhentong.com, shihuo.cn, shihuocdn.cn, shouqiev.com, shunchangzhixing.com, shuqireader.com, shuqistat.com, sigmob.cn, simshine.cn, sina.cn, sinopec.com, sinopecsales.com, sljkj.com, sm.cn, smzdm.com, snailsleep.net, snssdk.com, sodalife.xyz, sogaha.cn, sogou.com, soulapp.cn, soulapp.me, soutushenqi.com, sparke.cn, spotify.com, sqcosmos.com, ssjlicai.com, sspai.com, suh.cn, suning.com, suzhou.gov.cn, szsmk.com, szy.cn, tailgdd.com, taobao.com, taou.com, taptapdada.com, teamair.cn, tf.cn, thepaper.cn, tianmu.mobi, tipatipa.xyz, tipsoon.com, tmuyun.com, touker.com, toutiao.com, tratao.com, truthsocial.com, tsytv.com.cn, tuitiger.com, tujia.com, tuniu.com, txcmapp.com, txffp.com, u51.com, ubixioe.com, uc.cn, ulife.group, umetrip.com, usmile.com, variflight.com, versa-ai.com, vistastory.com, vistopia.com.cn, wacaijizhang.com, wallstreetcn.com, walmartmobile.cn, wandafilm.com, watsonsvip.com.cn, weather.com.cn, weathercn.com, weibo.cn, weibo.com, weico.cc, weidian.com, wenhua.com.cn, wfdata.club, wifi188.com, wifi8.com, winbull8.com, wind.com.cn, wmpvp.com, wps.cn, wting.info, wtzw.com, wukongtv.com, wuta-cam.com, xbwpys.com, xbxxhz.com, xcultur.com, xczim.com, xgimi.com, xiachufang.com, xiamenair.com, xiaoaisound.com, xiaocantech.com, xiaofubao.com, xiaoheihe.cn, xiaohongshu.com, xiaojukeji.com, xiaomi.com, xiaote.net, xiaotucc.com, xiaoxiaoyouxuan.com, xiaoxiongmeishu.com, xiaoyi.com, xiaoyuzhoufm.com, xiaozujian.com, xima.*, ximalaya.com, xinmanhua.net, xinpianchang.com, xmcdn.com, xmseeyouyima.com, xoyo.com, xqpark.cn, xueqiu.com, xunlei.com, xycdn.com, xyzq.cn, yaduo.com, yahoo.com, yangkeduo.com, ydstatic.com, yhd.com, yiche.com, yikaobang.com.cn, yinxiang.com, ykccn.com, ylyk.com, ymm56.com, yonghuivip.com, yorentown.com, youdao.com, youku.com, youonbike.com, youshu.cc, ys7.com, yuanfudao.com, yuebuy.cn, yuxueyuan.cn, yxzq.com, zbj.com, zcool.com.cn, zdmimg.com, zeekstudio.com, zhangle.com, zhangyue.com, zhangyue.net, zhaojinapp.com, zhengqi100.com, zhidiantianxia.cn, zhiduodev.com, zhihu.com, zhijianmedia.cn, zhinengxiyifang.cn, zhoudamozi.com, zhuanzhuan.com, zhumanggroup.com, ziben.com, ziroom.com, zjdr666.com, zjzwfw.gov.cn, zol.com.cn, zongheng.com, ztehome.com.cn, zto.com, zuche.com, zuoyebang.com, zybang.com

### iOS Lite

- Sections: Body Rewrite 10, Map Local 170, Script 30, URL Rewrite 73
- Scripts: 30 (30 requires-body); MITM hosts: 100
- Apps (17): 高德地图 (partial: 18 of 21 entries), 小红书 (partial: 22 of 28 entries), 微博 (partial: 22 of 39 entries), 知乎 (partial: 43 of 55 entries), 网易云音乐 (partial: 22 of 39 entries), 喜马拉雅 (partial: 39 of 44 entries), 微信公众号 / 小程序, 拼多多广告链, 菜鸟 (partial: 14 of 21 entries), 美团 / 大众点评 (partial: 30 of 32 entries), 饿了么, 京东 (non-payment hosts), 百度地图 / 百度网盘 (partial: 15 of 16 entries), 爱奇艺 (partial: 4 of 17 entries), 优酷 (partial: 2 of 8 entries), 芒果TV (partial: 8 of 16 entries), 腾讯视频 / 腾讯新闻 (partial: 2 of 3 entries)

- Skipped: 12306 (budget), 什么值得买 (budget), 彩云天气 (budget), 酷安 (budget), 携程 / 去哪儿 (budget), 滴滴 (budget), 顺丰 (budget), 中国移动 (budget)

### Module entries dropped

| Reason | Count | Examples |
|---|---|---|
| ddgksf2013-startingad: delegated to dedicated module (Bilibili (kokoryh/Sparkle bilibili.sgmodule)) | 1 | `^https?:\/\/api-access\.[0-9a-zA-Z_-]+\.com\/api\/ad` |
| ddgksf2013-startingad: duplicate pattern | 8 | `^https?:\/\/.*zdmimg\.com\/cpm\/api\/v\d\/advert_distribution\/get_all_advertise`, `^http:\/\/amdc\.m\.taobao\.com`, `^https?:\/\/api.coolapk.com\/v6\/main\/init` |
| ddgksf2013-startingad: host-agnostic or unparseable URL pattern | 12 | `^https?:\/\/m\.mynj\.cn:\d+\/znmh_FEP\/loadpic\.jsp.*ad_pic.*open _ reject`, `fly=type=http-response,pattern=^https?:\/\/.*flyert.*\/source\/plugin\/mobile\/m`, `weibo_json20=type=http-response,pattern=^https?://(sdk\|wb)app\.uve\.weibo\.com(/` |
| ddgksf2013-startingad: inactive upstream (no matching MITM hostname) | 39 | `hanglvzongheng=type=http-response,pattern=^https?:\/\/.*umetrip\.com\.cn\/gatewa`, `abchina=type=http-response,pattern=^https?:\/\/mobilepaas\.abchina\.com\.cn:441\`, `caiyun_json=type=http-response,pattern=^https?:\/\/biz\.cyapi\.cn\/api\/v\d\/use` |
| ddgksf2013-startingad: lint: empty or malformed script parameter '4}(:\\d+)?\\/amdc\\/mobileDispatch' | 1 | `amdc=type=http-response,pattern=^http:\/\/[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){1,4}(` |
| ddgksf2013-startingad: lint: empty or malformed script parameter '4}(:\\d+)?\\/api\\/v\\d\\/movie\\/index_recommend' | 1 | `555Ad=type=http-response,pattern=^https?:\/\/[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){1,` |
| ddgksf2013-startingad: lint: empty or malformed script parameter '}(:\\d+)?/wp-json/[a-zA-Z0-9_-]+/(mp\\/)?v\\d/posts' | 1 | `applet=type=http-response,pattern=^(https?://)?([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+` |
| ddgksf2013-startingad: malformed Script (QX syntax / missing pattern or script-path) | 1 | `zheye.min2=type=http-response,pattern=^https?:\/\/api\.zhihu\.com\/feed-root\/bl` |
| ddgksf2013-startingad: never-MITM host *.1rtb.net (matches (over-broad wildcard)) | 2 | `^https?:\/\/sdk\.1rtb\.net\/sdk\/req_ad`, `^https?:\/\/.*1rtb\.net\/sdk\/req_ad\?` |
| ddgksf2013-startingad: never-MITM host acs.m.taobao.com (matches acs.m.taobao.com) | 17 | `^https?:\/\/acs\.m\.taobao\.com\/gw\/mtop\.alibaba\.advertisementservice\.getadv`, `^https?:\/\/acs\.m\.taobao\.com\/gw\/mtop\.alibaba\.cbu\.app\.homepage\.startup`, `^https?:\/\/acs\.m\.taobao\.com\/gw\/mtop\.damai\.wireless\.home\.welcome` |
| ddgksf2013-startingad: never-MITM host adv.ccb.com (matches *.ccb.com) | 1 | `^https?:\/\/adv\.ccb\.com\/ebda\/ctm_adv` |
| ddgksf2013-startingad: never-MITM host api.jk.cn (matches *.jk.cn) | 1 | `^https?:\/\/api\.jk\.cn\/m\.api` |
| ddgksf2013-startingad: never-MITM host api.m.jd.com (matches api.m.jd.com) | 4 | `^https?:\/\/api\.m\.jd\.com\/api\?functionId=delivery_show`, `^https?:\/\/api\.m\.jd\.com\/client\.action\?functionId=(hotWords\|hotSearchTerms`, `^https?:\/\/api\.m\.jd\.com\/client\.action\?functionId=(start\|queryMaterialAdve` |
| ddgksf2013-startingad: never-MITM host api.msn.com (matches api.msn.com) | 1 | `^https?:\/\/api\.msn\.com\/weather` |
| ddgksf2013-startingad: never-MITM host assets.msn.com (matches assets.msn.com) | 2 | `^https?:\/\/assets\.msn\.com\/service\/weather\/locations\/search`, `^https:\/\/assets\.msn\.com\/service\/news\/feed\/pages\/startmhp` |
| ddgksf2013-startingad: never-MITM host creditcardapp.bankcomm.cn (matches *bank*) | 1 | `^https?:\/\/creditcardapp\.bankcomm\.cn\/mappweb_interface\/common\/(qryPopAds\|q` |
| ddgksf2013-startingad: never-MITM host creditcardapp.bankcomm.com (matches *bank*) | 2 | `^https?:\/\/creditcardapp\.bankcomm\.com\/mapp\/common\/(queryGuidePageAds\|getPo`, `^https?:\/\/creditcardapp\.bankcomm\.com\/mappweb.*(Advert\|Ads).do` |
| ddgksf2013-startingad: never-MITM host guide-acs.m.taobao.com (matches guide-acs.m.taobao.com) | 2 | `^https?:\/\/guide-acs\.m\.taobao\.com\/gw\/mtop\.taobao\.wireless\.home\.splash\`, `^https?:\/\/guide-acs\.m\.taobao\.com\/gw\/mtop\.fc\.resource\.tacdata\.get` |
| ddgksf2013-startingad: never-MITM host lban.spdb.com.cn (matches *.spdb.com.cn) | 1 | `^https?:\/\/lban\.spdb\.com\.cn\/mspmk-web-component\/(getAdvList\|prefetchAdvLis` |
| ddgksf2013-startingad: never-MITM host m.stock.pingan.com (matches *.pingan.com) | 1 | `^https?:\/\/m\.stock\.pingan\.com\/restapi\/rmd\/open\/O\/api\/openAd` |
| ddgksf2013-startingad: never-MITM host mpos-pic.helipay.com (matches *.helipay.com) | 1 | `^https?:\/\/mpos-pic\.helipay\.com\/upload\/images\/advertisment` |
| ddgksf2013-startingad: never-MITM host sapphire.api.microsoftapp.net (matches *.api.microsoftapp.net) | 1 | `^https?:\/\/sapphire\.api\.microsoftapp\.net\/config\/api\/v1\/get` |
| ddgksf2013-startingad: never-MITM host yunbusiness.ccb.com (matches *.ccb.com) | 1 | `^https?:\/\/yunbusiness\.ccb\.com\/clp_service\/txCtrl\?txcode=A3341A00(2\|9)` |
| ddgksf2013-startingad: script hosted outside GitHub/jsDelivr (royal-block-f6b1.q00.workers.dev) | 16 | `redbook.ads=type=http-response,pattern=^https?:\/\/[a-z]+\.xiaohongshu\.com\/api`, `redbook.ads2=type=http-response,pattern=^https?:\/\/[a-z]+\.xiaohongshu\.com\/ap`, `redbook.ads3=type=http-response,pattern=^https?:\/\/[a-z]+\.xiaohongshu\.com\/ap` |
| fmz200-blockads: body processor on a host already scripted by a higher-precedence source | 59 | `^https:\/\/j1\.pupuapi\.com\/client\/notification\/message_center\/unread_number`, `^https:\/\/api\.zhihu\.com\/search\/recommend_query\/v2\?`, `^https:\/\/api\.zhihu\.com\/search\/recommend_query\/v2\?` |
| fmz200-blockads: delegated to dedicated module (Bilibili (kokoryh/Sparkle bilibili.sgmodule)) | 30 | `^https:\/\/grpc\.biliapi\.net\/bilibili\.app\.(interface\.v1\.(Teenagers\/ModeSt`, `^https:\/\/api\.bilibili\.com\/x\/pd-proxy\/tracker\?`, `^https:\/\/api\.bilibili\.com\/pgc\/view\/v2\/app\/season\?` |
| fmz200-blockads: delegated to dedicated module (YouTube (Maasea YouTube.Enhance)) | 5 | `^https?:\/\/.+\.googleapis.com/.+ad_break`, `^https?:\/\/.+\.googleapis.com/.+log_event`, `^https?:\/\/.+\.googleapis.com/adsmeasurement` |
| fmz200-blockads: duplicate pattern | 133 | `^https?:\/\/api\.vistopia\.com\.cn\/api\/v\d\/home\/advertisement`, `^https?:\/\/daoyu\.sdo\.com\/api\/userCommon\/getAppStartAd`, `^https:\/\/acs\.m\.goofish\.com\/gw\/mtop\.taobao\.idle\.playboy\.recommend\/1\.` |
| fmz200-blockads: host-agnostic or unparseable URL pattern | 39 | `^https?:\/\/[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+){1,3}(:\d+)?\/api\/v\d\/advert - rejec`, `^https?:\/\/appapi\.huazhu\.com:\d+\/client\/app\/getAppStartPage\/ - reject`, `^https?:\/\/.*\/yyting\/advertclient\/ClientAdvertList.action - reject` |
| fmz200-blockads: inactive upstream (no matching MITM hostname) | 103 | `^https?:\/\/als\.baidu\.com\/clog\/clog - reject`, `^https?:\/\/log.+?baidu\.com - reject`, `^https?:\/\/js-ad\.ayximgs\.com\.ad-universe-cdn\.hzhcbkj\.cn\/xgapp\.php\/v2\/t` |
| fmz200-blockads: lint: invalid regex (bad escape \c at position 26) | 1 | `^https?:\/\/res\.kfc\.com.\cn\/advertisement\/ - reject` |
| fmz200-blockads: lint: unbalanced quoting (a quote opened inside a field swallows the next field) | 1 | `http-response ^https?:\/\/beta-api\.crunchyroll\.com\/cms offset_ms":\d+ offset_` |
| fmz200-blockads: never-MITM host *.17u.cn (matches (over-broad wildcard)) | 6 | `^https?:\/\/wx\.17u\.cn\/xcxhomeapi\/((aggregator\/index)\|(home\/(screen\|banner\|`, `^https:\/\/mada-travel\.17u\.cn\/mdapi\/config\/ads`, `^https:\/\/mada-travel\.17u\.cn\/mdapi\/config\/mine` |
| fmz200-blockads: never-MITM host *.58cdn.com.cn (matches (over-broad wildcard)) | 1 | `^https?:\/\/.+?\.58cdn\.com\.cn\/brandads\/` |
| fmz200-blockads: never-MITM host *.ly.com (matches (over-broad wildcard)) | 1 | `^https:\/\/mobileapi\.ly\.com\/wlfrontend\/app\/scenicMain` |
| fmz200-blockads: never-MITM host 119.29.29.* (matches (over-broad wildcard)) | 1 | `^https?:\/\/119\.29\.29\.\d+\/d` |
| fmz200-blockads: never-MITM host acs.m.taobao.com (matches acs.m.taobao.com) | 31 | `^https?:\/\/acs(\.\|-)m\.(taobao\|freshippo)\.com\/gw\/mtop\.wdk\.hippotown\.tabba`, `^https?:\/\/acs\.m\.taobao\.com\/gw\/mtop\.film\.mtopadvertiseapi\.(queryadverti`, `^https?:\/\/acs\.m\.taobao\.com\/gw\/mtop\.alimusic\.common\.mobileservice\.star` |
| fmz200-blockads: never-MITM host ad.ysepay.com (matches *.ysepay.com) | 1 | `^https?:\/\/ad\.ysepay\.com\/yst-ad\/ST101001\/[0-9]{11}\.jpg` |
| fmz200-blockads: never-MITM host ads.ysepay.com (matches *.ysepay.com) | 1 | `^https:\/\/ads\.ysepay\.com\/ads\/ctrl\/getAdvertisingInfo` |
| fmz200-blockads: never-MITM host api.m.jd.com (matches api.m.jd.com) | 6 | `^https?:\/\/api\.m\.jd\.com\/client\.action\?functionId=getWidgetV1052`, `^https?:\/\/api\.m\.jd\.com\/client\.action\?functionId=lite_advertising`, `^https?:\/\/api\.m\.jd\.com\/client\.action\?functionId=lite_SmartPush` |
| fmz200-blockads: never-MITM host app.95598pay.com (matches *.95598pay.com) | 1 | `^https?:\/\/app\.95598pay\.com\/debapi\/adsite\/` |
| fmz200-blockads: never-MITM host ccmsupport-sz.tenpay.com (matches *.tenpay.com) | 1 | `^https?:\/\/ccmsupport-sz\.tenpay\.com\/cgi-bin\/common\/ccm_page_element.cgi` |
| fmz200-blockads: never-MITM host cdn-xyk-app.bankofbeijing.com.cn (matches *bank*) | 1 | `^https?:\/\/cdn-xyk-app\.bankofbeijing\.com\.cn\/cdn\/resource\/image\/advertise` |
| fmz200-blockads: never-MITM host cdn.jlbank.com.cn (matches *bank*) | 1 | `^https?:\/\/cdn\.jlbank\.com\.cn\/jlstaticresource\/APPSTART` |
| fmz200-blockads: never-MITM host cdnmobibank.bankofbeijing.com.cn (matches *bank*) | 1 | `^https?:\/\/cdnmobibank\.bankofbeijing\.com\.cn\/cdn\/MarketingCloud\/.+\/.+\/99` |
| fmz200-blockads: never-MITM host cgbank.oss-cn-shenzhen.aliyuncs.com (matches *bank*) | 1 | `^https?:\/\/cgbank\.oss-cn-shenzhen\.aliyuncs\.com\/visual\/advertisingImg\/.+.j` |
| fmz200-blockads: never-MITM host creditcard.bankcomm.cn (matches *bank*) | 1 | `^https?:\/\/creditcard\.bankcomm\.(com\|cn)\/tfimg\/public00\/M00\/[a-zA-Z0-9]{2}` |
| fmz200-blockads: never-MITM host creditcardapp.bankcomm.cn (matches *bank*) | 3 | `^https?:\/\/creditcardapp\.bankcomm\.(com\|cn)\/mappweb_interface\/common\/(qryPo`, `^https?:\/\/creditcardapp\.bankcomm\.(com\|cn)\/mappweb_interaction\/appInfo\/app`, `^https?:\/\/creditcardapp\.bankcomm\.(com\|cn)\/rcg\/index\.html\?callbackurl=rcg` |
| fmz200-blockads: never-MITM host direct.z-bank.com (matches *bank*) | 1 | `^https?:\/\/direct\.z-bank\.com\/portal\/AdvertImageDownLoad4Mobile\.do` |
| fmz200-blockads: never-MITM host elife.icbc.com.cn (matches *.icbc.com.cn) | 1 | `^https?:\/\/elife\.icbc\.com\.cn\/OFSTNEWBASE\/floorinfo\/getMantlePages\.do` |
| fmz200-blockads: never-MITM host enjoy.cdn-static.abchina.com (matches *.abchina.com) | 1 | `^https?:\/\/enjoy\.cdn-static\.abchina\.com\/yx-engine-web\/file\/download\/(?!7` |
| fmz200-blockads: never-MITM host gmp.lakala.com (matches *.lakala.com) | 1 | `^https:\/\/(?:gmp\|wallet)\.lakala\.com\/(?:gmp\/openapi\/v2\/resource_space\/get` |
| fmz200-blockads: never-MITM host guide-acs.m.taobao.com (matches guide-acs.m.taobao.com) | 7 | `^https?:\/\/guide-acs\.m\.taobao\.com\/gw\/mtop\.cainiao\.guoguo\.nbnetflow\.ads`, `^https:\/\/guide-acs\.m\.taobao\.com\/gw\/mtop\.cainiao\.adx\.flyad\.getad`, `^https:\/\/guide-acs\.m\.taobao\.com\/gw\/mtop\.taobao\.(volvo\.secondfloor\.get` |
| fmz200-blockads: never-MITM host hcz-member.pingan.com.cn (matches *.pingan.com.cn) | 1 | `^https?:\/\/hcz-member\.pingan\.com\.cn\/micro-api\/homepage\/do\/app\/popbox\/g` |
| fmz200-blockads: never-MITM host image.spdbccc.com.cn (matches *.spdbccc.com.cn) | 1 | `^https?:\/\/image\.spdbccc\.com\.cn\/group\d\/M00\/[A-Z0-9]{2}\/[A-Z0-9]{2}\/.+(` |
| fmz200-blockads: never-MITM host imcs.citicbank.com (matches *bank*) | 2 | `^https:\/\/imcs\.citicbank\.com\/cloud\/([a-fA-F0-9]{32})\.(jpg\|png)`, `^https?:\/\/imcs\.citicbank\.com\/cloud\/.+(1125.+2436\|1242.+2688\|750.+1638\|563.` |
| fmz200-blockads: never-MITM host intellicc.bas.cmbchina.com (matches *.cmbchina.com) | 1 | `^https?:\/\/intellicc\.bas\.cmbchina\.com\/Edge\/api\/mlife\.intelli\.render\.ap` |
| fmz200-blockads: never-MITM host intellicc.bcs.cmbchina.com (matches *.cmbchina.com) | 1 | `^https?:\/\/intellicc\.bcs\.cmbchina\.com\/Edge\/api\/mlife\.intelli\.adrender\.` |
| fmz200-blockads: never-MITM host iobs.pingan.com.cn (matches *.pingan.com.cn) | 2 | `^https?:\/\/iobs\.pingan\.com\.cn\/download\/bweb-per-sf-prd\/bweb`, `^https?:\/\/iobs\.pingan\.com\.cn\/download\/icore-aops-base-dmz-prd\/(YourSyste` |
| fmz200-blockads: never-MITM host lban.spdb.com.cn (matches *.spdb.com.cn) | 3 | `^https?:\/\/lban\.spdb\.com\.cn\/mspmk-web-component\/getAdvList\.ah$`, `^https?:\/\/lban\.spdb\.com\.cn\/mspmk-web-component\/getAdvertisementList\.ah`, `^https?:\/\/lban\.spdb\.com\.cn\/mspmk-web-component\/prefetchAdvList\.ah` |
| fmz200-blockads: never-MITM host m.prod.app.hsbcfts.com.cn (matches *.hsbcfts.com.cn) | 1 | `^https?:\/\/m\.prod\.app\.hsbcfts\.com\.cn\/api\/sapp\/biz\/config\/open\/querya` |
| fmz200-blockads: never-MITM host mapi-app.bestpay.com.cn (matches *.bestpay.com.cn) | 2 | `^https?:\/\/mapi-app\.bestpay\.com\.cn\/gapi\/appclient\/noEnc\/getAppPopup`, `^https?:\/\/mapi-app\.bestpay\.com\.cn\/gapi\/appClient\/noEnc\/getHomePageAds` |
| fmz200-blockads: never-MITM host mbank.grcbank.com (matches *bank*) | 1 | `^https?:\/\/mbank\.grcbank\.com\/ydyh\/resources\/startpage\/.*.(jpg\|png)` |
| fmz200-blockads: never-MITM host mbank5.jsbchina.cn (matches *bank*) | 1 | `^https?:\/\/mbank5\.jsbchina\.cn:443` |
| fmz200-blockads: never-MITM host mbasecc.bas.cmbchina.com (matches *.cmbchina.com) | 1 | `^https?:\/\/mbasecc\.(bas\|bcs)\.cmbchina\.com\/Edge\/api\/mlife\.clientface\.cli` |
| fmz200-blockads: never-MITM host mbmodule-openapi.paas.cmbchina.com (matches *.cmbchina.com) | 1 | `^https?:\/\/mbmodule-openapi\.paas\.cmbchina\.com\/graphic\/v2\/module\/graphic` |
| fmz200-blockads: never-MITM host midc.cdn-static.abchina.com.cn (matches *.abchina.com.cn) | 1 | `^https?:\/\/midc\.cdn-static\.abchina\.com\.cn\/distributecenterimg\/file\/downl` |
| fmz200-blockads: never-MITM host mlife.jf365.boc.cn (matches *.boc.cn) | 1 | `^https?:\/\/mlife\.jf365\.boc\.cn\/AppPrj\/FirstPic\.do\?txnId=2PIC000001` |
| fmz200-blockads: never-MITM host mobile.cebbank.com (matches *bank*) | 1 | `^https?:\/\/mobile\.cebbank\.com\/cebclient\/ClientNoticeList` |
| fmz200-blockads: never-MITM host mpos-pic.helipay.com (matches *.helipay.com) | 1 | `^https?:\/\/mpos-pic\.helipay\.com\/upload\/images\/advertisment\/image` |
| fmz200-blockads: never-MITM host mps.95508.com (matches *.95508.com) | 1 | `^https?:\/\/mps\.95508\.com\/mps\/club\/cardPortals\/adv\/\d{25}\.(png\|jpg)` |
| fmz200-blockads: never-MITM host mres.aibank.com (matches *bank*) | 1 | `^https?:\/\/mres\.aibank\.com\/app\/resource\/cim\/cim0000001\/.+\.jpg` |
| fmz200-blockads: never-MITM host openapi.boc.cn (matches *.boc.cn) | 1 | `^https?:\/\/openapi\.boc\.cn\/unlogin\/app\/cbsp\/query_ad_list` |
| fmz200-blockads: never-MITM host pacdn.m.stock.pingan.com (matches *.pingan.com) | 1 | `^https?:\/\/pacdn\.m\.stock\.pingan\.com\/images\/` |
| fmz200-blockads: never-MITM host promote-trx.helipay.com (matches *.helipay.com) | 1 | `^https?:\/\/promote-trx\.helipay\.com\/promote-business-client\/pos\/appAdvertis` |
| fmz200-blockads: never-MITM host pv.elife.icbc.com.cn (matches *.icbc.com.cn) | 1 | `^https?:\/\/pv\.elife\.icbc\.com\.cn\/OFSTPV\/utm\.gif` |
| fmz200-blockads: never-MITM host rs.creditcard.cmbc.com.cn (matches *.cmbc.com.cn) | 1 | `^https?://rs.creditcard.cmbc.com.cn/mmc/img/126f35586ece469aa2daf2e451ba7b4d.jpg` |
| fmz200-blockads: never-MITM host static.95508.com (matches *.95508.com) | 4 | `^https?:\/\/static\.95508\.com\/mmg\/images\/ads\/.+\/(.+1125?.+2436\|.+%.+%\|.+_.`, `^https?:\/\/static\.95508\.com\/mmg\/ciop\/sysabbr\/cmep\/images\/(apppopupads\|p`, `^https?:\/\/static\.95508\.com\/icppweb\/images\/modelMaterial\/accurate\/202\d{` |
| fmz200-blockads: never-MITM host static.creditcard.hxb.com.cn (matches *.hxb.com.cn) | 1 | `^https?:\/\/static\.creditcard\.hxb\.com\.cn\/mcube\/apps\/group\d\/M00\/00\/2[A` |
| fmz200-blockads: never-MITM host static.mobile-bank.psbc.com (matches *bank*) | 1 | `^https?:\/\/static\.mobile-bank\.psbc\.com\/mgs` |
| fmz200-blockads: never-MITM host v.icbc.com.cn (matches *.icbc.com.cn) | 1 | `^https?:\/\/v\.icbc\.com\.cn\/userfiles\/Resources\/WAP\/advertisement\/` |
| fmz200-blockads: never-MITM host wap.spdb.com.cn (matches *.spdb.com.cn) | 1 | `^https?:\/\/wap\.spdb\.com\.cn\/mspmk-web-homeassist\/OpenScreenAdv\.ah$` |
| fmz200-blockads: never-MITM host webappcfg.paas.cmbchina.com (matches *.cmbchina.com) | 1 | `^https?:\/\/webappcfg\.paas\.cmbchina\.com\/v\d\/func\/getmarketconfig` |
| fmz200-blockads: never-MITM host www.cmbc.com.cn (matches *.cmbc.com.cn) | 2 | `^https?:\/\/www\.cmbc\.com\.cn\/m\/image\/loadingpage\/`, `^https?:\/\/www\.cmbc\.com\.cn\/m\/image\/banner\/.*.png` |
| fmz200-blockads: never-MITM host yghsh.cebbank.com (matches *bank*) | 1 | `^https?:\/\/yghsh\.cebbank\.com\/static\/picture\/.*.jpg` |
| fmz200-blockads: never-MITM host yunbusiness.ccb.com (matches *.ccb.com) | 5 | `^https?:\/\/yunbusiness\.ccb\.com\/basic_service\/txCtrl\?`, `^https?:\/\/yunbusiness\.ccb\.com\/clp_service\/txCtrl\?txcode=A3341A(002\|006\|00`, `^https?:\/\/yunbusiness\.ccb\.com\/clp_service\/txCtrl\?txcode=A3341C147` |
| fmz200-blockads: unresolved {{{argument}}} placeholder | 7 | `贴吧proto = type=http-response, pattern=^http(s:\/\/tiebac\|:\/\/c\.tieba)\.baidu\.`, `bilibili.airborne = type=http-request, pattern=^https:\/\/(grpc\.biliapi\.net\|ap`, `bilibili.request = type=http-request, pattern=^https:\/\/(grpc\.biliapi\.net\|app` |
| kelee-blockadvertisers-module: duplicate pattern | 3 | `^https:\/\/video-dsp\.pddpic\.com\/market-dsp-video\/`, `^https:\/\/images\.pinduoduo\.com\/mrk\/`, `^https:\/\/images\.pinduoduo\.com\/marketing_api\/` |
