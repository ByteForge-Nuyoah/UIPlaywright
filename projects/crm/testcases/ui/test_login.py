# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_login.py
# @Software: PyCharm
# @Desc    : CRM 登录功能测试用例

import os

import pytest
from loguru import logger
from playwright.sync_api import Page

from pages.login_page import LoginPage
from utils.files_utils.yaml_handle import YamlHandle


@pytest.mark.login
# 登录用例本身要验证 UI 登录流程，必须使用未登录的全新上下文，
# 通过 marker 覆盖项目级 conftest 注入的 storage_state。
@pytest.mark.browser_context_args(storage_state=None)
class TestLogin:
    """CRM 登录"""
    # 动态获取 yaml 数据文件路径
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "login_data.yaml")
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        logger.info("\n\n---------------Start: 开始测试-------------")
        self.login_page = LoginPage(page)
        self.login_page.navigate()
        yield
        # 清除登录 cookies，避免影响其他登录用例
        page.context.clear_cookies()

    @pytest.mark.parametrize("case", cases["user_with_phone_page"], ids=lambda x: x["title"])
    def test_login_user(self, case):
        """
        网页登录：输入用户名密码并提交，按用例标题分支断言登录成功/失败。
        - 标题含「成功」：URL 离开 /login（登录成功跳转）
        - 标题含「失败」：仍停留在 /login
        """
        login = case.get("login")
        password = case.get("password")
        title = case.get("title", "")
        self.login_page.login_on_page_flow(login=login, password=password)

        if "成功" in title:
            # 断言：登录成功，URL 离开登录页
            self.login_page.page.wait_for_url(lambda url: "/login" not in url, timeout=10000)
        else:
            # 断言：登录失败，仍停留在 /login
            assert "/login" in self.login_page.page.url, "登录失败时应停留在登录页"
