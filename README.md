# ACL-Next
Acess Control Lists Next For Clash, Based on ACL4SSR Mannix

## 分类

⚡ = `URLTest`  
👆🏻 = `Selector`  
🌐 = 访问到对应网站时，应……

 - ✈️ 代理
 - ⚡ 智能
 - 👆🏻 手动
 - 🛩️ 直连
 - 🚫 阻断
 - 🌐📺 哔哩哔哩
 - 🌐📺 哔哩哔哩 港澳台
 - 🌐🤖 人工智能
 - 🌐🎮 游戏平台
 - 🌐Ⓜ️ Microsoft
 - 🌐Ⓜ️ Microsoft Bing
 - 🌐🍎 Apple
 - 🌐❔ 未知
 - 🇨🇳 中国⚡
 - 🇨🇳 中国👆🏻
 - 🇨🇳 中国大陆⚡
 - 🇨🇳 中国大陆👆🏻
 - 🇭🇰 中国香港⚡
 - 🇭🇰 中国香港👆🏻
 - 🇲🇴 中国澳门⚡
 - 🇲🇴 中国澳门👆🏻
 - 🇹🇼 中国台湾⚡
 - 🇹🇼 中国台湾👆🏻
 - 🇺🇸 美国⚡
 - 🇺🇸 美国👆🏻
 - 🇬🇧 英国⚡
 - 🇬🇧 英国👆🏻
 - 🇫🇷 法国⚡
 - 🇫🇷 法国👆🏻
 - 🇯🇵 日本⚡
 - 🇯🇵 日本👆🏻
 - 🇸🇬 新加坡⚡
 - 🇸🇬 新加坡👆🏻
 - 🇰🇷 韩国⚡
 - 🇰🇷 韩国👆🏻
 - 🎏 其它⚡
 - 🎏 其它👆🏻

## 使用

> [!TIP]
> 本教程适用于：想将原始节点/订阅链接转换为带 ACL 规则的定制订阅（如用于 Clash、Surge、Quantumult X 等客户端）。

### 1. 准备链接！

确保你拥有以下任意一种内容：
- 一个或多个 **订阅链接**（如 `https://xxx.com/subscribe?token=xxx`）
- 或多个 **单节点链接**（如 `ss://...`、`ssr://...`、`vmess://...`）

### 2. 订阅转换！

访问任意一个提供订阅转换服务的网站（例如：[`Dler.io`](https://sub.dler.io/)），网站界面应类似下图：
<img width="1285" height="799" alt="image" src="https://github.com/user-attachments/assets/ebf12022-281a-47e8-8efe-62263be3ae51  " />


根据你正在使用的客户端，在【客户端】框中选一个客户端  
在【订阅链接】输入框中，将你的订阅或节点链接每行一条粘贴进去（支持多行），例如：
```
https://example.com/sub1
vmess://...
ss://...
```

在【远程配置】输入框中，填入 ACL-Next 的配置地址
```
https://github.com/hmjz100/ACL-Next/raw/main/ACL-Next.ini
```

点击【生成订阅链接】按钮，网站会自动生成一个新的订阅链接，并自动复制到剪贴板。

### 3. 最终验证！

新打开一个浏览器标签页，将得到的订阅链接粘贴到地址栏并访问

- 如果成功了，就会出现配置内容
  ```
  port: 7890
  socks-port: 7891
  allow-lan: true
  mode: Rule
  log-level: info
  external-controller: 127.0.0.1:9090
  proxies:
    - {name: "我是节点~~~"
  ...
  ```
- 如果没有出现配置内容，而是小字，那就是出错了
- 回头确认下【订阅链接】有没有填对，或者检查下填写的订阅是否还生效吧

### 4. 导入使用！
打开你的代理工具（如 Clash、Surge、Quantumult X 等客户端）  
在订阅设置中粘贴刚生成的链接  
保存，然后更新订阅  
看看代理组，Enjoy~
