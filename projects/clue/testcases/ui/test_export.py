# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc    : 导出文件

import os
import pytest
from loguru import logger
from playwright.sync_api import Page
from config.global_vars import GLOBAL_VARS
from utils.files_utils.yaml_handle import YamlHandle
from pages.export_page import ExportPage



@pytest.mark.export
class TestExportRecord:
    """Export"""

    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "export.yaml")
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        logger.info("\n\n---------------Start: 录制流程测试-------------")
        page.goto(GLOBAL_VARS["url"])
        self.page_obj = ExportPage(page)
        yield

    @pytest.mark.parametrize("case", cases["export_record_page"], ids=lambda x: x["title"])
    def test_recorded_flow(self, case):
        """导出录制文件：按用例数据执行完整导出流程。"""
        # 操作步骤：打开页面 → 按 page_no 翻页 → 触发导出录制文件流程
        self.page_obj.export_record_flow(case)
        # 断言：流程完成后仍在导出记录页（查询按钮可见）
        self.page_obj.assert_element_visible(self.page_obj.locator_button_search)
