# ACL-Next
Acess Control Lists Next For Clash, Based on ACL4SSR Mannix.

## 在线工具

仓库根目录的 [`index.html`](index.html) 是一个纯静态的订阅链接转换页面（jQuery + Semantic UI，无构建步骤）。
在仓库设置里启用 GitHub Pages（Source = `main` / `root`）后即可访问：

```
https://<你的用户名>.github.io/ACL-Next/
```

页面功能：多链接粘贴智能合并与去重、拖拽排序、后端 / 外部配置 / GitHub 代理前缀可选可手输、生成最终订阅链接。
所有请求都直接发向你选中的转换后端，本页面不代理、不存储任何数据。

## 分类

⚡ = `URLTest`  
🌩️ = `load-balance`
👆🏻 = `Selector`  
🌐 = 访问到对应网站时，应……

## 使用

> [!TIP]
> 本教程适用于：想将原始节点/订阅链接转换为带 ACL 规则的定制订阅（如用于 Clash、Surge、Quantumult X 等客户端）。

### 1. 准备链接！

确保你拥有以下任意一种内容：
- 一个或多个 **订阅链接**（如 `https://xxx.com/subscribe?token=xxx`）
- 或多个 **单节点链接**（如 `ss://...`、`ssr://...`、`vmess://...`）

### 2. 订阅转换！

推荐使用 [**SubConverter-Extended**](https://github.com/Aethersailor/SubConverter-Extended)（本项目 TOML 配置的目标后端），
也可使用任意 SubConverter 系服务（例如 [`Dler.io`](https://sub.dler.io/)），网站界面应类似下图：
<img width="1285" height="799" alt="image" src="https://github.com/user-attachments/assets/ebf12022-281a-47e8-8efe-62263be3ae51  " />


根据你正在使用的客户端，在【客户端】框中选一个客户端  
在【订阅链接】输入框中，将你的订阅或节点链接每行一条粘贴进去（支持多行），例如：
```
https://example.com/sub1
vmess://...
ss://...
```

在【远程配置】输入框中，填入 ACL-Next 的配置地址

#### INI 配置（兼容所有 SubConverter 分支）

```
https://github.com/hmjz100/ACL-Next/raw/main/ACL-Next.ini
```

仅需 Clash 核心功能、配置更精简的分支：

```
https://github.com/hmjz100/ACL-Next/raw/main/ACL-Next.Lite.ini
```

#### TOML 配置（需 [SubConverter-Extended](https://github.com/Aethersailor/SubConverter-Extended)）

TOML 是本项目推荐的配置格式，结构化、带类型、可拆分引用，自由度高于 INI：

```
https://github.com/hmjz100/ACL-Next/raw/main/ACL-Next.toml
```

```
https://github.com/hmjz100/ACL-Next/raw/main/ACL-Next.Lite.toml
```

> [!NOTE]
> 公共后端 `api.asailor.org` 与自建 SubConverter-Extended 均可正常加载本项目的 TOML 配置，
> INI 与 TOML 生成结果完全等价（规则集 URL 会多一个 `surge:` 格式标签，后端会剥离，抓取内容一致），可随时互换。
> 若某个后端拒绝 TOML，请先按下方「维护」一节做差分验证，再怀疑后端。

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

## 健康检查策略

分组为 `url-test` / `load-balance` 时，`interval`、`tolerance`、`timeout` 控制 Mihomo 的探活行为。
节点池很大时，过于激进的探测会被节点方或运营商限流，因此本项目统一采用：

```ini
custom_proxy_group=...`url-test`...,300,5,100
```

| 参数 | 值 | 含义 |
|------|----|------|
| `interval` | `300` | 每 300 秒测试一轮，避免高频探测 |
| `timeout` | `5` | 单个节点 5 秒无响应即判失败 |
| `tolerance` | `100` | 延迟波动在 100ms 内不切换，减少抖动 |

节点故障时最坏约 300 秒被发现并切换；日常不频繁打扰节点与运营商。
若你的节点很少或对切换速度敏感，可把 `interval` 调低（如 `60`）、`tolerance` 调高（如 `150`）。

## 维护：从 INI 生成 TOML

INI 是唯一的手工编辑源，TOML 由脚本生成，请勿直接改 TOML。

```powershell
python tools/ini2toml.py ACL-Next.ini ACL-Next.toml
python tools/ini2toml.py ACL-Next.Lite.ini ACL-Next.Lite.toml
```

改完 INI 后重新生成，然后提交 `ACL-Next.ini`、`ACL-Next.toml`、`ACL-Next.Lite.ini`、`ACL-Next.Lite.toml` 四个文件。

### 验证转换结果

本地语法检查：

```powershell
python -c "import tomllib;tomllib.load(open('ACL-Next.toml','rb'));print('ok')"
```

在线验证（`explain=true` 会返回后端实际加载了哪些分组/规则，便于和 INI 对比）：

```
https://<你的转换后端>/sub?target=clash&url=<订阅链接>&config=https://github.com/hmjz100/ACL-Next/raw/main/ACL-Next.ini&explain=true
```

关注返回 JSON 里的 `external_config.loaded`：为 `true` 才算外部配置真正生效。

### 已知坑：TOML 里 `*_rule_base` 必须是字符串

`clash_rule_base` 等基础模板键在 TOML 中**只能是单个字符串**（本地路径或 URL）。
若写成数组（`clash_rule_base = ["https://..."]`），SubConverter-Extended 的 TOML loader
会直接拒绝整个外部配置，表现为 HTTP 400：

```
Invalid request: selected external configuration could not be loaded or applied.
```

且报错信息不指向具体键名，只能靠二分定位。`tools/ini2toml.py` 已按字符串输出，
修改脚本时请勿改回数组。

### 差分验证（INI vs TOML 是否等价）

后端对两种配置各生成一份 Clash 配置，除 `rule-providers` 的 `getruleset` URL 外应逐字节相同
（TOML 侧会多一个 `surge:` 格式标签，后端抓取时会剥离，内容一致）。示例：

```powershell
$sub  = "<订阅链接>"
$ini  = "https://github.com/hmjz100/ACL-Next/raw/main/ACL-Next.Lite.ini"
$toml = "https://github.com/hmjz100/ACL-Next/raw/main/ACL-Next.Lite.toml"
curl.exe -s "https://api.asailor.org/sub?target=clash&url=$sub&config=$ini"  -o ini.yaml
curl.exe -s "https://api.asailor.org/sub?target=clash&url=$sub&config=$toml" -o toml.yaml
Compare-Object (Get-Content ini.yaml) (Get-Content toml.yaml)
```
