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
from pages.common_page import CommonPage
from pages.account_page import AccountPage
from config.global_vars import GLOBAL_VARS
from utils.files_utils.yaml_handle import YamlHandle


@pytest.mark.account
class TestCreateAccount:
    """创建账号"""

    # 动态获取yaml数据文件路径
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "account_data.yaml")
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        """
        page fixture 已通过 projects/clue/testcases/conftest.py 的 storage_state
        默认携带登录态。打开首页后，由 CommonPage 经左侧菜单导航到账号管理页。
        """
        logger.info("\n\n---------------Start: 开始测试创建账号-------------")
        page.goto(GLOBAL_VARS["url"])
        # 持有 CommonPage：左侧菜单等跨页布局与导航的统一入口
        self.common_page = CommonPage(page)
        yield

    @pytest.mark.parametrize("case", cases["create_account_page"], ids=lambda x: x["title"])
    def test_create_account_success(self, case):
        """
        创建新账号：根据用例标题判断期望结果（成功或失败）
        - 标题包含"成功"：断言账号创建成功
        - 标题包含"失败"：断言创建失败，提示"已存在"
        """
        phone = case.get("phone")
        name = case.get("name")
        user_name = case.get("user_name")
        # 账号密码从环境变量注入，不在仓库内保留默认明文值
        password = os.getenv("CLUE_TEST_ACCOUNT_PASSWORD")
        if not password:
            pytest.skip("CLUE_TEST_ACCOUNT_PASSWORD 未配置，跳过创建账号用例")
        title = case.get("title", "")

        # 成功用例用随机 user_name + phone，避免二次运行账号已存在导致失败（clue 无删除接口，无法 teardown 清理）
        if "成功" in title:
            from utils.data_utils.faker_handle import FakerData
            import random
            user_name = f"auto_{FakerData.generate_identifier(char_len=8)}"
            phone = f"199{random.randint(10000000, 99999999)}"

        # 操作步骤：经左侧菜单进入账号管理页 → 输入手机号/姓名/用户名/密码 → 提交创建账号表单
        account_page = (
            self.common_page
            .goto(AccountPage, CommonPage.locator_menu_account_management)
            .create_account_flow(phone=phone, name=name, user_name=user_name, password=password)
        )

        # 断言：按标题分支
        if "成功" in title:
            # 断言：账号创建成功
            account_page.assert_create_success(user_name=user_name)
        else:
            # 断言：账号创建失败，提示"已存在"
            account_page.assert_create_failed(keyword="已存在")
