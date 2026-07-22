# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : login_page.py
# @Software: PyCharm
# @Desc    : CRM 登录页

import allure
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from utils.base_utils.base_page import BasePage


class LoginPage(BasePage):
    """
    CRM 登录页。
    """
    # TODO: 打开 https://workspace-dev.spreadwin.cn 登录页，用开发者工具确认以下定位器
    locator_page_username = "id=username"                       # TODO: 用户名输入框定位器
    locator_page_password = "id=password"                       # TODO: 密码输入框定位器
    locator_page_login_btn = "xpath=//button[@type='submit']"   # TODO: 登录按钮定位器

    @allure.step("访问 CRM 登录页面")
    def navigate(self, timeout: int = 30):
        """
        访问登录页面
        # TODO: 确认登录页路径，可能是 /login 或根路径重定向到登录页
        """
        self.visit("/login", timeout=timeout)
        return self

    @allure.step("网页登录：输入用户名：{login}")
    def input_username_on_page(self, login):
        self.input(locator=self.locator_page_username, text=login)
        return self

    @allure.step("网页登录：输入密码：{password}")
    def input_password_on_page(self, password):
        self.input(locator=self.locator_page_password, text=password)
        return self

    @allure.step("网页登录：点击【登录】按钮，提交登录表单")
    def submit_login_on_page(self):
        self.click(locator=self.locator_page_login_btn)
        return self

    # --------------------- 流程 -------------------------------------
    @allure.step("网页登录：输入用户名：{login}，输入密码：{password}，点击【登录】按钮，提交登录表单")
    def login_on_page_flow(self, login, password):
        """
        完整登录操作 --> 输入用户名 + 密码 -> 提交表单。
        成功则 URL 离开登录页；失败仍停留。

        :return: self（CRM 暂未建 home_page，调用方直接用 self.page 继续操作）
        """
        (self
         .input_username_on_page(login)
         .input_password_on_page(password)
         .submit_login_on_page())
        # TODO: 登录成功后按实际首页 URL 调整断言（这里先等离开 /login）
        try:
            self.page.wait_for_url(lambda url: "/login" not in url, timeout=5000)
        except PlaywrightTimeoutError:
            pass
        return self
