# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc    : 导出记录

import allure
from utils.base_utils.base_page import BasePage


class ExportPage(BasePage):
    locator_link_export_record = 'text=导出记录'
    locator_button_search = "xpath=//button[span[normalize-space()='查 询'] or normalize-space()='查 询']"
    locator_input_time = "xpath=//label[contains(normalize-space(), '时间')]//following::input[1]"
    locator_button_previous_month = "xpath=//button[@aria-label='上个月 (翻页上键)' and not(contains(@style, 'visibility: hidden'))]"
    locator_date_1 = "xpath=(//div[contains(@class, 'ant-picker-dropdown') and not(contains(@style, 'display: none'))]//div[normalize-space()='1'])[1]"
    locator_date_4 = "xpath=(//div[contains(@class, 'ant-picker-dropdown') and not(contains(@style, 'display: none'))]//div[normalize-space()='4'])[2]"
    locator_button_reset = "xpath=//button[span[normalize-space()='重 置'] or normalize-space()='重 置']"
    locator_checkbox_sensitive_download = "xpath=//label[contains(normalize-space(), '敏感下载')]//input[@type='checkbox']"
    locator_checkbox_desensitized_download = "xpath=//label[contains(normalize-space(), '脱敏下载')]//input[@type='checkbox']"
    locator_textbox_page_no = "xpath=//input[@aria-label='页']"

    @allure.step("点击【导出记录】")
    def click_export_record(self):
        self.click(self.locator_link_export_record)
        return self

    @allure.step("点击【查 询】")
    def click_search(self):
        self.click(self.locator_button_search)
        return self

    @allure.step("点击【时间】输入框")
    def click_time_input(self):
        self.click(self.locator_input_time)
        return self

    @allure.step("点击【上个月 (翻页上键)】")
    def click_previous_month(self):
        self.click(self.locator_button_previous_month)
        return self

    @allure.step("点击日期【1】")
    def click_date_1(self):
        self.click(self.locator_date_1)
        return self

    @allure.step("点击日期【4】")
    def click_date_4(self):
        self.click(self.locator_date_4)
        return self

    @allure.step("点击【重 置】")
    def click_reset(self):
        self.click(self.locator_button_reset)
        return self

    @allure.step("选择【敏感下载】")
    def select_sensitive_download(self):
        self.click(self.locator_checkbox_sensitive_download)
        return self

    @allure.step("选择【脱敏下载】")
    def select_desensitized_download(self):
        self.click(self.locator_checkbox_desensitized_download)
        return self

    @allure.step("输入页：{value}")
    def input_page_no(self, value):
        self.input(self.locator_textbox_page_no, value)
        return self

    @allure.step("在页按键：{key}")
    def press_page_no(self, key):
        self.press(self.locator_textbox_page_no, key)
        return self

    @allure.step("导出记录页完整流程")
    def export_record_flow(self, case):
        """
        由 Playwright 录制片段转换生成的完整流程。
        """
        (self
         .click_export_record()
         .click_search()
         .click_time_input()
         .click_previous_month()
         .click_date_1()
         .click_date_4()
         .click_search()
         .click_reset()
         .select_sensitive_download()
         .select_desensitized_download()
         .input_page_no(case.get("page_no", '5'))
         .press_page_no(case.get("page_no_key", 'Enter'))
         )
        return self
