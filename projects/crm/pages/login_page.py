# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : login_page.py
# @Software: PyCharm
# @Desc    : CRM 登录页

import allure
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from config.global_vars import GLOBAL_VARS
from utils.base_utils.base_page import BasePage


class LoginPage(BasePage):
    """
    CRM 登录页（workspace-dev.spreadwin.cn/login）。
    定位器由 Playwright codegen 录制确认：
    - 账号/密码为带 label 的 textbox（label 文本「账号」「密码」）
    - 登录按钮为 role=button[name=登录]
    """
    # 登录方式切换 tab：录制为 page.locator("div").nth(1)，疑为「账号密码登录」tab；
    # 若页面默认即账号密码登录，可在 flow 中跳过 click_login_tab()，请按实际 DOM 校验后替换
    locator_login_tab = "xpath=(//div[contains(@class, 'ant-tabs-tab')])[2]"
    locator_page_username = "xpath=//label[contains(normalize-space(), '账号')]//following::input[1]"
    locator_page_password = "xpath=//label[contains(normalize-space(), '密码')]//following::input[1]"
    locator_page_login_btn = "xpath=//button[span[normalize-space()='登录'] or normalize-space()='登录']"
    # 登录成功后页面的「我的账号」入口
    locator_my_account = "xpath=//div[normalize-space()='我的账号']"

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

    @allure.step("点击【我的账号】")
    def click_my_account(self):
        """登录成功后点击页面上的「我的账号」入口"""
        self.click(self.locator_my_account)
        return self

    # --------------------- 流程 -------------------------------------
    @allure.step("网页登录：输入用户名：{login}，输入密码：{password}，点击【登录】按钮，提交登录表单")
    def login_on_page_flow(self, login, password):
        """
        核心登录操作 --> 输入用户名 + 密码 -> 提交表单。
        成功则 URL 离开登录页；失败仍停留。
        注意：不含 click_login_tab()，若页面默认非账号密码登录，调用方需先 click_login_tab()。

        :return: self（CRM 暂未建 home_page，调用方直接用 self.page 继续操作）
        """
        (self
         .input_username_on_page(login)
         .input_password_on_page(password)
         .submit_login_on_page())
        try:
            self.page.wait_for_url(lambda url: "/login" not in url, timeout=5000)
        except PlaywrightTimeoutError:
            pass
        return self

    @allure.step("CRM 登录完整录制流程：账号 {account} -> 登录 -> 进入我的账号")
    def login_recorded_flow(self, case):
        """
        还原 codegen 录制的完整流程：访问登录页 -> 切换 tab -> 输入账号 -> 账号回车
        -> 输入密码 -> 点击登录 -> 进入我的账号。
        录制中「账号 press Enter 后再次 fill 同一值」为试错冗余操作，已省略；
        账号/密码的 click 已与 fill 合并为 input（BasePage.input）。
        """
        (self
         .navigate()
         .click_login_tab()
         .input_username_on_page(case.get("account", ""))
         .press_username_key(case.get("account_key", "Enter"))
         .input_password_on_page(case.get("password", ""))
         .submit_login_on_page()
         .click_my_account())
        return self
