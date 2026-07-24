# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc    : Playwright录制片段转 account_page.py 风格 Page Object 工具

"""
将 Playwright codegen 录制片段转换为当前框架 Page Object 代码。

使用示例：
    python utils/tools/po_style_converter.py --input device.txt --class-name DevicePage
    python utils/tools/po_style_converter.py --input device.txt --class-name DevicePage --output device_page.py
"""

import re
import hashlib
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class RecordedAction:
    action_type: str
    locator_key: str = ""
    locator_expr: str = ""
    label: str = ""
    value: str = ""
    data_key: str = ""
    method_name: str = ""
    step_text: str = ""
    raw_code: str = ""


class PoStyleConverter:
    """Playwright录制片段转 Page Object 代码。"""

    def __init__(self, class_name: str, file_name: Optional[str] = None):
        self.class_name = class_name if class_name.endswith("Page") else f"{class_name}Page"
        self.file_name = file_name or self._camel_to_snake(self.class_name) + ".py"
        self.locators: Dict[str, str] = {}
        self.locator_counts: Dict[str, int] = {}
        self.unsupported_lines: List[str] = []
        # 录制里的 page.goto(...) 起始 URL（导航由用例 setup 负责，转换时仅记录供参考）
        self.recorded_urls: List[str] = []

    def convert(self, script: str) -> str:
        actions = self._parse_script(script)
        return self._render(actions)

    def _parse_script(self, script: str) -> List[RecordedAction]:
        actions: List[RecordedAction] = []
        pending_download = False
        pending_popup = False

        for raw_line in script.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            if "expect_download()" in line:
                pending_download = True
                continue
            if "expect_popup()" in line:
                pending_popup = True
                continue
            if re.match(r"\w+\s*=\s*\w+_info\.value", line) or line.endswith(".close()"):
                continue
            if not line.startswith("page."):
                continue

            # page.goto(...) 仅记录起始 URL，不生成动作（导航由用例 setup 的 page.goto 负责）
            goto_match = re.match(r"page\.goto\(\"([^\"]+)\"\)", line)
            if goto_match:
                self.recorded_urls.append(goto_match.group(1))
                continue

            action = self._parse_action_line(line)
            if not action:
                self.unsupported_lines.append(line)
                continue

            if pending_download:
                action.action_type = "download_popup" if pending_popup else "download"
                action.method_name = self._method_name("download", action.label)
                action.step_text = f"下载：{action.label}"
                pending_download = False
                pending_popup = False

            actions.append(action)

        return self._dedupe_method_names(self._merge_redundant(self._merge_click_fill(actions)))

    def _parse_action_line(self, line: str) -> Optional[RecordedAction]:
        target, action_type, value = self._split_target_action(line)
        if not target or not action_type:
            return None

        locator_expr, label, key_hint = self._parse_locator_chain(target)
        if not locator_expr:
            return None

        locator_key = self._register_locator(key_hint, locator_expr)
        method_name = self._method_name(action_type, label)
        step_text = self._step_text(action_type, label, value)

        data_key = self._data_key(label)
        if action_type == "press":
            data_key = f"{data_key}_key"

        return RecordedAction(
            action_type=action_type,
            locator_key=locator_key,
            locator_expr=locator_expr,
            label=label,
            value=value,
            data_key=data_key,
            method_name=method_name,
            step_text=step_text,
            raw_code=line,
        )

    def _split_target_action(self, line: str):
        patterns = [
            ("fill", r"^(page\..+)\.fill\(\"(.*)\"\)$"),
            ("press", r"^(page\..+)\.press\(\"(.*)\"\)$"),
            ("upload", r"^(page\..+)\.set_input_files\(\"(.*)\"\)$"),
            ("click", r"^(page\..+)\.click\(\)$"),
            ("check", r"^(page\..+)\.check\(\)$"),
        ]
        for action_type, pattern in patterns:
            match = re.match(pattern, line)
            if match:
                value = match.group(2) if len(match.groups()) > 1 else ""
                return match.group(1), action_type, value
        return None, None, ""

    def _parse_locator_chain(self, target: str):
        # page.get_by_role("button", name="Close") 或 page.get_by_role("textbox", name="手机号", exact=True)
        role_match = re.search(r"page\.get_by_role\(\"([^\"]+)\",\s*name=\"([^\"]+)\"(?:,\s*exact=True)?\)", target)
        if role_match:
            role, name = role_match.groups()
            locator_expr = self._role_to_locator(role, name)
            key_hint = f"{role}_{name}"
            label = self._clean_label(name)
            return locator_expr, label, key_hint

        # page.get_by_text("1", exact=True).nth(1)
        text_exact_match = re.search(r"page\.get_by_text\(\"([^\"]+)\",\s*exact=True\)(?:\.nth\((\d+)\))?", target)
        if text_exact_match:
            text, nth = text_exact_match.groups()
            locator_expr = f"text={text}"
            if nth is not None:
                locator_expr = f"xpath=(//*[normalize-space()='{text}'])[{int(nth) + 1}]"
            key_hint = f"text_{text}_{nth or 'exact'}"
            return locator_expr, self._clean_label(text), key_hint

        # page.get_by_text("测试店铺").nth(1)
        text_match = re.search(r"page\.get_by_text\(\"([^\"]+)\"\)(?:\.nth\((\d+)\))?", target)
        if text_match:
            text, nth = text_match.groups()
            locator_expr = f"text={text}"
            if nth is not None:
                locator_expr = f"xpath=(//*[normalize-space()='{text}'])[{int(nth) + 1}]"
            key_hint = f"text_{text}_{nth or ''}"
            return locator_expr, self._clean_label(text), key_hint

        # page.locator("...")
        locator_match = re.search(r"page\.locator\(\"([^\"]+)\"\)", target)
        if locator_match:
            selector = locator_match.group(1)
            return selector, self._clean_label(selector), f"locator_{selector}"

        return "", "", ""

    def _role_to_locator(self, role: str, name: str) -> str:
        clean_name = name.strip()
        if role == "button":
            return f"xpath=//button[span[normalize-space()='{clean_name}'] or normalize-space()='{clean_name}']"
        if role == "link":
            return f"text={clean_name}"
        if role == "textbox":
            field_name = clean_name.replace(":", "").replace("：", "").strip()
            if field_name == "页":
                return "xpath=//input[@aria-label='页']"
            return (
                "xpath=//label[contains(normalize-space(), '"
                f"{field_name}')]//following::input[1]"
            )
        if role == "combobox":
            field_name = clean_name.replace("*", "").replace(":", "").replace("：", "").strip()
            return (
                "xpath=//label[contains(normalize-space(), '"
                f"{field_name}')]//following::*[@role='combobox' or contains(@class, 'ant-select')][1]"
            )
        if role == "checkbox":
            return f"xpath=//label[contains(normalize-space(), '{clean_name}')]//input[@type='checkbox']"
        return f"xpath=//*[@role='{role}' and normalize-space()='{clean_name}']"

    def _register_locator(self, key_hint: str, locator_expr: str) -> str:
        base = "locator_" + self._slugify(key_hint, keep_role_prefix=True)
        base = re.sub(r"_+", "_", base).strip("_")
        if not base or base == "locator":
            base = "locator_element"

        for key, expr in self.locators.items():
            if expr == locator_expr:
                return key

        count = self.locator_counts.get(base, 0)
        self.locator_counts[base] = count + 1
        key = base if count == 0 else f"{base}_{count + 1}"
        self.locators[key] = locator_expr
        return key

    def _merge_click_fill(self, actions: List[RecordedAction]) -> List[RecordedAction]:
        merged: List[RecordedAction] = []
        index = 0
        while index < len(actions):
            current = actions[index]
            next_action = actions[index + 1] if index + 1 < len(actions) else None
            if (
                current.action_type == "click"
                and next_action
                and next_action.action_type == "fill"
                and current.locator_key == next_action.locator_key
            ):
                merged.append(next_action)
                index += 2
                continue
            merged.append(current)
            index += 1
        return merged

    def _merge_redundant(self, actions: List[RecordedAction]) -> List[RecordedAction]:
        """
        合并 codegen 录制里的试错冗余（仅在「同一 locator_key」局部范围内，避免误伤跨字段动作）：
        1. 连续 fill 同字段 -> 取末值（fill 本就覆盖，前次无效）；
        2. fill -> press(Enter 等) -> fill 同字段 -> 视为试错，丢弃中间 press，末值覆盖；
        3. fill -> click(重聚焦) -> fill 同字段 -> 丢弃重聚焦 click，末值覆盖；
        4. press(ArrowLeft/Backspace 等光标退键) 夹在同字段动作间 -> 丢弃；
        5. 连续相同 click 同字段 -> 去重为一次。
        """
        backspace_keys = {"ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown",
                          "Backspace", "Delete", "Home", "End"}
        result: List[RecordedAction] = []
        for action in actions:
            prev = result[-1] if result else None
            prev2 = result[-2] if len(result) >= 2 else None
            same_loc = lambda a, b: a and b and a.locator_key == b.locator_key

            # 规则 4：光标/退键试错
            if (action.action_type == "press" and action.value in backspace_keys
                    and same_loc(prev, action)):
                continue
            # 规则 1：连续 fill
            if (action.action_type == "fill" and prev and prev.action_type == "fill"
                    and same_loc(prev, action)):
                prev.value = action.value
                continue
            # 规则 2：fill -> press -> fill
            if (action.action_type == "fill" and prev and prev.action_type == "press"
                    and same_loc(prev, action) and prev2 and prev2.action_type == "fill"
                    and same_loc(prev2, action)):
                result.pop()
                prev2.value = action.value
                continue
            # 规则 3：fill -> click(重聚焦) -> fill
            if (action.action_type == "fill" and prev and prev.action_type == "click"
                    and same_loc(prev, action) and prev2 and prev2.action_type == "fill"
                    and same_loc(prev2, action)):
                result.pop()
                prev2.value = action.value
                continue
            # 规则 5：连续相同 click
            if (action.action_type == "click" and prev and prev.action_type == "click"
                    and same_loc(prev, action) and prev.label == action.label):
                continue
            result.append(action)
        return result

    def _dedupe_method_names(self, actions: List[RecordedAction]) -> List[RecordedAction]:
        seen: Dict[str, tuple] = {}
        counts: Dict[str, int] = {}
        for action in actions:
            signature = (action.action_type, action.locator_key)
            current = seen.get(action.method_name)
            if current is None:
                seen[action.method_name] = signature
                counts[action.method_name] = 1
                continue
            if current == signature:
                continue
            counts[action.method_name] += 1
            action.method_name = f"{action.method_name}_{counts[action.method_name]}"
            seen[action.method_name] = signature
        return actions

    def _render(self, actions: List[RecordedAction]) -> str:
        flow_name = self._flow_name()
        lines = [
            "# -*- coding: utf-8 -*-",
            "# @Version: Python 3.13",
            "# @Author  : 会飞的🐟",
            f"# @File    : {self.file_name}",
            "# @Software: PyCharm",
            f"# @Desc    : {self.class_name} PO（由录制脚本转换生成）",
            "",
            "import allure",
            "from utils.base_utils.base_page import BasePage",
            "",
            "",
            f"class {self.class_name}(BasePage):",
        ]

        if self.recorded_urls:
            lines.append(f"    # 录制起始 URL：{self.recorded_urls[0]}（导航由用例 setup 负责，此处仅备查）")

        if self.unsupported_lines:
            lines.extend(["", "    # TODO: 以下录制行暂未自动转换，请人工补充："])
            for line in self.unsupported_lines:
                lines.append(f"    # - {line}")

        if self.locators:
            for name, selector in self.locators.items():
                note = "  # TODO: 自动 ID，每次会话变化，建议改用 label/role 定位" if "el-id" in selector else ""
                lines.append(f"    {name} = {selector!r}{note}")
        else:
            lines.append("    pass")

        generated_methods = set()
        for action in actions:
            if action.method_name in generated_methods:
                continue
            generated_methods.add(action.method_name)
            lines.extend(["", *self._render_method(action)])

        lines.extend(["", f"    @allure.step(\"{self.class_name}完整流程\")", f"    def {flow_name}(self, case):"])
        lines.append("        \"\"\"")
        lines.append("        由 Playwright 录制片段转换生成的完整流程。")
        lines.append("        \"\"\"")
        lines.append("        (self")
        for action in actions:
            if action.action_type in {"fill", "press", "upload"}:
                lines.append(f"         .{action.method_name}(case.get(\"{action.data_key}\", {action.value!r}))")
            elif action.action_type in {"download", "download_popup"}:
                lines.append(f"         .{action.method_name}()")
            else:
                lines.append(f"         .{action.method_name}()")
        lines.append("         )")
        lines.append("        return self")
        lines.append("")
        return "\n".join(lines)

    def _render_method(self, action: RecordedAction) -> List[str]:
        locator_ref = f"self.{action.locator_key}"
        lines = [f"    @allure.step(\"{action.step_text}\")"]

        if action.action_type == "fill":
            lines.append(f"    def {action.method_name}(self, value):")
            lines.append(f"        self.input({locator_ref}, value)")
        elif action.action_type == "press":
            lines.append(f"    def {action.method_name}(self, key):")
            lines.append(f"        self.press({locator_ref}, key)")
        elif action.action_type == "upload":
            lines.append(f"    def {action.method_name}(self, value):")
            lines.append(f"        self.upload_file({locator_ref}, value)")
        elif action.action_type == "check":
            lines.append(f"    def {action.method_name}(self):")
            lines.append(f"        self.click({locator_ref})")
        elif action.action_type == "download":
            lines.append(f"    def {action.method_name}(self):")
            lines.append("        with self.page.expect_download() as download_info:")
            lines.append(f"            self.click({locator_ref})")
            lines.append("        return download_info.value")
        elif action.action_type == "download_popup":
            lines.append(f"    def {action.method_name}(self):")
            lines.append("        with self.page.expect_download() as download_info:")
            lines.append("            with self.page.expect_popup() as page_info:")
            lines.append(f"                self.click({locator_ref})")
            lines.append("            popup_page = page_info.value")
            lines.append("        download = download_info.value")
            lines.append("        popup_page.close()")
            lines.append("        return download")
        else:
            lines.append(f"    def {action.method_name}(self):")
            lines.append(f"        self.click({locator_ref})")

        if action.action_type not in {"download", "download_popup"}:
            lines.append("        return self")
        return lines

    def _method_name(self, action_type: str, label: str) -> str:
        prefix = {
            "click": "click",
            "fill": "input",
            "check": "select",
            "press": "press",
            "upload": "upload",
            "download": "download",
            "download_popup": "download",
        }.get(action_type, action_type)
        return f"{prefix}_{self._slugify(label)}"

    def _step_text(self, action_type: str, label: str, value: str) -> str:
        if action_type == "fill":
            return f"输入{label}：{{value}}"
        if action_type == "press":
            return f"在{label}按键：{{key}}"
        if action_type == "upload":
            return f"上传文件：{{value}}"
        if action_type == "check":
            return f"选择【{label}】"
        return f"点击【{label}】"

    def _flow_name(self) -> str:
        base = self.class_name[:-4] if self.class_name.endswith("Page") else self.class_name
        return f"{self._camel_to_snake(base)}_flow"

    def _data_key(self, label: str) -> str:
        key = self._slugify(label)
        key = re.sub(r"^(button|link|textbox|combobox|checkbox|text)_", "", key)
        return key or "value"

    def _page_module_name(self) -> str:
        return self.file_name[:-3] if self.file_name.endswith(".py") else self._camel_to_snake(self.class_name)

    def data_file_name(self) -> str:
        base = self.class_name[:-4] if self.class_name.endswith("Page") else self.class_name
        return f"{self._camel_to_snake(base)}.yaml"

    def test_file_name(self) -> str:
        base = self.class_name[:-4] if self.class_name.endswith("Page") else self.class_name
        return f"test_{self._camel_to_snake(base)}.py"

    def case_key(self) -> str:
        base = self.class_name[:-4] if self.class_name.endswith("Page") else self.class_name
        return f"{self._camel_to_snake(base)}_cases"

    def marker_name(self) -> str:
        base = self.class_name[:-4] if self.class_name.endswith("Page") else self.class_name
        return self._camel_to_snake(base).replace("_page", "")

    def generate_data_yaml(self, script: str) -> str:
        actions = self._parse_script(script)
        data = {
            action.data_key: action.value
            for action in actions
            if action.action_type in {"fill", "press", "upload"} and action.value
        }
        lines = [f"{self.case_key()}:", f"  - title: {self.class_name}录制流程", "    run: true"]
        for key, value in data.items():
            lines.append(f"    {key}: {value!r}")
        return "\n".join(lines) + "\n"

    def generate_testcase(self, page_import: Optional[str] = None) -> str:
        page_module = page_import or self._page_module_name()
        flow_name = self._flow_name()
        data_file = self.data_file_name()
        case_key = self.case_key()
        marker = self.marker_name()
        test_class = f"Test{self.class_name[:-4] if self.class_name.endswith('Page') else self.class_name}"
        return "\n".join([
            "# -*- coding: utf-8 -*-",
            "# @Version: Python 3.13",
            "# @Author  : 会飞的🐟",
            f"# @File    : {self.test_file_name()}",
            "# @Software: PyCharm",
            f"# @Desc    : {self.class_name} 测试用例（由录制脚本转换生成）",
            "",
            "import os",
            "",
            "import pytest",
            "from loguru import logger",
            "from playwright.sync_api import Page",
            "",
            "from config.global_vars import GLOBAL_VARS",
            f"from pages.{page_module} import {self.class_name}",
            "from utils.files_utils.yaml_handle import YamlHandle",
            "",
            "",
            f"@pytest.mark.{marker}",
            "@pytest.mark.recordings",
            f"class {test_class}:",
            f"    \"\"\"{self.class_name}录制流程\"\"\"",
            "",
            f"    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), \"data\", \"{data_file}\")",
            "    cases = YamlHandle(data_path).read_yaml",
            "",
            "    @pytest.fixture(autouse=True)",
            "    def setup_teardown_for_each(self, page: Page):",
            "        logger.info(\"\\n\\n---------------Start: 录制流程测试-------------\")",
            "        page.goto(GLOBAL_VARS[\"url\"])",
            f"        self.page_obj = {self.class_name}(page)",
            "        yield",
            "",
            f"    @pytest.mark.parametrize(\"case\", cases[\"{case_key}\"], ids=lambda x: x[\"title\"])",
            "    def test_recorded_flow(self, case):",
            f"        self.page_obj.{flow_name}(case)",
            "",
        ])

    def _clean_label(self, label: str) -> str:
        return label.replace(" :", "").replace(":", "").replace("：", "").replace("*", "").strip()

    def _slugify(self, text: str, keep_role_prefix: bool = False) -> str:
        mapping = {
            "关闭": "close",
            "Close": "close",
            "设备列表": "device_list",
            "设备号": "device_no",
            "IMEI号": "imei",
            "服务时间": "service_time",
            "查 询": "search",
            "查询": "search",
            "重 置": "reset",
            "重置": "reset",
            "导 出": "export",
            "导出": "export",
            "导出脱敏数据": "export_desensitized_data",
            "导出敏感数据": "export_sensitive_data",
            "入库管理": "storage_management",
            "4S店名称": "shop_name",
            "测试店铺": "test_shop",
            "添加入库": "add_storage",
            "页": "page_no",
            "上个月 翻页上键": "previous_month",
            "上个月 (翻页上键)": "previous_month",
            "Enter": "enter",
        }
        cleaned = self._clean_label(text)
        role_prefix = ""
        if keep_role_prefix and "_" in cleaned:
            possible_role, label_part = cleaned.split("_", 1)
            if possible_role in {"button", "link", "textbox", "combobox", "checkbox", "text"}:
                role_prefix = possible_role + "_"
                cleaned = self._clean_label(label_part)

        cleaned = cleaned.replace("(", " ").replace(")", " ").replace("/", " ")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if keep_role_prefix and not cleaned[:1].isdigit():
            cleaned = re.sub(r"_\d+$", "", cleaned)
        if cleaned in mapping:
            return role_prefix + mapping[cleaned]
        if cleaned.isascii():
            cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", cleaned).strip("_").lower()
            return role_prefix + (cleaned or "element")
        digest = hashlib.md5(cleaned.encode("utf-8")).hexdigest()[:8]
        return role_prefix + "element_" + digest

    def _camel_to_snake(self, name: str) -> str:
        name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
        return name.lower()


