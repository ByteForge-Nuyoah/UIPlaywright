# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : home_page.py
# @Software: PyCharm
# @Desc    : 登录成功后的入口页

import allure
from utils.base_utils.base_page import BasePage


class HomePage(BasePage):
    """
    系统首页（登录成功后的着陆页 /welcome
    """

    # 顶部用户信息（登录成功后会出现，可用于校验登录态）
    locator_welcome_tip = "xpath=//*[@id='root']/div/div[2]/div[2]/header[2]/div/div[3]/div/div/div/span/div/div[2]/div/span"
    # 左侧菜单
    locator_menu_account_management = "text=账号管理"
    locator_menu_vehicle_management = "text=车辆管理"

    @allure.step("校验已成功进入首页 /welcome")
    def assert_on_home(self):
        """
        断言当前确实在 /welcome 首页。
        登录失败时此断言会失败，链式调用就会在这里截断，不会误进子页面。
        """
        self.assert_url_contains(url="/welcome")
        return self

    @allure.step("从首页跳转到【账号管理】")
    def goto_account_management(self):
        """
        点击左侧菜单【账号管理】，进入账号管理子页面。

        :return: AccountPage 实例，供调用方继续链式操作
        """
        # 局部导入，避免与 HomePage 互相 import 形成循环
        from pages.account.account_page import AccountPage

        self.click(self.locator_menu_account_management)
        return AccountPage(self.page)

    @allure.step("从首页进入数据/欢迎页交互区")
    def goto_data(self):
        """
        进入数据概览/欢迎页交互区（DataPage 本身就在 /welcome 内）。

        :return: DataPage 实例
        """
        from pages.data.data_page import DataPage

        return DataPage(self.page)

    @allure.step("从首页跳转到【车辆管理】-【车辆列表】")
    def goto_vehicle_list(self):
        """
        点击左侧菜单【车辆管理】并进入【车辆列表】页面。

        :return: VehicleListPage 实例
        """
        from pages.vehicle.vehicle_list_page import VehicleListPage

        vehicle_list_page = VehicleListPage(self.page)
        vehicle_list_page.click_menu_vehicle_management().click_vehicle_list()
        return vehicle_list_page
