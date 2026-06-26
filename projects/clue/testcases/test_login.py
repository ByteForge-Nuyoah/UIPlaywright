# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_login.py
# @Software: PyCharm
# @Desc    : 登录功能测试用例

import os

import pytest
from loguru import logger
from playwright.sync_api import Page

from pages.login_page import LoginPage
from utils.files_utils.yaml_handle import YamlHandle


@pytest.mark.login
# 登录用例本身就是要验证 UI 登录流程，必须使用未登录的全新上下文，
# 通过 marker 覆盖项目级 conftest 注入的 storage_state。
@pytest.mark.browser_context_args(storage_state=None)
class TestLogin:
    """登录"""
    # 动态获取yaml数据文件路径
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "login_data.yaml")
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        logger.info("\n\n---------------Start: 开始测试-------------")
        self.login_page = LoginPage(page)
        self.login_page.navigate()
        # 登录测试需要测试登录功能，所以保留登录操作
        yield
        # 清除登录cookies，避免影响其他登录用例
        page.context.clear_cookies()

    @pytest.mark.parametrize("case", cases["login_cases"], ids=lambda x: x["title"])
    def test_login_user(self, case):
        """
        网页登录：根据用例标题判断期望结果（成功或失败）
        - 标题包含"成功"：login_on_page_flow() 返回 HomePage，断言已在 /welcome
        - 标题包含"失败"：仍停留在 /user/login，由 LoginPage 自身断言
        """
        login = case.get("login")
        password = case.get("password")
        title = case.get("title", "")

        # PO 链式：登录页 → 登录成功后直接拿到 HomePage 实例
        home_page = self.login_page.login_on_page_flow(login=login, password=password)

        if "成功" in title:
            # HomePage 自带断言方法，且 assert_on_home 返回 self，可继续链式
            home_page.assert_on_home()
        else:
            # 失败用例：链已断在登录页；直接在 login_page 上断言即可
            self.login_page.assert_url_contains(url="/user/login")
