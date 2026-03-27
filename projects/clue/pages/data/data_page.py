# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : data_page.py
# @Software: PyCharm
# @Desc: 数据概览/欢迎页交互

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
        self.visit("/welcome")

    @allure.step("点击【本周】筛选（第{index}处）")
    def click_week(self, index: int = 0):
        """
        点击“本周”筛选
        """
        if index == 0:
            self.click(self.locator_week)
        else:
            self.page.get_by_text("本周").nth(index).click()

    @allure.step("点击【本月】筛选（第{index}处）")
    def click_month(self, index: int = 0):
        """
        点击“本月”筛选
        """
        if index == 0:
            self.click(self.locator_month)
        else:
            self.page.get_by_text("本月").nth(index).click()

    @allure.step("点击【安装数】")
    def click_install_count(self):
        """
        点击“安装数”
        """
        self.click(self.locator_install_count)

    @allure.step("打开日期选择器并选择月份：{month_text}")
    def select_month(self, month_text: str = "1月"):
        """
        日期选择器选择月份
        """
        self.click(self.locator_date_picker_input)
        self.click(f"text={month_text}")

    @allure.step("点击范围按钮：{range_label}")
    def click_range_button(self, range_label: str = "一年"):
        """
        点击范围按钮（例如：一年）
        """
        self.click(f"role=button[name=\"{range_label}\"]")

    @allure.step("点击范围下拉：{scope_label}")
    def click_scope_button(self, scope_label: str = "所有"):
        """
        点击范围下拉（例如：所有）
        """
        self.click(f"role=button[name=\"{scope_label}\"]")

    @allure.step("进入模块：线索跟进情况")
    def enter_clue_follow_section(self):
        """
        进入“线索跟进情况”模块
        """
        self.click(self.locator_section_clue_follow)

    @allure.step("切换标签：事故线索")
    def switch_to_accident_clue_tab(self):
        """
        切换到“事故线索”标签
        """
        self.click(self.locator_tab_accident_clue)

    @allure.step("点击公司卡片（按title）：{title}（第{index}处）")
    def click_company_by_title(self, title: str, index: int = 0):
        """
        点击公司卡片，按 title 属性匹配
        """
        selector = f"[title=\"{title}\"]"
        elems = self.page.locator(selector)
        count = elems.count()
        target_index = index if index < count else 0
        elems.nth(target_index).click()

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
        欢迎页交互完整流程
        """
        self.click_week(index=0)
        self.click_month(index=0)
        self.click_install_count()
        self.click_week(index=1)
        self.click_month(index=2)
        self.select_month(month_text=month_text)
        self.click_range_button(range_label=range_label)
        self.click_scope_button(scope_label=scope_label)
        self.enter_clue_follow_section()
        self.switch_to_accident_clue_tab()
        self.click_company_by_title(title=company_title, index=company_index)
        # 使用智能等待替代强制等待，等待页面稳定
        self.assert_url_contains("/welcome")
