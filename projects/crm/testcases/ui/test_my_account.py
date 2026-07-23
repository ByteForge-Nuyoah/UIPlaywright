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
        打开首页后，由 MyAccountPage.navigate() 点击「我的账号」入口进入编辑页。
        """
        logger.info("\n\n---------------Start: 我的账号测试-------------")
        page.goto(GLOBAL_VARS["url"])
        self.page_obj = MyAccountPage(page)
        yield

    @pytest.mark.parametrize("case", cases["my_account_cases"], ids=lambda x: x["title"])
    def test_update_base_info(self, case):
        """我的账号：更新真实姓名/邮箱/头像、解除绑定微信、更新基本信息。"""
        # 操作步骤：进入我的账号 -> 编辑基本信息 -> 上传头像 -> 确定 -> 解绑微信 -> 更新
        self.page_obj.navigate().my_account_update_flow(case)
        # 断言：更新后仍在我的账号页（更新基本信息按钮可见）
        self.page_obj.assert_element_visible(self.page_obj.locator_btn_update_base_info)
