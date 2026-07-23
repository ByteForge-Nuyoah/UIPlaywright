# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc    : 登录页

import allure
from config.global_vars import GLOBAL_VARS
from utils.base_utils.base_page import BasePage
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class LoginPage(BasePage):
    # 网页登录
    locator_page_username = "id=user_name"
    locator_page_password = "id=password"
    locator_page_login_btn = "xpath=//*[@id='root']/div/div/form/button"

    @allure.step("访问登录页面：/user/login")
    def navigate(self, timeout: int = 30000):
        """
        访问登录页面
        """
        self.page.goto(GLOBAL_VARS["url"] + "/user/login", timeout=timeout)
        self.wait_for_load_state()
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
        完整登录操作 --> 输入用户名 + 密码 → 提交表单 → 返回首页。
        设计：
        - 登录成功：返回 HomePage；后续跨页导航用 CommonPage(page).goto_xxx()
        - 登录失败：URL 仍停留在 /user/login，调用方应在拿到 HomePage 实例后
          先做 URL 断言（assert_url_contains("/user/login")）再判断；
          失败用例通常不会再继续链式动作，所以 HomePage 实例可被丢弃。

        :return: HomePage 实例
        """
        from pages.home_page import HomePage

        self.input_username_on_page(login) # 输入用户名
        self.input_password_on_page(password) # 输入密码
        self.submit_login_on_page() # 提交表单
        try:
            self.page.wait_for_url(lambda url: "/user/login" not in url, timeout=5000)
        except PlaywrightTimeoutError:
            pass
        return HomePage(self.page)
