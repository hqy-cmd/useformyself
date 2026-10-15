# iOS 实验模块

测试设备版本（用户提供）：iOS 27.0.1，Surge 5.102 beta。尚未在该 iPhone 上实际验证。

模块只添加两个定位域名的 MITM 与 http-request 二进制脚本。使用与 Mac 版相同的 ARPC/protobuf 逻辑，不包含独立 VPN App、PAC 服务、定位数据库修改或证书。iPhone 使用自己的 Surge VPN，不需要连接 Mac。

## 导入

公共模板：
https://raw.githubusercontent.com/hqy-cmd/useformyself/main/modules/wloc/WLoc-iOS.sgmodule

公共模板默认 enabled=false，坐标 UNSET。下载为本地模块后，编辑唯一脚本行的 argument，填入 enabled=true&lat=纬度&lon=经度&altitude=0&hacc=10&vacc=10，再导入 Surge。仅接受 WGS-84。该版直接使用 script argument 字面量，避免依赖尚未在目标 iOS 版本确认的模块参数表交互。

如收到已经设置测试坐标的本地 WLoc-iOS-Test.sgmodule，可直接导入。不要同时启用 Mac 版和 iOS 版脚本。该预设文件不会提交到公共仓库。

## 测试顺序

1. 确认 Surge VPN 已启动，MITM 与脚本功能开启，Surge 自己的 CA 已安装并完全信任（设置 → 通用 → 关于本机 → 证书信任设置）。不安装 WLoc 的另一张 CA。
2. 启用模块，核对有效 MITM 域名列表包含 gs-loc.apple.com 和 gs-loc-cn.apple.com，且没有被既有排除项优先排除。
3. 在 Surge 请求记录中过滤 gs-loc。先尝试 Wi-Fi 环境，打开 Apple 地图点击当前位置。若仍使用缓存，可临时关闭再开启 iPhone 定位服务；阅读系统提示，定位结束后保持开启。
4. 请求应出现 POST /clls/wloc。脚本成功时日志出现 `[WLoc] synthetic response generated (N bytes)`；异常放行出现 `[WLoc] passthrough: ...`。成功日志不输出坐标、BSSID 或报文。
5. 以地图当前位置标记/详情为依据。地图搜索结果、视野跳转和 IP 地址不能单独证明系统定位成功。重复定位观察稳定性，再单独测试蜂窝环境。

## 结果解释

- 无请求：先排查缓存、请求是否进入 Surge，以及系统是否改用了其他接口。
- TLS 错误：先确认 CA 完全信任；若系统实施额外校验/证书固定，脚本不能绕过，关闭模块。
- 有 POST 但无脚本日志：检查脚本下载、正则匹配、脚本启用状态及其他先匹配的请求脚本。
- passthrough：提供错误文字即可；无需提交原始报文或 BSSID。
- 脚本成功但位置不变：可能由其他定位源、系统缓存或响应接受策略导致，不能宣称已兼容。

上游 README 的 iOS 27 beta6 后限制明确描述网页定位，不能据此判断客户端/Surge 必然可用或不可用。Surge 更换了拦截工具，没有自动绕过苹果系统校验。

## 恢复

禁用本模块，保留 Surge 常规代理。重新请求定位，必要时在理解系统提示后再开关定位服务。不删除其他配置依赖的 Surge CA。

本模块没有在手机上完成测试，不能把 Mac 脚本引擎和 HTTPS 测试当成 iOS 实测。

官方接口说明：https://manual.nssurge.com/scripting/http-request.html
上游：https://github.com/OpenHRTT/wloc
