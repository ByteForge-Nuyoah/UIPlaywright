# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : login_page.py
# @Software: PyCharm
# @Desc    : 登录页 PO

import allure
from utils.base_utils.base_page import BasePage


class LoginPage(BasePage):
    """
    登录页。

    返回值约定：
    - 单步动作（input_xxx / submit_xxx）→ return self，便于页内链式
    - flow 方法（login_on_page_flow）→ 返回登录后期望的下一个 PO（HomePage）
      失败场景下 HomePage 实例仍可创建，但调用方应该先做 URL 断言再决定是否继续
    """
    # 网页登录
    locator_page_username = "id=user_name"
    locator_page_password = "id=password"
    locator_page_login_btn = "xpath=//*[@id='root']/div/div/form/button"
    # 登录成功后的 title（保留，便于将来直接在登录页做轻量断言）
    locator_welcome_tip = "xpath=//*[@id='root']/div/div[2]/div[2]/header[2]/div/div[3]/div/div/div/span/div/div[2]/div/span"

    @allure.step("访问登录页面：/user/login")
    def navigate(self, timeout: int = 30):
        """
        访问登录页面
        """
        self.visit("/user/login", timeout=timeout)
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
        完整登录操作 --> 输入用户名 + 密码 → 提交表单 → 返回首页 PO。

        设计：
        - 登录成功：调用方可直接链式 `.goto_account_management()` 等
        - 登录失败：URL 仍停留在 /user/login，调用方应在拿到 HomePage 实例后
          先做 URL 断言（assert_url_contains("/user/login")）再判断；
          失败用例通常不会再继续链式动作，所以 HomePage 实例可被丢弃。

        :return: HomePage 实例
        """
        # 局部导入，避免与 home_page 循环依赖
        from pages.home_page import HomePage

        (self
         .input_username_on_page(login)
         .input_password_on_page(password)
         .submit_login_on_page())
        # 给前端一点时间完成路由跳转 / 错误提示渲染
        self.page.wait_for_timeout(3000)
        return HomePage(self.page)
