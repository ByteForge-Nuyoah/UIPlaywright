# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_create_account.py
# @Software: PyCharm
# @Desc    : CRM 创建账号测试用例

import os

import pytest
from loguru import logger
from playwright.sync_api import Page

from config.global_vars import GLOBAL_VARS
from pages.common_page import CommonPage
from pages.create_account_page import CreateAccountPage
from utils.files_utils.yaml_handle import YamlHandle


@pytest.mark.create_account
class TestCreateAccount:
    """创建账号"""

    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "create_account.yaml")
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        """
        page fixture 已通过项目级 conftest 注入 storage_state（默认携带登录态）。
        打开首页后，由 CommonPage 经菜单「账号」导航到账号管理页。
        """
        logger.info("\n\n---------------Start: 创建账号测试-------------")
        page.goto(GLOBAL_VARS["url"])
        # 持有 CommonPage：侧边菜单等跨页布局与导航的统一入口
        self.common_page = CommonPage(page)
        yield

    @pytest.mark.parametrize("case", cases["create_account_cases"], ids=lambda x: x["title"])
    def test_create_account(self, case):
        """
        创建账号：根据用例标题判断期望结果（成功或失败）
        - 标题含「成功」：断言账号创建成功（弹窗关闭 + 列表出现新账号）
        - 其余：断言创建失败，提示包含 error_keyword
        注意：当前 admin 账号「为下一级创建一个管理员账号」配额已满，默认用例为失败分支。
        """
        title = case.get("title", "")
        user_name = case.get("user_name")
        phone = case.get("phone")
        # 成功用例用随机 user_name + phone，避免二次运行账号已存在导致失败
        if "成功" in title:
            from utils.data_utils.faker_handle import FakerData
            import random
            user_name = f"auto_{FakerData.generate_identifier(char_len=8)}"
            phone = f"199{random.randint(10000000, 99999999)}"
        flow_case = {**case, "user_name": user_name, "phone": phone}

        # 操作步骤：经菜单进入账号管理页 -> 打开创建表单 -> 填写并选择 -> 提交
        create_account_page = self.common_page.goto(CreateAccountPage, CommonPage.locator_menu_account)
        create_account_page.create_account_flow(flow_case)

        # 断言：按标题分支
        if "成功" in title:
            create_account_page.assert_create_success(user_name=user_name)
        else:
            create_account_page.assert_create_failed(
                keyword=case.get("error_keyword", "只能为下一级创建一个账号作为管理员")
            )
