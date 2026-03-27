# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : account_page.py
# @Software: PyCharm
# @Desc: TODO: Description

import allure
from utils.base_utils.base_page import BasePage


class AccountPage(BasePage):
    locator_menu_account_management = "text=账号管理"
    locator_btn_new_account = "xpath=//*[@id='corporation']/div/div[3]/div[3]/button/span"
    locator_btn_account_type = "xpath=//form/div[1]/div/div[2]/div/div/div/button[1]"
    locator_checkbox_role = "xpath=//*[@id='roles']/label/span[1]/input"
    locator_input_phone = "xpath=//*[@id='phone']"
    locator_input_name = "xpath=//*[@id='name']"
    locator_input_user_name = "xpath=//*[@id='user_name']"
    locator_input_password = "xpath=//*[@id='password']"
    locator_radio_status = "xpath=//*[@id='status']/label[1]/span[1]/input"
    locator_radio_allow_export = "xpath=//*[@id='allow_export']/label[2]/span[1]/input"
    locator_radio_allow_export_sensitive = "xpath=//*[@id='allow_export_sensitive']/label[2]"
    locator_btn_confirm = "xpath=/html/body/div[2]/div/div[2]/div/div[1]/div/div[3]/div/div/button[2]"

    @allure.step("点击【账号管理】菜单")
    def click_menu_account_management(self):
        self.click(self.locator_menu_account_management)

    @allure.step("点击【新建账号】按钮")
    def click_btn_new_account(self):
        self.click(self.locator_btn_new_account)
        # 使用智能等待替代强制等待，等待弹窗出现
        self.assert_element_visible(self.locator_btn_account_type)

    @allure.step("选择账号类型")
    def select_account_type(self):
        self.click(self.locator_btn_account_type)

    @allure.step("选择角色")
    def select_role(self):
        self.click(self.locator_checkbox_role)

    @allure.step("输入手机号：{phone}")
    def input_phone(self, phone):
        self.input(self.locator_input_phone, phone)

    @allure.step("输入姓名：{name}")
    def input_name(self, name):
        self.input(self.locator_input_name, name)

    @allure.step("输入账号名称：{user_name}")
    def input_user_name(self, user_name):
        self.input(self.locator_input_user_name, user_name)

    @allure.step("输入密码：{password}")
    def input_password(self, password):
        self.input(self.locator_input_password, password)

    @allure.step("选择账号状态")
    def select_status(self):
        self.click(self.locator_radio_status)

    @allure.step("选择导出状态")
    def select_allow_export(self):
        self.click(self.locator_radio_allow_export)

    @allure.step("选择导出敏感信息状态")
    def select_allow_export_sensitive(self):
        try:
            # Try to click with a short timeout, as this field might be hidden if Export is disabled
            self.page.click(self.locator_radio_allow_export_sensitive, timeout=3000)
        except Exception as e:
            print(f"Skipping allow_export_sensitive selection: {e}")

    @allure.step("点击【确定】按钮")
    def click_confirm(self):
        self.click(self.locator_btn_confirm)

    @allure.step("断言创建账号成功，校验用户名：{user_name}")
    def assert_create_success(self, user_name: str):
        """
        断言创建账号成功：
        1. 校验页面出现新账号用户名
        """
        self.assert_element_visible(f"text={user_name}")

    @allure.step("断言创建账号失败，校验错误信息包含：{keyword}")
    def assert_create_failed(self, keyword: str = "已存在"):
        """
        断言创建账号失败：
        1. 校验页面出现错误提示关键字（默认：已存在）
        """
        self.assert_element_visible(f"text={keyword}")

    @allure.step("创建账号流程")
    def create_account_flow(self, phone, name, user_name, password):
        """
        完整创建账号流程
        """
        self.click_menu_account_management()
        self.click_btn_new_account()
        self.select_account_type()
        self.select_role()
        self.input_phone(phone)
        self.input_name(name)
        self.input_user_name(user_name)
        self.input_password(password)
        self.select_status()
        self.select_allow_export()
        self.select_allow_export_sensitive()
        self.click_confirm()
