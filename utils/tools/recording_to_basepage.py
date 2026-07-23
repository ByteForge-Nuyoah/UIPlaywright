# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc    : Playwright 录制的 pytest 脚本 -> BasePage 封装方法的函数式脚本

"""
将 Playwright codegen 录制的 pytest 脚本转换为使用 BasePage 封装方法的函数式脚本。

与 po_style_converter.py 互补：
- po_style_converter：输出 Page Object 三件套（page + data + testcase）
- 本工具：输出函数式脚本，逐行把 page.xxx 替换为 base_page.page.goto/click/input/press/check

支持的动作：
    page.goto(url)                       -> base_page.page.goto(url)
    page.get_by_role(...).click()        -> base_page.click(locator)
    page.get_by_role(...).fill(value)    -> base_page.input(locator, value)
    page.get_by_role(...).press(key)     -> base_page.press(locator, key)
    page.get_by_role(...).check()        -> base_page.check(locator)
    page.get_by_text(...).click()        -> base_page.click(locator)
    page.locator(...).click()/fill()/... -> base_page.click/input(locator, ...)
    page.locator(sel).nth(N).click()     -> base_page.click('xpath=(//sel)[N+1]')   (sel 为纯标签名)
    page.locator(sel).filter(has_text=T) -> base_page.click('xpath=//sel[normalize-space()=T]')

用法：
    python utils/tools/recording_to_basepage.py --input recorded.py
    python utils/tools/recording_to_basepage.py --input recorded.py --output converted.py --merge

说明：
- 默认逐行 1:1 原样替换；--merge 合并相邻同元素的 click+input 为一条 input。
- download/弹窗(with expect_download/expect_popup)、set_input_files、链式 get_by_role().get_by_role()
  等控制流无法逐行映射，保留为 # TODO 注释，需手工处理（建议改用 Page Object 的 download 方法）。
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from utils.tools.po_style_converter import PoStyleConverter


# action_type -> BasePage 方法名
ACTION_TO_METHOD = {
    "click": "click",
    "fill": "input",
    "press": "press",
    "check": "check",
}

GOTO_RE = re.compile(r'page\.goto\("([^"]+)"\)')
DEF_PAGE_PARAM_RE = re.compile(r'def\s+(\w+)\s*\(\s*page\b[^)]*\)')
NTH_RE = re.compile(r'^page\.locator\("([^"]+)"\)\.nth\((\d+)\)$')
FILTER_TEXT_RE = re.compile(
    r'^page\.locator\("([^"]+)"\)\.filter\(has_text=(?:re\.compile\(r?"([^"]+)"\)|"([^"]+)")\)$'
)
TAG_RE = re.compile(r'^[a-zA-Z][a-zA-Z0-9]*$')
# 下载/弹窗控制流关键字
CONTROL_FLOW_RE = re.compile(r'expect_download|expect_popup|_info\.value|\.close\(\)')


def _new_converter() -> PoStyleConverter:
    """复用 po_style_converter 的定位器解析逻辑（get_by_role/get_by_text/locator -> xpath/css）。"""
    return PoStyleConverter(class_name="TmpPage", file_name="tmp_page.py")


def _indent_of(line: str) -> str:
    return line[:len(line) - len(line.lstrip())]


def _locator_from_target(target: str, conv: PoStyleConverter) -> str:
    """把录制 target 转为 locator 字符串；增强 nth/filter，其余复用 po_style_converter。"""
    # page.locator("sel").nth(N) -> xpath=(//sel)[N+1]
    m = NTH_RE.match(target)
    if m:
        sel, n = m.group(1), int(m.group(2))
        if TAG_RE.match(sel):
            return f'xpath=(//{sel})[{n + 1}]'
        return ""
    # page.locator("sel").filter(has_text=T) -> xpath=//sel[normalize-space()='T']
    m = FILTER_TEXT_RE.match(target)
    if m:
        sel = m.group(1)
        text = (m.group(2) or m.group(3) or "").strip("^$")
        if TAG_RE.match(sel) and text:
            return f"xpath=//{sel}[normalize-space()='{text}']"
        return ""
    # 通用：get_by_role/get_by_text/page.locator("...")
    locator_expr, _label, _ = conv._parse_locator_chain(target)
    return locator_expr


def _convert_recorded_line(line: str, conv: PoStyleConverter) -> Optional[str]:
    """转换单行；非录制行返回 None，无法转换的录制行返回 # TODO 注释。"""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    indent = _indent_of(line)

    # page.goto(url) -> base_page.page.goto(url)
    m = GOTO_RE.search(stripped)
    if m:
        return f'{indent}base_page.page.goto({m.group(1)!r})'

    # 下载/弹窗控制流行：标 TODO（BasePage 未封装 expect_download/expect_popup）
    if CONTROL_FLOW_RE.search(stripped):
        return f'{indent}# TODO 下载/弹窗控制流需手工处理: {stripped}'

    # 仅处理以 page. 开头的录制动作行
    if not stripped.startswith("page."):
        return None

    target, action_type, value = conv._split_target_action(stripped)
    if not target or not action_type:
        return f'{indent}# TODO 未自动转换: {stripped}'

    locator_expr = _locator_from_target(target, conv)
    if not locator_expr:
        return f'{indent}# TODO 未自动转换(定位器无法识别): {stripped}'

    method = ACTION_TO_METHOD.get(action_type)
    if not method:
        return f'{indent}# TODO 未自动转换(动作 {action_type}): {stripped}'

    if action_type == "fill":
        return f'{indent}base_page.input({locator_expr!r}, {value!r})'
    if action_type == "press":
        return f'{indent}base_page.press({locator_expr!r}, {value!r})'
    return f'{indent}base_page.{method}({locator_expr!r})'


