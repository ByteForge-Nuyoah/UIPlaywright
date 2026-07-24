# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc    : CRM 登录页

import allure
from config.global_vars import GLOBAL_VARS
from utils.base_utils.base_page import BasePage
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class LoginPage(BasePage):
    """
    CRM 登录页
    """
    locator_login_tab = "xpath=(//div[contains(@class, 'ant-tabs-tab')])[2]"
    locator_page_username = "xpath=//label[contains(normalize-space(), '账号')]//following::input[1]"
    locator_page_password = "xpath=//label[contains(normalize-space(), '密码')]//following::input[1]"
    locator_page_login_btn = "xpath=//button[span[normalize-space()='登录'] or normalize-space()='登录']"

    @allure.step("访问 CRM 登录页面：/login")
    def navigate(self, timeout: int = 30000):
        """
        访问登录页面（base_url 由项目环境配置注入：test -> workspace-dev.spreadwin.cn）
        """
        self.page.goto(GLOBAL_VARS["url"] + "/login", timeout=timeout)
        self.wait_for_load_state()
        return self

    @allure.step("切换登录方式 tab")
    def click_login_tab(self):
        """切换到「账号密码登录」tab（若页面默认即是，可跳过此步）"""
        self.click(self.locator_login_tab)
        return self

    @allure.step("网页登录：输入用户名：{login}")
    def input_username_on_page(self, login):
        self.input(locator=self.locator_page_username, text=login)
        return self

    @allure.step("网页登录：在用户名输入框按键：{key}")
    def press_username_key(self, key):
        self.press(locator=self.locator_page_username, keyboard=key)
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
        登录操作 --> 输入用户名 + 密码 -> 提交表单 -> 返回首页。
        :return: HomePage 实例（登录成功后的着陆页，调用方可继续断言或经 CommonPage 跨页导航）
        """
        from pages.home_page import HomePage
        (self
         .input_username_on_page(login)
         .input_password_on_page(password)
         .submit_login_on_page())
        try:
            self.page.wait_for_url(lambda url: "/login" not in url, timeout=5000)
        except PlaywrightTimeoutError:
            pass
        return HomePage(self.page)

    @allure.step("CRM 登录完整录制流程：账号 {account} -> 登录 -> 进入我的账号")
    def login_recorded_flow(self, case):
        """
        访问登录页 -> 切换 tab -> 输入账号 -> 账号回车-> 输入密码 -> 点击登录 -> 进入我的账号。
        :return: MyAccountPage 实例
        """
        from pages.common_page import CommonPage
        from pages.my_account_page import MyAccountPage
        (self
         .navigate()
         .click_login_tab()
         .input_username_on_page(case.get("account", ""))
         .press_username_key(case.get("account_key", "Enter"))
         .input_password_on_page(case.get("password", ""))
         .submit_login_on_page())
        # 登录成功后经「我的账号」入口进入编辑页（入口定位由 CommonPage 统一维护）
        return CommonPage(self.page).goto(MyAccountPage, CommonPage.locator_entry_my_account)
