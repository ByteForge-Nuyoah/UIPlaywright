# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_create_account.py
# @Software: PyCharm
# @Desc: 创建账号测试用例

import pytest
from loguru import logger
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.account.account_page import AccountPage
from config.global_vars import GLOBAL_VARS
import os
from utils.files_utils.yaml_handle import YamlHandle

@pytest.mark.account
class TestCreateAccount:
    """创建账号"""

    # 动态获取yaml数据文件路径
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "account_data.yaml")
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        logger.info("\n\n---------------Start: 开始测试创建账号-------------")
        # 登录
        self.login_page = LoginPage(page)
        self.login_page.navigate()
        # 使用配置文件中的用户名密码登录
        self.login_page.login_on_page_flow(login=GLOBAL_VARS.get("admin_user_name"),
                                           password=str(GLOBAL_VARS.get("admin_user_password")))

        # 初始化账号页面
        self.account_page = AccountPage(page)

        yield

        # 清除登录cookies，避免影响其他登录用例
        page.context.clear_cookies()

    @pytest.mark.parametrize("case", cases["account_cases"], ids=lambda x: x["title"])
    def test_create_account_success(self, case):
        """
        测试创建新账号：根据标题判断成功或失败并断言结果
        """
        phone = case.get("phone")
        name = case.get("name")
        user_name = case.get("user_name")
        password = case.get("password")

        # 执行创建账号流程
        self.account_page.create_account_flow(phone=phone, name=name, user_name=user_name, password=password)

        # 断言结果
        title = case.get("title", "")
        if "成功" in title:
            self.account_page.assert_create_success(user_name=user_name)
        else:
            self.account_page.assert_create_failed(keyword="已存在")
