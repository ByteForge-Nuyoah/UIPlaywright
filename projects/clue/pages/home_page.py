# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc    : 登录成功后的入口页

import allure
from utils.base_utils.base_page import BasePage


class HomePage(BasePage):
    """
    系统首页（登录成功后的着陆页 /welcome）。
    """

    # 顶部用户信息（登录成功后会出现，可用于校验登录态）
    locator_welcome_tip = "xpath=//*[@id='root']/div/div[2]/div[2]/header[2]/div/div[3]/div/div/div/span/div/div[2]/div/span"
    @allure.step("校验已成功进入首页 /welcome")
    def assert_on_home(self):
        """
        断言当前确实在 /welcome 首页。
        登录失败时此断言会失败，链式调用就会在这里截断，不会误进子页面。
        """
        self.assert_url_contains(url="/welcome")
        return self

    @allure.step("从首页进入数据/欢迎页交互区")
    def goto_data(self):
        """
        进入数据概览/欢迎页交互区（DataPage 本身就在 /welcome 内，属首页内容）。

        :return: DataPage 实例
        """
        from pages.data_page import DataPage

        return DataPage(self.page)
