#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ini2toml.py - 将本仓库的 ACL-Next.ini / ACL-Next.Lite.ini 复刻为
SubConverter-Extended 原生支持的 TOML 外部配置格式。

TOML 相比 INI 的优势：
  * 值是结构化类型（数组 / 布尔 / 数字），不必用反引号与逗号拼字符串；
  * 每个策略组、规则集都是独立表格，顺序由声明位置决定，可读且可 diff；
  * 支持 import 引入片段文件，可把 emoji 这类超长正则拆出去。

用法：
    python tools/ini2toml.py ACL-Next.ini      > ACL-Next.toml
    python tools/ini2toml.py ACL-Next.Lite.ini > ACL-Next.Lite.toml
"""
from __future__ import annotations

import io
import re
import sys
from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------- 基础工具


def toml_str(value: str) -> str:
    """按 TOML 规范输出字符串，必要时改用多行字符串。"""
    if value == "":
        return '""'
    if any(c in value for c in "\n\r\t\x00") or value.count("\\") > 4:
        body = value.replace("\\", "\\\\")
        if body.endswith('"'):
            body = body[:-1] + '\\"'
        return '"""\n' + body + '"""'
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def toml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return toml_str(str(value))


def dump_table(rows: List[Tuple[str, Any]], indent: str = "") -> List[str]:
    """输出键值表；空数组写成 key = []。"""
    lines: List[str] = []
    for key, val in rows:
        if isinstance(val, list):
            if not val:
                lines.append(f"{indent}{key} = []")
                continue
            if all(not isinstance(v, (list, dict)) for v in val) and all(
                not (isinstance(v, str) and len(v) > 60) for v in val
            ):
                lines.append(f"{indent}{key} = [{', '.join(toml_scalar(v) for v in val)}]")
            else:
                lines.append(f"{indent}{key} = [")
                for v in val:
                    lines.append(f"{indent}  {toml_scalar(v)},")
                lines.append(f"{indent}]")
        else:
            lines.append(f"{indent}{key} = {toml_scalar(val)}")
    return lines


def array_of_tables(name: str, items: List[List[Tuple[str, Any]]]) -> List[str]:
    """输出 [[name]] 表格数组。"""
    lines: List[str] = []
    for item in items:
        lines.append("")
        lines.append(f"[[{name}]]")
        lines.extend(dump_table(item))
    return lines


# ---------------------------------------------------------------- INI 解析


def parse_ini(path: str) -> List[str]:
    """把 INI 读成 `key=value` 字符串列表，保留声明顺序（含重复键）。"""
    entries: List[str] = []
    with io.open(path, "r", encoding="utf-8-sig") as fh:
        for raw in fh:
            stripped = raw.rstrip("\r\n").strip()
            if not stripped or stripped.startswith(";") or stripped.startswith("#"):
                continue
            if stripped.startswith("[") and stripped.endswith("]"):
                # 段名在本仓库的 INI 中不参与键值解析，全部键都视为同一层
                continue
            if "=" not in stripped:
                continue
            key, _, value = stripped.partition("=")
            entries.append(f"{key.strip()}={value.strip()}")
    return entries


def get_single(entries: List[str], key: str) -> "str | None":
    for e in entries:
        k, _, v = e.partition("=")
        if k.strip() == key:
            return v
    return None


def get_all(entries: List[str], key: str) -> List[str]:
    return [v for e in entries for k, _, v in [e.partition("=")] if k.strip() == key]


def truthy(value: "str | None") -> bool:
    return value is not None and value.strip().lower() in ("1", "true", "yes", "on")


# ---------------------------------------------------------------- 转换逻辑


def parse_group(line: str) -> Dict[str, Any]:
    """解析 custom_proxy_group=名称`类型`规则...`URL`interval,timeout,tolerance"""
    body = line
    interval = timeout = tolerance = None
    url = None
    m = re.search(r"`([\d.,\s]*)$", body)
    if m:
        nums = [p for p in m.group(1).split(",") if p != ""]
        body = body[: m.start()]
        if len(nums) >= 3:
            interval, timeout, tolerance = (
                int(float(nums[0])),
                int(float(nums[1])),
                int(float(nums[2])),
            )
        elif len(nums) == 2:
            interval, timeout = (int(float(nums[0])), int(float(nums[1])))
        elif len(nums) == 1:
            interval = int(float(nums[0]))
    parts = body.split("`")
    name = parts[0]
    gtype = parts[1] if len(parts) > 1 else "select"
    rest = parts[2:]
    if rest and re.match(r"^(https?://|www\.)", rest[-1]):
        url = rest[-1]
        rest = rest[:-1]
    rules = [p for p in rest if p != ""]
    group: Dict[str, Any] = {"name": name, "type": gtype}
    if rules:
        group["rule"] = rules
    if url:
        group["url"] = url
    if interval is not None:
        group["interval"] = interval
    if timeout is not None:
        group["timeout"] = timeout
    if tolerance is not None:
        group["tolerance"] = tolerance
    return group


def parse_ruleset(line: str) -> Dict[str, Any]:
    """解析 ruleset=组名,地址[,间隔|选项]"""
    group, _, rest = line.partition(",")
    rest = rest.strip()
    interval = None
    options: List[str] = []
    m = re.search(r",(\d+)(\|([^,]+))?$", rest)
    if m:
        interval = int(m.group(1))
        if m.group(3):
            options = [m.group(3)]
        rest = rest[: m.start()]
    if rest.startswith("[]"):
        payload = rest[2:]
        items = [i for i in payload.split(",") if i != ""]
        ruleset = "[]" + ",".join(items)
    else:
        ruleset = rest
    out: Dict[str, Any] = {"group": group.strip(), "ruleset": ruleset}
    if interval is not None:
        out["interval"] = interval
    if options:
        out["options"] = options
    return out


def convert(ini_path: str) -> str:
    root = parse_ini(ini_path)

    def pick(key: str, default: "str | None" = None) -> "str | None":
        v = get_single(root, key)
        return v if v is not None else default

    out: List[str] = []
    out.append("# Generated by tools/ini2toml.py from " + ini_path + " - do not edit by hand.")
    out.append("#")
    out.append("# TOML replica of the ACL-Next external config, for backends that read TOML")
    out.append("# (e.g. Aethersailor/SubConverter-Extended).")
    out.append("# Usage: /sub?target=clash&url=<subscription>&config=<URL of this file>")
    out.append("")
    out.append("version = 1")

    # ---- [custom]
    out.append("")
    out.append("[custom]")
    rows: List[Tuple[str, Any]] = []
    rows.append(("enable_rule_generator", truthy(pick("enable_rule_generator", "true"))))
    rows.append(("overwrite_original_rules", truthy(pick("overwrite_original_rules", "false"))))
    if pick("add_emoji"):
        rows.append(("add_emoji", truthy(pick("add_emoji"))))
    if pick("remove_old_emoji"):
        rows.append(("remove_old_emoji", truthy(pick("remove_old_emoji"))))
    for key in ("include_remarks", "exclude_remarks"):
        vals = get_all(root, key)
        if vals:
            rows.append((key, vals))
    for key in ("ruleprepend", "ruleappend"):
        vals = get_all(root, key)
        if vals:
            rows.append((key, vals))
    # *_rule_base 在 TOML 里必须是「单个字符串」（本地路径或 URL），不是数组。
    # 早期版本按 include_remarks 的写法输出成数组，导致 SubConverter-Extended
    # 的 TOML loader 直接拒绝整个外部配置（HTTP 400
    # "selected external configuration could not be loaded or applied"）。
    # INI 中同名键重复出现时后者覆盖前者，这里同样取最后一次声明。
    for key in (
        "clash_rule_base",
        "surge_rule_base",
        "surfboard_rule_base",
        "mellow_rule_base",
        "quan_rule_base",
        "quanx_rule_base",
        "loon_rule_base",
        "sssub_rule_base",
        "singbox_rule_base",
        "stash_rule_base",
    ):
        vals = get_all(root, key)
        if vals:
            rows.append((key, vals[-1]))
    out.extend(dump_table(rows))

    # ---- emoji
    emoji_items: List[List[Tuple[str, Any]]] = []
    for e in get_all(root, "emoji"):
        if "," not in e:
            continue
        match, _, emoji = e.rpartition(",")
        emoji_items.append([("match", match.strip()), ("emoji", emoji.strip())])
    if emoji_items:
        out.extend(array_of_tables("emoji", emoji_items))

    # ---- rename_node
    rename_items: List[List[Tuple[str, Any]]] = []
    for e in get_all(root, "rename_node"):
        if "," not in e:
            continue
        match, _, rep = e.rpartition(",")
        rename_items.append([("match", match.strip()), ("replace", rep.strip())])
    if rename_items:
        out.extend(array_of_tables("rename_node", rename_items))

    # ---- custom_groups
    groups: List[List[Tuple[str, Any]]] = []
    for g in get_all(root, "custom_proxy_group"):
        parsed = parse_group(g)
        rows = [("name", parsed["name"]), ("type", parsed["type"])]
        if "rule" in parsed:
            rows.append(("rule", parsed["rule"]))
        if "url" in parsed:
            rows.append(("url", parsed["url"]))
        for k in ("interval", "timeout", "tolerance", "disable_udp"):
            if k in parsed:
                rows.append((k, parsed[k]))
        groups.append(rows)
    if groups:
        out.extend(array_of_tables("custom_groups", groups))

    # ---- rulesets
    rulesets: List[List[Tuple[str, Any]]] = []
    for r in get_all(root, "ruleset"):
        parsed = parse_ruleset(r)
        rows = [("group", parsed["group"])]
        if parsed.get("type"):
            rows.append(("type", parsed["type"]))
        rows.append(("ruleset", parsed["ruleset"]))
        if "interval" in parsed:
            rows.append(("interval", parsed["interval"]))
        if parsed.get("options"):
            rows.append(("options", parsed["options"]))
        rulesets.append(rows)
    if rulesets:
        out.append("")
        out.append("[ruleset]")
        out.append("enabled = true")
        out.append(
            "overwrite_original_rules = "
            + str(truthy(pick("overwrite_original_rules", "false"))).lower()
        )
        out.extend(array_of_tables("rulesets", rulesets))

    out.append("")
    return "\n".join(out) + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write(__doc__)
        return 2
    text = convert(sys.argv[1])
    # 中文注释与 emoji 需要显式 UTF-8 输出。
    # 不要用 PowerShell 的 `>` 重定向捕获 stdout：它会写成 UTF-16LE + BOM，
    # 把整份配置变成乱码。请把输出路径作为第二个参数传入。
    if len(sys.argv) >= 3:
        with io.open(sys.argv[2], "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        return 0
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    sys.stdout.write(text)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
