# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_my_account.py
# @Software: PyCharm
# @Desc    : CRM 我的账号-更新基本信息用例

import os

import pytest
from loguru import logger
from playwright.sync_api import Page

from config.global_vars import GLOBAL_VARS
from pages.common_page import CommonPage
from pages.my_account_page import MyAccountPage
from utils.files_utils.yaml_handle import YamlHandle


@pytest.mark.my_account
class TestMyAccount:
    """CRM 我的账号"""

    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "my_account.yaml")
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        """
        page fixture 已通过项目级 conftest 注入 storage_state（默认携带登录态）。
        打开首页后，由 CommonPage 经「我的账号」入口导航进入编辑页。
        """
        logger.info("\n\n---------------Start: 我的账号测试-------------")
        page.goto(GLOBAL_VARS["url"])
        # 持有 CommonPage：「我的账号」入口等跨页布局与导航的统一入口
        self.common_page = CommonPage(page)
        yield

    @pytest.mark.parametrize("case", cases["my_account_cases"], ids=lambda x: x["title"])
    def test_update_base_info(self, case):
        """我的账号：更新真实姓名/手机号/邮箱/头像、更新基本信息。"""
        # 操作步骤：经「我的账号」入口进入编辑页 -> 输入真实姓名/手机号/邮箱 -> 上传头像 -> 确定 -> 更新基本信息
        my_account_page = self.common_page.goto(MyAccountPage, CommonPage.locator_entry_my_account)
        my_account_page.my_account_update_flow(case)
        # 断言：更新后仍在我的账号页（更新基本信息按钮可见）
        my_account_page.assert_element_visible(my_account_page.locator_btn_update_base_info)
