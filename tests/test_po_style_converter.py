
# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_po_style_converter.py
# @Software: PyCharm
# @Desc    : Page Object 风格转换工具测试

import ast
import subprocess
import sys

from utils.tools.po_style_converter import convert_script, generate_suite


DEVICE_SCRIPT = '''
# 设备管理
page.get_by_role("button", name="Close").click()
page.get_by_role("link", name="设备列表").click()
page.get_by_role("textbox", name="IMEI号 :").click()
page.get_by_role("textbox", name="IMEI号 :").fill("869497052182449")
page.get_by_role("button", name="查 询").click()
page.get_by_role("button", name="重 置").click()
page.get_by_role("textbox", name="服务时间 :").click()
page.get_by_role("button", name="上个月 (翻页上键)").click()
page.get_by_text("1", exact=True).nth(1).click()
page.get_by_text("28").nth(3).click()
page.get_by_role("button", name="查 询").click()
with page.expect_download() as download2_info:
    with page.expect_popup() as page3_info:
        page.get_by_role("button", name="导出脱敏数据").click()
    page3 = page3_info.value
page.get_by_role("button", name="入库管理").click()
page.get_by_role("combobox", name="* 4S店名称 :").click()
page.get_by_text("测试店铺").nth(1).click()
page.get_by_role("textbox", name="设备号 :").fill("869497052182449 573970116302449")
with page.expect_download() as download3_info:
    page.get_by_role("button", name="添加入库").click()
page.get_by_role("textbox", name="页").press("Enter")
'''


def test_convert_device_script_to_account_page_style():
    code = convert_script(DEVICE_SCRIPT, "DevicePage", "device_page.py")

    assert "class DevicePage(BasePage):" in code
    assert "locator_button_close" in code
    assert "locator_link_device_list" in code
    assert "locator_textbox_imei" in code
    assert "locator_button_search" in code
    assert "locator_button_export_desensitized_data" in code
    assert "locator_combobox_shop_name" in code
    assert "locator_textbox_device_no" in code
    assert "def input_imei(self, value):" in code
    assert "def download_export_desensitized_data(self):" in code
    assert "def download_add_storage(self):" in code
    assert "def device_flow(self, case):" in code
    assert '.input_imei(case.get("imei", \'869497052182449\'))' in code
    assert '.press_page_no(case.get("page_no_key", \'Enter\'))' in code
    ast.parse(code)


def test_convert_keeps_unsupported_lines_as_todo():
    code = convert_script('page.get_by_label("用户名").click()\n', "DemoPage", "demo_page.py")

    assert "# TODO: 以下录制行暂未自动转换，请人工补充：" in code
    assert '# - page.get_by_label("用户名").click()' in code
    ast.parse(code)


def test_unknown_chinese_locator_name_is_deterministic():
    script = 'page.get_by_role("button", name="未知按钮").click()\n'

    first = convert_script(script, "DemoPage", "demo_page.py")
    second = convert_script(script, "DemoPage", "demo_page.py")

    assert first == second
    assert "locator_button_element_" in first


def test_cli_creates_parent_directory(tmp_path):
    input_path = tmp_path / "input.py"
    output_path = tmp_path / "generated" / "device_page.py"
    input_path.write_text('page.get_by_role("button", name="Close").click()\n', encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "utils/tools/po_style_converter.py",
            "--input",
            str(input_path),
            "--class-name",
            "DevicePage",
            "--output",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert output_path.exists()
    assert "class DevicePage(BasePage):" in output_path.read_text(encoding="utf-8")


def test_generate_suite_contains_page_data_and_testcase():
    suite = generate_suite(DEVICE_SCRIPT, "DevicePage", "device_page.py", page_import="device.device_page")

    assert set(suite) == {"page", "data", "testcase"}
    assert "class DevicePage(BasePage):" in suite["page"]
    assert "device_cases:" in suite["data"]
    assert "imei: '869497052182449'" in suite["data"]
    assert "device_no: '869497052182449 573970116302449'" in suite["data"]
    assert "page_no_key: 'Enter'" in suite["data"]
    assert "from pages.device.device_page import DevicePage" in suite["testcase"]
    assert "@pytest.mark.device" in suite["testcase"]
    assert "self.page_obj.device_flow(case)" in suite["testcase"]
    ast.parse(suite["page"])
    ast.parse(suite["testcase"])


def test_cli_generates_suite_files(tmp_path):
    input_path = tmp_path / "input.py"
    suite_dir = tmp_path / "project"
    input_path.write_text('page.get_by_role("textbox", name="IMEI号 :").fill("123")\n', encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "utils/tools/po_style_converter.py",
            "--input",
            str(input_path),
            "--class-name",
            "DevicePage",
            "--file-name",
            "device_page.py",
            "--suite-dir",
            str(suite_dir),
            "--page-subdir",
            "pages/device",
            "--page-import",
            "device.device_page",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert (suite_dir / "pages" / "device" / "device_page.py").exists()
    assert (suite_dir / "data" / "device.yaml").exists()
    assert (suite_dir / "testcases" / "test_device.py").exists()
