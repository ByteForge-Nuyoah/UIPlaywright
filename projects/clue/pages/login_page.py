# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : login_page.py
# @Software: PyCharm
# @Desc: TODO: Description

import allure
from utils.base_utils.base_page import BasePage


class LoginPage(BasePage):
    # 网页登录
    locator_page_username = "id=user_name"
    locator_page_password = "id=password"
    locator_page_login_btn = "xpath=//*[@id='root']/div/div/form/button"
    # 登录成功后的 title
    locator_welcome_tip = "xpath=//*[@id='root']/div/div[2]/div[2]/header[2]/div/div[3]/div/div/div/span/div/div[2]/div/span"

    @allure.step("访问登录页面：/user/login")
    def navigate(self, timeout: int = 30):
        """
        访问登录页面
        """
        self.visit("/user/login", timeout=timeout)

    @allure.step("网页登录：输入用户名：{login}")
    def input_username_on_page(self, login):
        """
        网页登录：输入用户名
        """
        self.input(locator=self.locator_page_username, text=login)

    @allure.step("网页登录：输入密码：{password}")
    def input_password_on_page(self, password):
        """
        网页登录：输入密码
        """
        self.input(locator=self.locator_page_password, text=password)

    @allure.step("网页登录：点击【登录】按钮，提交登录表单")
    def submit_login_on_page(self):
        """
        网页登录：点击登录按钮，提交登录表单
        """
        self.click(locator=self.locator_page_login_btn)

    # --------------------- 流程 -------------------------------------
    @allure.step("网页登录：输入用户名：{login}，输入密码：{password}，点击【登录】按钮，提交登录表单")
    def login_on_page_flow(self, login, password):
        """
        完整登录操作 --> 网页登录：输入用户名，密码，点击登录按钮，提交登录表单
        """
        self.input_username_on_page(login)
        self.input_password_on_page(password)
        self.submit_login_on_page()
        self.page.wait_for_timeout(3000)
        # 断言登录成功后的 title 是否包含用户名
        # self.assert_text_contains(locator=self.locator_welcome_tip, text=login)
