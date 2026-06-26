# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_create_account.py
# @Software: PyCharm
# @Desc    : 创建账号测试用例

import os
import pytest
from loguru import logger
from playwright.sync_api import Page
from pages.home_page import HomePage
from config.global_vars import GLOBAL_VARS
from utils.files_utils.yaml_handle import YamlHandle


@pytest.mark.account
class TestCreateAccount:
    """创建账号"""

    # 动态获取yaml数据文件路径
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "account_data.yaml")
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        """
        page fixture 已通过 projects/clue/testcases/conftest.py 的 storage_state
        默认携带登录态。这里只需打开首页 → 由 HomePage 派发到 AccountPage，
        即可在用例里走完整的 PO 链。
        """
        logger.info("\n\n---------------Start: 开始测试创建账号-------------")
        page.goto(GLOBAL_VARS["url"])
        # 入口只持有 HomePage；具体子 PO 由它的导航方法返回
        self.home_page = HomePage(page)
        yield

    @pytest.mark.parametrize("case", cases["account_cases"], ids=lambda x: x["title"])
    def test_create_account_success(self, case):
        """
        创建新账号：演示从首页 → 账号管理页 → 创建账号 的完整链式 PO 流转。
        """
        phone = case.get("phone")
        name = case.get("name")
        user_name = case.get("user_name")
        password = case.get("password")
        title = case.get("title", "")

        # 链式 PO：HomePage → AccountPage → 完整创建流程，全链路一气呵成
        account_page = (
            self.home_page
            .goto_account_management()
            .create_account_flow(phone=phone, name=name, user_name=user_name, password=password)
        )

        # 断言结果
        if "成功" in title:
            account_page.assert_create_success(user_name=user_name)
        else:
            account_page.assert_create_failed(keyword="已存在")
