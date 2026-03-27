# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_data_page.py
# @Software: PyCharm
# @Desc: 欢迎页/数据概览交互用例

import os
import pytest
from loguru import logger
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.data.data_page import DataPage
from config.global_vars import GLOBAL_VARS
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
        登录并进入欢迎页
        """
        logger.info("\n\n---------------Start: 欢迎页交互测试-------------")
        self.login_page = LoginPage(page)
        self.login_page.navigate()
        self.login_page.login_on_page_flow(
            login=str(GLOBAL_VARS.get("admin_user_name")),
            password=str(GLOBAL_VARS.get("admin_user_password")),
        )
        self.data_page = DataPage(page)
        self.data_page.navigate()
        yield
        page.context.clear_cookies()

    @pytest.mark.parametrize("case", cases["data_cases"], ids=lambda x: x["title"])
    def test_data_interaction(self, case):
        """
        欢迎页交互：按录制脚本还原流程
        """
        self.data_page.data_interaction_flow(
            month_text=case.get("month_text", "1月"),
            range_label=case.get("range_label", "一年"),
            scope_label=case.get("scope_label", "所有"),
            company_title=case.get("company_title", "钉钉集团"),
            company_index=int(case.get("company_index", 1)),
        )
        # 基础断言：仍处于欢迎页
        self.data_page.assert_url_contains(url="/welcome")
