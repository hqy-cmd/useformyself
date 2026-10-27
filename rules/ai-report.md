# AI rules report

Generated: 2026-10-27 23:44:54 UTC

## Upstreams

| Upstream | Entries | DOMAIN | SUFFIX | KEYWORD | IP-CIDR | IP-ASN | Source |
|---|---|---|---|---|---|---|---|
| [QuixoticHeart](https://raw.githubusercontent.com/QuixoticHeart/rule-set/refs/heads/ruleset/surge/ai.list) | 244 | 48 | 188 | 8 | 0 | 0 | fresh |
| [VPSDance](https://raw.githubusercontent.com/VPSDance/ai-proxy-rules/main/rules/surge/global.list) | 319 | 56 | 249 | 5 | 6 | 3 | fresh |
| [dler-io](https://raw.githubusercontent.com/dler-io/Rules/main/Surge/Surge%203/Provider/AI%20Suite.list) | 192 | 87 | 82 | 0 | 23 | 0 | fresh |
| [v2fly category-ai-!cn (MetaCubeX)](https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-ai-!cn.list) | 207 | 34 | 173 | 0 | 0 | 0 | fresh |

Raw union before exclusions: 493

## Output

- `AI_Domain.list`: 369 (248 suffix, 121 exact)
- `AI.list`: 38 (DOMAIN-KEYWORD 7, IP-CIDR/IP-CIDR6 29, IP-ASN 2)

## Dropped rule types (unsupported in DOMAIN-SET / not wanted)

- **PROCESS-NAME** (23): `PROCESS-NAME,Antigravity`, `PROCESS-NAME,Antigravity.exe`, `PROCESS-NAME,Augment`, `PROCESS-NAME,Augment.exe`, `PROCESS-NAME,ChatGPT`, `PROCESS-NAME,ChatGPT.exe`, `PROCESS-NAME,Claude`, `PROCESS-NAME,Claude.exe`, `PROCESS-NAME,Codex`, `PROCESS-NAME,Codex.exe`, `PROCESS-NAME,Cursor`, `PROCESS-NAME,Cursor.exe`, `PROCESS-NAME,Windsurf`, `PROCESS-NAME,Windsurf.exe`, `PROCESS-NAME,antigravity`, `PROCESS-NAME,augment`, `PROCESS-NAME,chatgpt`, `PROCESS-NAME,claude`, `PROCESS-NAME,claude.exe`, `PROCESS-NAME,codex`, `PROCESS-NAME,cowork-svc.exe`, `PROCESS-NAME,cursor`, `PROCESS-NAME,windsurf`

## Exclusions by category

| Category | Removed |
|---|---|
| ASN: generic VPS hosting | 1 |
| Keywords: shared telemetry / too broad | 3 |
| Broad infrastructure | 17 |
| Shared third-party services (broad suffixes) | 5 |
| Apple group conflicts | 3 |
| ByteDance / TikTok infrastructure | 7 |
| Chinese companies' overseas AI sites | 21 |
| Noise / not AI | 8 |

### ASN: generic VPS hosting

Removed: `IP-ASN,14061`

Exclude rules with no current match (kept for future upstream changes): `IP-ASN,20473`

### Keywords: shared telemetry / too broad

Removed: `DOMAIN-KEYWORD,sentry`, `DOMAIN-KEYWORD,datadog`, `DOMAIN-KEYWORD,sift`

Exclude rules with no current match (kept for future upstream changes): `DOMAIN-KEYWORD,colab`, `DOMAIN-KEYWORD,developerprofiles`, `DOMAIN-KEYWORD,generativelanguage`

### Broad infrastructure

Removed: `DOMAIN,storage.googleapis.com`, `DOMAIN,api.cloudflare.com`, `DOMAIN,cp4.cloudflare.com`, `DOMAIN-SUFFIX,awsstatic.com`, `DOMAIN-SUFFIX,awsapps.com`, `DOMAIN-SUFFIX,aws.dev`, `DOMAIN-SUFFIX,sso.amazonaws.com`, `DOMAIN,cognito-identity.us-east-1.amazonaws.com`, `DOMAIN-SUFFIX,console.aws.a2z.com`, `DOMAIN-SUFFIX,auth0.com`, `DOMAIN-SUFFIX,intercom.io`, `DOMAIN-SUFFIX,intercomcdn.com`, `DOMAIN-SUFFIX,identrust.com`, `DOMAIN,login.live.com`, `DOMAIN,login.microsoftonline.com`, `DOMAIN,api.github.com`, `DOMAIN,www.bing.com`

### Shared third-party services (broad suffixes)

Removed: `DOMAIN-SUFFIX,sentry.io`, `DOMAIN-SUFFIX,stripe.com`, `DOMAIN-SUFFIX,segment.io`, `DOMAIN-SUFFIX,launchdarkly.com`, `DOMAIN-SUFFIX,algolia.net`

### Apple group conflicts

Removed: `DOMAIN-SUFFIX,apps.mzstatic.com`, `DOMAIN-SUFFIX,gateway.icloud.com`, `DOMAIN,gspe1-ssl.ls.apple.com`

### ByteDance / TikTok infrastructure

Removed: `DOMAIN-SUFFIX,byteoversea.com`, `DOMAIN-SUFFIX,abtestvm-sg.bytedance.com`, `DOMAIN-SUFFIX,bytegate-sg.byteintlapi.com`, `DOMAIN-SUFFIX,sf16-short-sg.bytedapm.com`, `DOMAIN-SUFFIX,lf3-static.bytednsdoc.com`, `DOMAIN-SUFFIX,starling.zijieapi.com`, `DOMAIN-SUFFIX,tron-sg.bytelemon.com`

### Chinese companies' overseas AI sites

Removed: `DOMAIN-SUFFIX,kimi.ai`, `DOMAIN-SUFFIX,moonshot.ai`, `DOMAIN-SUFFIX,minimax.io`, `DOMAIN-SUFFIX,qoder.com`, `DOMAIN-SUFFIX,coze.com`, `DOMAIN-SUFFIX,cici.com`, `DOMAIN-SUFFIX,ciciai.com`, `DOMAIN-SUFFIX,ciciaicdn.com`, `DOMAIN-SUFFIX,dola.com`, `DOMAIN-SUFFIX,marscode.com`, `DOMAIN-SUFFIX,trae.ai`, `DOMAIN-SUFFIX,traeapi.us`, `DOMAIN,trae-api-sg.mchost.guru`, `DOMAIN,trae-api-us.mchost.guru`, `DOMAIN-SUFFIX,trae-api-sg.mchost.guru`, `DOMAIN-SUFFIX,lovart.ai`, `DOMAIN-SUFFIX,tripo3d.ai`, `DOMAIN-SUFFIX,youmind.ai`, `DOMAIN-SUFFIX,youmind.com`, `DOMAIN-SUFFIX,youmind.site`, `DOMAIN-SUFFIX,tapnow.ai`

Exclude rules with no current match (kept for future upstream changes): `DOMAIN-SUFFIX,kimi.com`, `DOMAIN-SUFFIX,hailuoai.video`, `DOMAIN-SUFFIX,hailuo.ai`, `DOMAIN-SUFFIX,qwen.ai`, `DOMAIN-SUFFIX,qwenlm.ai`, `DOMAIN-SUFFIX,klingai.com`, `DOMAIN-SUFFIX,z.ai`, `DOMAIN-SUFFIX,deepseek.com`

### Noise / not AI

Removed: `DOMAIN-SUFFIX,envato.com`, `DOMAIN-SUFFIX,envato-static.com`, `DOMAIN-SUFFIX,envatousercontent.com`, `DOMAIN-SUFFIX,themeforest.net`, `DOMAIN-SUFFIX,oystermercury.top`, `DOMAIN-SUFFIX,liveperson.net`, `DOMAIN-SUFFIX,lpsnmedia.net`, `DOMAIN,7h15.ru1353t.1s.m4d3.by.5ukk4w.skk.moe`

## Manual includes

(none)

## Normalisation

- DOMAIN covered by DOMAIN-SUFFIX: 14
- DOMAIN-KEYWORD covered by shorter keyword: 2
- DOMAIN-SUFFIX covered by broader DOMAIN-SUFFIX: 5
