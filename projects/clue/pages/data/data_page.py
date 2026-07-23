# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : data_page.py
# @Software: PyCharm
# @Desc    : 数据概览/欢迎页交互

import allure
from utils.base_utils.base_page import BasePage


class DataPage(BasePage):
    # 区域/筛选
    locator_week = "text=本周"
    locator_month = "text=本月"
    locator_install_count = "text=安装数"
    locator_date_picker_input = ".ant-picker.ant-picker-borderless > .ant-picker-input"
    locator_button_year = "role=button[name=\"一年\"]"
    locator_button_all = "role=button[name=\"所有\"]"
    # 模块/标签
    locator_section_clue_follow = "text=线索跟进情况"
    locator_tab_accident_clue = "role=tab[name=\"事故线索\"]"

    @allure.step("访问欢迎页：/welcome")
    def navigate(self):
        """
        访问欢迎页
        """
        self.page.goto("/welcome")
        self.wait_for_load_state()
        return self

    @allure.step("点击【本周】筛选（第{index}处）")
    def click_week(self, index: int = 0):
        if index == 0:
            self.click(self.locator_week)
        else:
            self.page.get_by_text("本周").nth(index).click()
        return self

    @allure.step("点击【本月】筛选（第{index}处）")
    def click_month(self, index: int = 0):
        if index == 0:
            self.click(self.locator_month)
        else:
            self.page.get_by_text("本月").nth(index).click()
        return self

    @allure.step("点击【安装数】")
    def click_install_count(self):
        self.click(self.locator_install_count)
        return self

    @allure.step("打开日期选择器并选择月份：{month_text}")
    def select_month(self, month_text: str = "1月"):
        self.click(self.locator_date_picker_input)
        self.click(f"text={month_text}")
        return self

    @allure.step("点击范围按钮：{range_label}")
    def click_range_button(self, range_label: str = "一年"):
        self.click(f"role=button[name=\"{range_label}\"]")
        return self

    @allure.step("点击范围下拉：{scope_label}")
    def click_scope_button(self, scope_label: str = "所有"):
        self.click(f"role=button[name=\"{scope_label}\"]")
        return self

    @allure.step("进入模块：线索跟进情况")
    def enter_clue_follow_section(self):
        self.click(self.locator_section_clue_follow)
        return self

    @allure.step("切换标签：事故线索")
    def switch_to_accident_clue_tab(self):
        self.click(self.locator_tab_accident_clue)
        return self

    @allure.step("点击公司卡片（按title）：{title}（第{index}处）")
    def click_company_by_title(self, title: str, index: int = 0):
        selector = f"[title=\"{title}\"]"
        elems = self.page.locator(selector)
        count = elems.count()
        target_index = index if index < count else 0
        elems.nth(target_index).click()
        return self

    @allure.step("欢迎页交互流程")
    def data_interaction_flow(
        self,
        month_text: str = "1月",
        range_label: str = "一年",
        scope_label: str = "所有",
        company_title: str = "钉钉集团",
        company_index: int = 1
    ):
        """
        欢迎页交互完整流程；仍停留在欢迎页，故返回 self。
        """
        (self
         .click_week(index=0)
         .click_month(index=0)
         .click_install_count()
         .click_week(index=1)
         .click_month(index=2)
         .select_month(month_text=month_text)
         .click_range_button(range_label=range_label)
         .click_scope_button(scope_label=scope_label)
         .enter_clue_follow_section()
         .switch_to_accident_clue_tab()
         .click_company_by_title(title=company_title, index=company_index))
        # 智能等待，确认未跳离欢迎页
        self.assert_url_contains("/welcome")
        return self
