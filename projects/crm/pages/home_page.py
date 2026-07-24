# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc    : CRM 登录成功后的入口页（根路径 /）

import re
import allure
from playwright.sync_api import expect
from utils.base_utils.base_page import BasePage


class HomePage(BasePage):
    """
    CRM 首页（登录成功后的着陆页，根路径 /）。
    只封装首页自身的内容；顶部头像 / 左侧菜单等跨页共享布局与导航见 CommonPage。
    """

    @allure.step("校验已成功进入 CRM 首页")
    def assert_on_home(self, timeout: int = 10000):
        """
        断言登录成功：URL 已离开 /login，进入首页。
        登录失败时 URL 仍停留在 /login，此断言会失败，链式调用在此截断。
        """
        expect(self.page).not_to_have_url(re.compile("/login"), timeout=timeout)
        return self