def _merge_click_fill_pairs(lines: List[Optional[str]]) -> List[Optional[str]]:
    """--merge：相邻同 locator 的 base_page.click(L) + base_page.input(L, v) 合并为 input(L, v)。"""
    click_re = re.compile(r'^(\s*)base_page\.click\((.*)\)\s*$')
    input_re = re.compile(r'^(\s*)base_page\.input\((.*), (.*)\)\s*$')
    merged: List[Optional[str]] = []
    i = 0
    while i < len(lines):
        cur, nxt = lines[i], (lines[i + 1] if i + 1 < len(lines) else None)
        cm = click_re.match(cur) if cur else None
        im = input_re.match(nxt) if nxt else None
        if cm and im and cm.group(1) == im.group(1) and cm.group(2) == im.group(2):
            merged.append(nxt)  # 保留 input，丢弃 click
            i += 2
            continue
        if cur is not None:
            merged.append(cur)
        i += 1
    return merged


def convert_script(src: str, merge: bool = False) -> str:
    """转换整段脚本：保留 def/import/注释，录制行替换为 base_page 方法。"""
    conv = _new_converter()
    out_lines: List[str] = [
        "# -*- coding: utf-8 -*-",
        "# 由 recording_to_basepage.py 自动转换生成",
        "# base_page 为 BasePage 实例，需由调用方注入（fixture 或手工构造）",
        "",
    ]

    converted: List[Optional[str]] = []
    for line in src.splitlines():
        # def test_x(page...) -> def test_x(base_page)
        new_def = DEF_PAGE_PARAM_RE.sub(r'def \1(base_page)', line)
        if new_def != line:
            converted.append(new_def)
            continue
        replaced = _convert_recorded_line(line, conv)
        converted.append(replaced if replaced is not None else line)

    if merge:
        converted = _merge_click_fill_pairs(converted)

    out_lines.extend(l if l is not None else "" for l in converted)
    return "\n".join(out_lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Playwright 录制 pytest 脚本 -> BasePage 封装方法的函数式脚本"
    )
    parser.add_argument("--input", "-i", required=True, help="录制的 pytest 脚本文件")
    parser.add_argument("--output", "-o", help="输出文件；不传则打印到控制台")
    parser.add_argument("--merge", action="store_true", help="合并相邻同元素 click+fill 为 input")
    args = parser.parse_args()

    src = Path(args.input).read_text(encoding="utf-8")
    result = convert_script(src, merge=args.merge)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"已生成: {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
