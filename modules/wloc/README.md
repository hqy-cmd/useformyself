# WLoc Surge 模块（实验版）

已完成协议移植、离线测试和 Surge 真实 HTTPS 链路测试；macOS 27.0.1 已触发系统 WLoc 请求并使地图视野转向测试区域；精确位置及持续稳定性仍待验证。默认 enabled=false，lat/lon=UNSET。不安装 WLoc App，不启动独立代理，不改系统 PAC。

## 原理与范围

验证环境：macOS 27.0.1、Surge 6.10.0 (12300)。
源码来源：https://github.com/OpenHRTT/wloc
固定提交：07b3ba0ce63d50c2fc771809e560946e070bda89

当前上游主链路是 HTTPS 请求拦截后直接构造响应，不是简单替换 JSON，也不是修改公网 IP：

1. 目标仅为 gs-loc.apple.com / gs-loc-cn.apple.com 的 POST /clls/wloc。
2. 读取 ARPC：大端 UInt16 版本、三个 UInt16 长度字符串、UInt32 functionID、UInt32 payload 长度。
3. 解析 protobuf：顶层 field 2 为 Wi-Fi 列表；设备 field 1 为 BSSID，field 2 为 location。
4. location 的纬度、经度为乘 1e8 后取整的 int64（不是 sint64/ZigZag）；负数用 64 位补码 varint。
5. 与上游一样设置精度、海拔和 field 4/11/12 常量，去除顶层 3/4/33，保留其余字段，包括蜂窝字段；本模块不声称改写蜂窝定位。
6. 返回 00 01 00 00 00 01 00 00 + UInt16 大端长度 + protobuf，HTTP 200。

Surge 负责 TLS MITM 和请求处理，JavaScript 负责二进制协议。脚本不发起网络请求，不存储或记录坐标、BSSID 或原始报文。遇到不支持的报文/参数会记录简短原因并放行。与上游相比，本版额外拒绝无 Wi-Fi、ARPC 尾随数据和响应超过 65535 字节等情况；未知 protobuf group 类型放行，不强行改写。

## 安装

在 Surge 中通过本仓库的 `modules/wloc/WLoc.sgmodule` 原始文件 URL 安装。模块使用远程脚本，默认关闭改写；填入自己的目标坐标后设 enabled=true。

离线安装可将 wloc.js 和模块复制到 Surge 配置目录，并把 script-path 改成 wloc.js。

模块参数：

| 参数 | 默认值 | 含义 |
| --- | --- | --- |
| enabled | false | 填 true 才执行定位改写 |
| lat | UNSET | WGS-84 纬度，-90 到 90 |
| lon | UNSET | WGS-84 经度，-180 到 180 |
| altitude | 0 | 海拔米；取整，范围 -12000 到 100000 |
| hacc | 10 | 水平精度米，0 到 1000000 的整数 |
| vacc | 10 | 垂直精度米，0 到 1000000 的整数 |

第一版只接收 WGS-84；高德/腾讯 GCJ-02、百度 BD-09 坐标需先转换。本模块不包含地图选点。

## 真实验证步骤

1. 确保 Surge MITM 和脚本功能开启，Surge CA 在系统钥匙串中得到系统信任。仅用户钥匙串信任不一定足以让 locationd 接受。模块不能配置/替换 CA，也不会关闭证书校验。
2. 检查有效 MITM 主机列表中是否有优先的 Apple 域名排除项。模块只追加两个精确域名，不覆盖现有 MITM 列表；既有排除规则可能导致不拦截。
3. 填入目标 WGS-84 坐标，再设 enabled=true。确保目标请求实际通过 Surge HTTP 引擎；本机系统代理和增强模式虽已开启，但仍需请求记录确认。
4. 用地图等应用发起新定位。部分系统关闭全局定位开关会提示从“查找我的 Mac”移除此设备；不要把关闭总开关当成无副作用的缓存刷新。成功证据应同时包含：目标 POST 请求命中 wloc-local 脚本、得到本地响应，以及系统/地图实际位置变为目标。
5. 不生效时区分：没有请求（路由/缓存）、TLS 失败（信任/系统限制）、脚本放行（协议/参数）、脚本成功但系统未采用（系统策略/其他定位源）。离线测试不能证明这些步骤成功。

不会更改 IP 定位、GPS 硬件或保证所有应用采用该结果。Apple 协议和系统行为可能变化。

## 停用与恢复

