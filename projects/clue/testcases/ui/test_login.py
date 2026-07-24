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
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "login_data.yaml")
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

    @pytest.mark.parametrize("case", cases["user_with_phone_page"], ids=lambda x: x["title"])
    def test_login_user(self, case):
        """
        网页登录：根据用例标题判断期望结果（成功或失败）
        - 标题包含"成功"：断言页面进入 /welcome，且导航栏头像 href = /${login}
        - 标题包含"失败"：仍停留在 /user/login
        """
        login = case.get("login")
        password = case.get("password")
        title = case.get("title", "")
        # 操作步骤：登录页输入用户名及密码，点击【登录】按钮，提交登录表单 -> 返回登录态(CommonPage)
        common_page = self.login_page.login_on_page_flow(login=login, password=password)

        # 断言：按标题分支
        if "成功" in title:
            # 断言：登录成功，页面进入 /welcome
            common_page.assert_on_home()
            # 断言：导航栏右上角用户头像区已渲染（登录成功才会出现）
            # 说明：当前系统头像是 ant-design Avatar（span），非 <a> 标签无 href，
            #       故用头像区容器可见性替代模板原「头像 a 标签 href=/${login}」断言
            common_page.assert_element_visible(locator=common_page.locator_avatar_nickname)
        else:
            # 断言：登录失败，仍停留在 /user/login
            common_page.assert_url_contains(url="/user/login")
