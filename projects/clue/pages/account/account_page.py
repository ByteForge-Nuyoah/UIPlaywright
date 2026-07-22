# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : account_page.py
# @Software: PyCharm
# @Desc    : 账号管理页

import allure
from loguru import logger
from utils.base_utils.base_page import BasePage


class AccountPage(BasePage):
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
    # ant-design Modal 确定按钮（基于 ant-modal 模式，若弹窗非标准结构需 DOM 调整）
    locator_btn_confirm = "xpath=//div[contains(@class,'ant-modal')]//div[contains(@class,'ant-modal-footer')]//button[contains(@class,'ant-btn-primary')]"

    @allure.step("点击【新建账号】按钮")
    def click_btn_new_account(self):
        self.click(self.locator_btn_new_account)
        # 智能等待替代强制等待，等待弹窗出现
        self.assert_element_visible(self.locator_btn_account_type)
        return self

    @allure.step("选择账号类型")
    def select_account_type(self):
        self.click(self.locator_btn_account_type)
        return self

    @allure.step("选择角色")
    def select_role(self):
        self.click(self.locator_checkbox_role)
        return self

    @allure.step("输入手机号：{phone}")
    def input_phone(self, phone):
        self.input(self.locator_input_phone, phone)
        return self

    @allure.step("输入姓名：{name}")
    def input_name(self, name):
        self.input(self.locator_input_name, name)
        return self

    @allure.step("输入账号名称：{user_name}")
    def input_user_name(self, user_name):
        self.input(self.locator_input_user_name, user_name)
        return self

    @allure.step("输入密码：{password}")
    def input_password(self, password):
        self.input(self.locator_input_password, password)
        return self

    @allure.step("选择账号状态")
    def select_status(self):
        self.click(self.locator_radio_status)
        return self

    @allure.step("选择导出状态")
    def select_allow_export(self):
        self.click(self.locator_radio_allow_export)
        return self

    @allure.step("选择导出敏感信息状态")
    def select_allow_export_sensitive(self):
        try:
            # 短超时尝试点击；若导出关闭则该字段隐藏，跳过即可
            self.click(self.locator_radio_allow_export_sensitive, timeout=3000)
        except Exception as e:
            logger.warning(f"跳过导出敏感信息选择（字段可能隐藏）：{e}")
        return self

    @allure.step("点击【确定】按钮")
    def click_confirm(self):
        self.click(self.locator_btn_confirm)
        return self

    @allure.step("断言创建账号成功，校验用户名：{user_name}")
    def assert_create_success(self, user_name: str):
        """
        断言创建账号成功：校验页面出现新账号用户名
        """
        self.assert_element_visible(f"text={user_name}")
        return self

    @allure.step("断言创建账号失败，校验错误信息包含：{keyword}")
    def assert_create_failed(self, keyword: str = "已存在"):
        """
        断言创建账号失败：校验页面出现错误提示关键字
        """
        self.assert_element_visible(f"text={keyword}")
        return self

    @allure.step("创建账号流程")
    def create_account_flow(self, phone, name, user_name, password):
        """
        完整创建账号流程；仍停留在账号管理页，故返回 self。
        导航到账号管理页由 CommonPage.goto_account_management 负责，此处只做建账号操作。
        """
        (self
         .click_btn_new_account()
         .select_account_type()
         .select_role()
         .input_phone(phone)
         .input_name(name)
         .input_user_name(user_name)
         .input_password(password)
         .select_status()
         .select_allow_export()
         .select_allow_export_sensitive()
         .click_confirm())
        return self
