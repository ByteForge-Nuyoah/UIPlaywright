# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_data_page.py
# @Software: PyCharm
# @Desc    : 欢迎页/数据概览交互用例（演示 HomePage → DataPage 链式）

import os

import pytest
from loguru import logger
from playwright.sync_api import Page

from config.global_vars import GLOBAL_VARS
from pages.home_page import HomePage
from utils.files_utils.yaml_handle import YamlHandle


@pytest.mark.data
@pytest.mark.recordings
class TestDataPage:
    """欢迎页/数据概览"""

    # 动态获取yaml数据文件路径
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "data_page.yaml")
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        """
        page fixture 已通过项目级 conftest 注入 storage_state（默认携带登录态）。
        入口统一通过 HomePage 派发，体现完整 PO 链。
        """
        logger.info("\n\n---------------Start: 欢迎页交互测试-------------")
        # 先到 /welcome，再由 HomePage 派发到 DataPage
        page.goto(GLOBAL_VARS["url"])
        self.home_page = HomePage(page)
        yield

    @pytest.mark.parametrize("case", cases["data_cases"], ids=lambda x: x["title"])
    def test_data_interaction(self, case):
        """
        欢迎页交互：HomePage → DataPage 链式调用执行完整流程。
        """
        # PO 链：HomePage → DataPage → 完整交互流程 → 断言
        (self.home_page
            .goto_data()
            .data_interaction_flow(
                month_text=case.get("month_text", "1月"),
                range_label=case.get("range_label", "一年"),
                scope_label=case.get("scope_label", "所有"),
                company_title=case.get("company_title", "钉钉集团"),
                company_index=int(case.get("company_index", 1)),
            )
            .assert_url_contains(url="/welcome"))
