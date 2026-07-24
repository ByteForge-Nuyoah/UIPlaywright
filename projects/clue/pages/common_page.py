# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc    : 跨页面通用页面对象：登录态布局壳（顶部头像 + 左侧菜单）、跨页导航与登录态校验

import re
import allure
from utils.base_utils.base_page import BasePage


class CommonPage(BasePage):
    """
    跨页面通用页面对象：登录后所有页面共享的布局壳元素、跨页导航与登录态校验。
    - 顶部：用户头像区
    - 左侧：导航菜单（ant-design pro 持久 layout，非任一具体页面专属）
    - 跨页导航：通过 goto(page_cls, *targets) 通用跳转，新增页面无需在本类加方法，
      只需把新的菜单/链接定位器作为类属性补一行即可。

    继承 BasePage，直接复用 is_element_attr_have_value / assert_element_visible 等通用断言方法。
    """
    locator_avatar_nickname = ".ant-pro-global-header-header-actions-avatar"

    # 左侧导航菜单（登录后所有页面共享的 layout chrome）
    locator_menu_account_management = "text=账号管理"
    locator_menu_vehicle_management = "text=车辆管理"
    locator_link_vehicle_list = "text=车辆列表"

    @allure.step("校验已成功登录（URL 已进入 /welcome）")
    def assert_on_home(self, timeout: int = 5000):
        """
        断言登录成功：URL 已进入 /welcome 着陆页。
        登录失败时 URL 仍停留在 /user/login，此断言会失败，链式调用在此截断。
        （原 HomePage 的职责，登录态校验归入 CommonPage 后首页壳不再单独建类。）
        """
        self.assert_url_contains(url="/welcome", timeout=timeout)
        return self

    @allure.step("点击导航目标：{target}")
    def click_nav(self, target: str):
        """
        点击一个导航目标。target 为完整定位器（xpath=/text=/css=//./#）时直接使用，
        否则按 text=<target> 包裹（适用于纯文本菜单项）。
        """
        locator = target if re.match(r"^(xpath=|text=|css=|//|\.|#)", target) else f"text={target}"
        self.click(locator)
        return self

    @allure.step("跨页导航到目标页面")
    def goto(self, page_cls, *targets):
        """
        按顺序点击若干导航目标（菜单/链接）后，构造并返回目标页面对象。
        新增页面零改本类：调用方传入定位器即可，无需在此添加 goto_xxx 方法。

        :param page_cls: 目标页面对象类（如 VehicleListPage）
        :param targets: 依次点击的导航定位器（本类的 locator_* 属性或任意定位器串）
        :return: page_cls 实例
        """
        for target in targets:
            self.click_nav(target)
        return page_cls(self.page)
