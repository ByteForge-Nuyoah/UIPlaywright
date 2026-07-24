# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc    : CRM 创建账号页（账号管理 -> 创建账号 弹窗表单，Element Plus）

import allure
from utils.base_utils.base_page import BasePage


class CreateAccountPage(BasePage):
    """
    CRM 创建账号页：账号管理列表页的「创建账号」弹窗表单
    """
    # 账号管理列表页的「创建账号」按钮
    locator_btn_create = "xpath=//button[span[normalize-space()='创建账号'] or normalize-space()='创建账号']"
    # 表单输入框（Element Plus el-form-item label 文本定位）
    locator_input_user_name = "xpath=//label[normalize-space()='用户名']//following::input[1]"
    locator_input_real_name = "xpath=//label[normalize-space()='真实姓名']//following::input[1]"
    locator_input_phone = "xpath=//label[normalize-space()='手机号']//following::input[1]"
    locator_input_email = "xpath=//label[normalize-space()='E-mail']//following::input[1]"
    locator_input_password = "xpath=//label[normalize-space()='密码']//following::input[1]"
    locator_input_confirm_password = "xpath=//label[normalize-space()='确认密码']//following::input[1]"
    # 提交按钮「确认」
    locator_btn_confirm = "xpath=//button[span[normalize-space()='确认'] or normalize-space()='确认']"
    # Element Plus 全局消息提示（提交后的成功/错误信息）
    locator_msg = ".el-message__content"

    def _select_el_option(self, field, option):
        wrapper = (f"//div[contains(@class,'el-form-item') and "
                   f".//label[normalize-space()='{field}']]//div[contains(@class,'el-select__wrapper')]")
        self.click(wrapper)
        self.page.get_by_role("option", name=option, exact=True).click()
        return self

    @allure.step("点击【创建账号】打开创建表单")
    def open_create_form(self):
        self.click(self.locator_btn_create)
        # 等待表单弹窗渲染（用户名输入框可见即代表表单已打开）
        self.assert_element_visible(self.locator_input_user_name)
        return self

    @allure.step("输入登录用户名：{user_name}")
    def input_user_name(self, user_name):
        self.input(self.locator_input_user_name, user_name)
        return self

    @allure.step("输入真实姓名：{real_name}")
    def input_real_name(self, real_name):
        self.input(self.locator_input_real_name, real_name)
        return self

    @allure.step("输入手机号：{phone}")
    def input_phone(self, phone):
        self.input(self.locator_input_phone, phone)
        return self

    @allure.step("输入邮箱：{email}")
    def input_email(self, email):
        self.input(self.locator_input_email, email)
        return self

    @allure.step("选择品牌商：{brand}")
    def select_brand(self, brand):
        self._select_el_option("品牌商", brand)
        return self

    @allure.step("选择角色：{role}")
    def select_role(self, role):
        self._select_el_option("角色", role)
        return self

    @allure.step("输入密码：{password}")
    def input_password(self, password):
        self.input(self.locator_input_password, password)
        return self

    @allure.step("输入确认密码：{confirm_password}")
    def input_confirm_password(self, confirm_password):
        self.input(self.locator_input_confirm_password, confirm_password)
        return self

    @allure.step("点击【确认】提交创建账号表单")
    def click_confirm(self):
        self.click(self.locator_btn_confirm)
        return self

    # --------------------- 断言 -------------------------------------
    @allure.step("断言创建失败，错误提示包含：{keyword}")
    def assert_create_failed(self, keyword):
        self.assert_text_contains(self.locator_msg, keyword, timeout=8000)
        return self

    @allure.step("断言创建成功，校验用户名：{user_name}")
    def assert_create_success(self, user_name):
        """
        断言创建成功：弹窗关闭 + 账号列表出现新用户名。
        """
        self.assert_element_hidden(self.locator_btn_confirm, timeout=8000)
        self.assert_element_visible(f"text={user_name}")
        return self

    # --------------------- 流程 -------------------------------------
    @allure.step("创建账号流程")
    def create_account_flow(self, case):
        """
        完整流程
        """
        password = case.get("password", "")
        (self
         .open_create_form()
         .input_user_name(case.get("user_name", ""))
         .input_real_name(case.get("real_name", ""))
         .input_phone(case.get("phone", ""))
         .input_email(case.get("email", ""))
         .select_brand(case.get("brand", ""))
         .select_role(case.get("role", ""))
         .input_password(password)
         .input_confirm_password(case.get("confirm_password", password))
         .click_confirm())
        return self
