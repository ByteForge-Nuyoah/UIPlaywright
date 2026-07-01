# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : vehicle_list_page.py
# @Software: PyCharm
# @Desc    : 车辆管理/车辆列表

import allure
from utils.base_utils.base_page import BasePage


class VehicleListPage(BasePage):
    locator_input_device_no = "xpath=//input[@id='corporation_imei']"
    locator_btn_search = "xpath=//button[span[normalize-space()='查 询']]"
    locator_btn_reset = "xpath=//button[span[normalize-space()='重 置']]"
    locator_btn_expand = "xpath=//button[contains(., '展开')]"
    locator_checkbox_associated = "xpath=//label[.//span[normalize-space()='已关联']]//input[@type='checkbox']"
    locator_checkbox_unassociated = "xpath=//label[.//span[normalize-space()='未关联']]//input[@type='checkbox']"
    locator_btn_export = "xpath=//button[span[normalize-space()='导 出']]"
    locator_btn_export_desensitized = "xpath=//div[contains(@class, 'ant-popover')]//button[span[normalize-space()='导出脱敏数据']]"
    locator_btn_export_sensitive = "xpath=//div[contains(@class, 'ant-popover')]//button[span[normalize-space()='导出敏感数据']]"
    locator_dialog_export_sensitive = "xpath=//div[@role='dialog' and .//*[normalize-space()='导出敏感数据']]"
    locator_checkbox_sensitive_confirm = "xpath=//input[@id='agreement']"
    locator_btn_export_sensitive_confirm = "xpath=//div[contains(@class, 'ant-modal') and .//*[normalize-space()='导出敏感数据']]//button[span[normalize-space()='导出敏感数据']]"

    @allure.step("输入设备号：{device_no}")
    def input_device_no(self, device_no: str):
        self.input(self.locator_input_device_no, device_no)
        return self

    @allure.step("点击【查询】按钮")
    def click_search(self):
        self.click(self.locator_btn_search)
        return self

    @allure.step("点击【重置】按钮")
    def click_reset(self):
        self.click(self.locator_btn_reset)
        return self

    @allure.step("点击【展开】按钮")
    def click_expand(self):
        self.click(self.locator_btn_expand)
        return self

    @allure.step("选择关联状态：已关联")
    def select_associated(self):
        self.click(self.locator_checkbox_associated)
        return self

    @allure.step("选择关联状态：未关联")
    def select_unassociated(self):
        self.click(self.locator_checkbox_unassociated)
        return self

    @allure.step("点击【导出】按钮")
    def click_export(self):
        self.click(self.locator_btn_export)
        return self

    @allure.step("点击【导出脱敏数据】按钮")
    def click_export_desensitized(self):
        self.click(self.locator_btn_export_desensitized)
        return self

    @allure.step("点击【导出敏感数据】按钮")
    def click_export_sensitive(self):
        self.click(self.locator_btn_export_sensitive)
        return self

    @allure.step("勾选敏感数据导出确认")
    def select_sensitive_confirm(self):
        self.click(self.locator_checkbox_sensitive_confirm)
        return self

    @allure.step("点击敏感数据弹窗【导出敏感数据】按钮")
    def click_export_sensitive_confirm(self):
        self.click(self.locator_btn_export_sensitive_confirm)
        return self

    @allure.step("导出脱敏数据")
    def export_desensitized_data(self):
        self.click_export()
        with self.page.expect_download() as download_info:
            with self.page.expect_popup() as page_info:
                self.click_export_desensitized()
            popup_page = page_info.value
        download = download_info.value
        popup_page.close()
        return download

    @allure.step("导出敏感数据")
    def export_sensitive_data(self):
        self.click_export()
        self.click_export_sensitive()
        self.assert_element_visible(self.locator_dialog_export_sensitive)
        self.select_sensitive_confirm()
        with self.page.expect_download() as download_info:
            with self.page.expect_popup() as page_info:
                self.click_export_sensitive_confirm()
            popup_page = page_info.value
        download = download_info.value
        popup_page.close()
        return download

    @allure.step("车辆列表筛选与导出流程")
    def vehicle_list_filter_export_flow(self, device_no: str):
        """
        执行车辆列表筛选、重置、关联状态筛选、导出脱敏/敏感数据流程。
        """
        (self
         .input_device_no(device_no)
         .click_search()
         .click_reset()
         .click_expand()
         .select_associated()
         .click_search()
         .select_unassociated()
         .click_search())

        desensitized_download = self.export_desensitized_data()
        sensitive_download = self.export_sensitive_data()
        return desensitized_download, sensitive_download