def convert_script(script: str, class_name: str, file_name: Optional[str] = None) -> str:
    return PoStyleConverter(class_name=class_name, file_name=file_name).convert(script)


def generate_suite(script: str, class_name: str, file_name: Optional[str] = None, page_import: Optional[str] = None):
    converter = PoStyleConverter(class_name=class_name, file_name=file_name)
    return {
        "page": converter.convert(script),
        "data": converter.generate_data_yaml(script),
        "testcase": converter.generate_testcase(page_import=page_import),
    }


def main():
    parser = argparse.ArgumentParser(description="Playwright录制片段转 account_page.py 风格 Page Object")
    parser.add_argument("--input", "-i", required=True, help="录制脚本片段文件")
    parser.add_argument("--output", "-o", help="输出 Page Object 文件；不传则打印到控制台")
    parser.add_argument("--class-name", "-c", required=True, help="页面类名，例如 DevicePage")
    parser.add_argument("--file-name", help="生成文件头里的文件名，例如 device_page.py")
    parser.add_argument("--suite-dir", help="生成 page/data/testcase 三件套的目录，例如 projects/crm")
    parser.add_argument("--page-subdir", default="pages", help="page 文件相对 suite-dir 的目录，默认 pages")
    parser.add_argument("--data-subdir", default="data", help="data 文件相对 suite-dir 的目录，默认 data")
    parser.add_argument("--testcase-subdir", default="testcases/ui", help="testcase 文件相对 suite-dir 的目录，默认 testcases/ui")
    parser.add_argument("--page-import", help="testcase 中导入 page 的模块名，例如 device.device_page")
    args = parser.parse_args()

    script = Path(args.input).read_text(encoding="utf-8")
    converter = PoStyleConverter(args.class_name, args.file_name)

    if args.suite_dir:
        suite_dir = Path(args.suite_dir)
        page_dir = suite_dir / args.page_subdir
        data_dir = suite_dir / args.data_subdir
        testcase_dir = suite_dir / args.testcase_subdir
        page_path = page_dir / converter.file_name
        data_path = data_dir / converter.data_file_name()
        testcase_path = testcase_dir / converter.test_file_name()
        page_import = args.page_import or converter._page_module_name()

        for target_dir in (page_dir, data_dir, testcase_dir):
            target_dir.mkdir(parents=True, exist_ok=True)
        page_path.write_text(converter.convert(script), encoding="utf-8")
        data_path.write_text(converter.generate_data_yaml(script), encoding="utf-8")
        testcase_path.write_text(converter.generate_testcase(page_import=page_import), encoding="utf-8")
        print(f"Page Object: {page_path}")
        print(f"Data YAML: {data_path}")
        print(f"Testcase: {testcase_path}")
        return

    code = converter.convert(script)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(code, encoding="utf-8")
    else:
        print(code)


if __name__ == "__main__":
    main()
