# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc    : 跨页面通用页面对象：登录态布局壳（顶部头像）、跨页导航与登录态校验

import re
import allure
from playwright.sync_api import expect
from utils.base_utils.base_page import BasePage


class CommonPage(BasePage):
    """
    跨页面通用页面对象：登录后所有页面共享的布局壳元素、跨页导航与登录态校验。
    继承 BasePage，直接复用 assert_element_visible 等通用断言方法。
    """
    # 顶部用户头像区
    locator_avatar = ".ant-pro-global-header-header-actions-avatar"
    # 我的账号」入口
    locator_entry_my_account = "xpath=//div[normalize-space()='我的账号']"
    # 侧边菜单「账号」项（点击进入账号管理列表页）；用 normalize-space 精确匹配，排除「我的账号」
    locator_menu_account = "xpath=//li[contains(@class,'sub-menu') and normalize-space()='账号']"

    @allure.step("校验已成功登录（URL 已离开 /login）")
    def assert_on_home(self, timeout: int = 10000):
        """
        断言登录成功：URL 已离开 /login，进入登录后着陆态。
        登录失败时 URL 仍停留在 /login，此断言会失败，链式调用在此截断。
        （原 HomePage 的职责，登录态校验归入 CommonPage 后首页壳不再单独建类。）
        """
        expect(self.page).not_to_have_url(re.compile("/login"), timeout=timeout)
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
        按顺序点击若干导航目标（菜单/入口）后，构造并返回目标页面对象。
        新增页面零改本类：调用方传入定位器即可，无需在此添加 goto_xxx 方法。

        :param page_cls: 目标页面对象类（如 CreateAccountPage）
        :param targets: 依次点击的导航定位器（本类的 locator_* 属性或任意定位器串）
        :return: page_cls 实例
        """
        for target in targets:
            self.click_nav(target)
        return page_cls(self.page)
