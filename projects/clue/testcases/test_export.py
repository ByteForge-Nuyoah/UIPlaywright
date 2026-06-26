# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_export.py
# @Software: PyCharm
# @Desc    : 导出文件

import os
import pytest
from loguru import logger
from playwright.sync_api import Page
from config.global_vars import GLOBAL_VARS
from utils.files_utils.yaml_handle import YamlHandle
from pages.export.export_page import ExportPage



@pytest.mark.export_record
@pytest.mark.recordings
class TestExportRecord:
    """ExportRecordPage录制流程"""

    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "export.yaml")
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        logger.info("\n\n---------------Start: 录制流程测试-------------")
        page.goto(GLOBAL_VARS["url"])
        self.page_obj = ExportPage(page)
        yield

    @pytest.mark.parametrize("case", cases["export_record_cases"], ids=lambda x: x["title"])
    def test_recorded_flow(self, case):
        self.page_obj.export_record_flow(case)
