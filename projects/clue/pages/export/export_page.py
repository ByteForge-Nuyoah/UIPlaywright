# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : export_page.py
# @Software: PyCharm
# @Desc    : 导出记录

import allure
from utils.base_utils.base_page import BasePage


class ExportPage(BasePage):
    locator_link_export_record = 'text=导出记录'
    locator_button_search = "xpath=//button[span[normalize-space()='查 询'] or normalize-space()='查 询']"
    locator_textbox_element_19fcb9eb = "xpath=//label[contains(normalize-space(), '时间')]//following::input[1]"
    locator_button_previous_month = "xpath=//button[@aria-label='上个月 (翻页上键)' and not(contains(@style, 'visibility: hidden'))]"
    locator_text_1_1 = "xpath=(//div[contains(@class, 'ant-picker-dropdown') and not(contains(@style, 'display: none'))]//div[normalize-space()='1'])[1]"
    locator_text_4_3 = "xpath=(//div[contains(@class, 'ant-picker-dropdown') and not(contains(@style, 'display: none'))]//div[normalize-space()='4'])[2]"
    locator_button_reset = "xpath=//button[span[normalize-space()='重 置'] or normalize-space()='重 置']"
    locator_checkbox_element_1dd0c974 = "xpath=//label[contains(normalize-space(), '敏感下载')]//input[@type='checkbox']"
    locator_checkbox_element_acd2c2dc = "xpath=//label[contains(normalize-space(), '脱敏下载')]//input[@type='checkbox']"
    locator_textbox_page_no = "xpath=//input[@aria-label='页']"

    @allure.step("点击【导出记录】")
    def click_export_record(self):
        self.click(self.locator_link_export_record)
        return self

    @allure.step("点击【查 询】")
    def click_search(self):
        self.click(self.locator_button_search)
        return self

    @allure.step("点击【时间】")
    def click_element_19fcb9eb(self):
        self.click(self.locator_textbox_element_19fcb9eb)
        return self

    @allure.step("点击【上个月 (翻页上键)】")
    def click_previous_month(self):
        self.click(self.locator_button_previous_month)
        return self

    @allure.step("点击【1】")
    def click_1(self):
        self.click(self.locator_text_1_1)
        return self

    @allure.step("点击【4】")
    def click_4(self):
        self.click(self.locator_text_4_3)
        return self

    @allure.step("点击【重 置】")
    def click_reset(self):
        self.click(self.locator_button_reset)
        return self

    @allure.step("选择【敏感下载】")
    def select_element_1dd0c974(self):
        self.click(self.locator_checkbox_element_1dd0c974)
        return self

    @allure.step("选择【脱敏下载】")
    def select_element_acd2c2dc(self):
        self.click(self.locator_checkbox_element_acd2c2dc)
        return self

    @allure.step("输入页：{value}")
    def input_page_no(self, value):
        self.input(self.locator_textbox_page_no, value)
        return self

    @allure.step("在页按键：{key}")
    def press_page_no(self, key):
        self.press(self.locator_textbox_page_no, key)
        return self

    @allure.step("ExportRecordPage完整流程")
    def export_record_flow(self, case):
        """
        由 Playwright 录制片段转换生成的完整流程。
        """
        (self
         .click_export_record()
         .click_search()
         .click_element_19fcb9eb()
         .click_previous_month()
         .click_1()
         .click_4()
         .click_search()
         .click_reset()
         .select_element_1dd0c974()
         .select_element_acd2c2dc()
         .input_page_no(case.get("page_no", '5'))
         .press_page_no(case.get("page_no_key", 'Enter'))
         )
        return self