把 enabled 改成 false 可停止改写，但模块仍追加 MITM 域名；完全停用请在 Surge 中禁用 WLoc Local 模块。随后重新请求定位并等待缓存更新；若系统关闭定位开关会影响“查找我的 Mac”，应先评估该影响。无需移除其他应用使用的 Surge CA；本模块没有新建证书、后台服务或 PAC。

## 验证记录

2026-10-15：
- Node 语法检查通过。
- 20 项独立 Python 编码的合成协议用例在 Node 和本机 Surge JavaScript 引擎内全部通过。
- 覆盖负经纬度/海拔 int64、未知 64 位字段、多 Wi-Fi、字段删除、无效参数、错误 URL/方法、截断/溢出及禁用。
- 默认参数展开后，作为最小完整配置执行 surge-cli --check 返回 OK。直接对 sgmodule 用 --check 会报缺少 FINAL；这不是完整模块加载验证。
- 未安装/启用模块，未变更定位、证书或现有 Surge 配置；没有真实 locationd 请求验证。

复现：`python3 tests/test.py`（需要 Node、Python 3 和本机 Surge CLI）。测试使用合成 BSSID，通过 CLI 的 generic 脚本求值运行；不触发定位或修改流量。

限制：请求体超过模块 max-size=1 MiB 时，Surge 会拒绝连接，脚本无法放行；TLS 握手失败同样发生在脚本之前。日志中的 passthrough 仅指脚本已运行后的异常处理。

## 授权与来源

上游自有代码 MIT 授权允许修改和再分发；已保留 LICENSE 及版权署名。本版本参考协议及变换逻辑重新实现为无依赖 JavaScript，没有打包 SwiftProtobuf、SnapKit 等第三方组件。上游源码请从上述仓库的固定提交获取。

关键来源：
- https://github.com/OpenHRTT/wloc/blob/07b3ba0ce63d50c2fc771809e560946e070bda89/WLocApp/WLocCore/AppWLocMutator.swift
- https://github.com/OpenHRTT/wloc/blob/07b3ba0ce63d50c2fc771809e560946e070bda89/WLocApp/WLocCore/AppWLocARPC.swift
- https://github.com/OpenHRTT/wloc/blob/07b3ba0ce63d50c2fc771809e560946e070bda89/WLocApp/WLocCore/BSSIDApp.pb.swift
- https://manual.nssurge.com/scripting/http-request.html
- https://manual.nssurge.com/profile/module.html

## 真实链路测试（2026-10-15）

- 已在 Surge 中实际加载本地模块；两个域名的 HTTPS POST 合成请求均返回 HTTP 200 本地响应。
- TLS 使用系统现有信任，无 `-k` 或跳过证书验证。独立解码返回 protobuf，坐标与本地指定测试值完全一致。
- 合成测试数据仅含虚构 BSSID，不能替代系统定位验证。
- 打开地图并刷新 locationd 后，地图仍显示原位置；系统日志显示 Wi-Fi tile/cache 查询。本轮观察到 locationd 访问 cl2.apple.com，未观察到目标 /clls/wloc 请求。
- 因而目前只能确认模块的实际 HTTPS 处理链路有效，不能宣称系统定位修改成功，也不能由此判定系统完全不兼容。
- 测试结束已禁用本地测试模块，保留原证书、定位开关和其他 Surge 模块。取消了会影响“查找我的 Mac”的关闭定位操作。
- 下一步应确认如何在保留现有系统设置的前提下触发新的 WLoc 请求，并区分缓存、系统新协议和其他定位来源；未删除定位数据库或改动系统保护。

## 系统定位开关复测（2026-10-15）

经明确授权临时关闭再开启系统定位后，Surge 捕获了 locationd 发出的真实 POST /clls/wloc 请求，目标为 gs-loc-cn.apple.com。地图视野从原区域转到测试区域，天气也随之更新；此次没有通过搜索或手动平移地图设置测试区域。

这是比合成请求更进一步的系统链路证据，但尚未从地图当前位置详情读取到精确经纬度，也没有验证长时间稳定性，因此不等同于完整验收。

复测后系统定位已恢复开启，系统服务列表中的 Find My Mac 定位权限为开启；没有验证 iCloud 设备列表的注册状态。全局定位开关有系统提示的副作用，不能作为无人值守自动刷新操作。

本地测试模块在本轮复测后保持开启；公开模块默认仍关闭，公开文件不保存本机目标坐标。

## iOS 实验版

[测试指南](iOS-TEST.md) · [公共模板](WLoc-iOS.sgmodule)。尚未完成 iPhone 实测；与 Mac 版共用协议脚本。
