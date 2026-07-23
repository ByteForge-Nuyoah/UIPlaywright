# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc    : 跨页面通用页面对象：登录态布局壳（顶部头像 + 左侧菜单）与跨页导航

import allure
from utils.base_utils.base_page import BasePage


class CommonPage(BasePage):
    """
    跨页面通用页面对象：封装登录后所有页面共享的布局壳元素与跨页导航。
    - 顶部：用户头像区
    - 左侧：导航菜单（ant-design pro 持久 layout，非任一具体页面专属）
    继承 BasePage，直接复用 is_element_attr_have_value / assert_element_visible 等通用断言方法。
    """
    locator_avatar_nickname = ".ant-pro-global-header-header-actions-avatar"

    # 左侧导航菜单（登录后所有页面共享的 layout chrome）
    locator_menu_account_management = "text=账号管理"
    locator_menu_vehicle_management = "text=车辆管理"
    locator_link_vehicle_list = "text=车辆列表"

    @allure.step("从左侧菜单跳转到【账号管理】")
    def goto_account_management(self):
        """
        点击左侧菜单【账号管理】，进入账号管理子页面。
        :return: AccountPage 实例，供调用方继续链式操作
        """
        # 局部导入，避免与子页面互相 import 形成循环
        from pages.account_page import AccountPage
        self.click(self.locator_menu_account_management)
        return AccountPage(self.page)

    @allure.step("从左侧菜单跳转到【车辆管理】-【车辆列表】")
    def goto_vehicle_list(self):
        """
        点击左侧菜单【车辆管理】，再点击子菜单【车辆列表】，进入车辆列表页面。
        :return: VehicleListPage 实例
        """
        from pages.vehicle_list_page import VehicleListPage
        self.click(self.locator_menu_vehicle_management)
        self.click(self.locator_link_vehicle_list)
        return VehicleListPage(self.page)
