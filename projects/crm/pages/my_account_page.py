# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc    : CRM 我的账号页（个人基本信息编辑）

import allure
from utils.base_utils.base_page import BasePage


class MyAccountPage(BasePage):
    """
    CRM 我的账号页：编辑真实姓名/手机号/邮箱/头像、更新基本信息。
    """
    # 表单输入框：ant-design Form 的 label 文本定位
    locator_input_real_name = "xpath=//label[contains(normalize-space(), '真实姓名')]//following::input[1]"
    # 录制为 get_by_role("textbox", name="手机号", exact=True)，转换器未识别 exact=True，手工补
    locator_input_phone = "xpath=//label[contains(normalize-space(), '手机号')]//following::input[1]"
    locator_input_email = "xpath=//label[contains(normalize-space(), '邮箱')]//following::input[1]"
    # 头像 figure：点击后挂载隐藏 input[type=file]（当前页面 label「点击上传头像」/ button「重新上传」均不存在）
    locator_avatar_figure = "figure > .avatar"
    # 头像上传：点击 figure 后挂载出的隐藏 input[type=file]，set_input_files 直接作用其上
    locator_input_avatar_upload = "xpath=(//input[@type='file'])[1]"
    # 头像裁剪/确认弹窗的「确定」按钮
    locator_btn_confirm = "xpath=//button[span[normalize-space()='确定'] or normalize-space()='确定']"
    locator_btn_update_base_info = "xpath=//button[span[normalize-space()='更新基本信息'] or normalize-space()='更新基本信息']"

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

    @allure.step("上传头像：{file_path}")
    def upload_avatar(self, file_path):
        # 先点击头像 figure 触发上传组件挂载隐藏 input[type=file]（已验证不触发原生文件选择器，
        self.click(self.locator_avatar_figure)
        self.upload_file(self.locator_input_avatar_upload, file_path)
        return self

    @allure.step("点击【确定】")
    def click_confirm(self):
        self.click(self.locator_btn_confirm)
        return self

    @allure.step("点击【更新基本信息】")
    def click_update_base_info(self):
        self.click(self.locator_btn_update_base_info)
        return self

    # --------------------- 流程 -------------------------------------
    @allure.step("我的账号-更新基本信息流程")
    def my_account_update_flow(self, case):
        """
        我的账号编辑流程：输入真实姓名 -> 输入手机号-> 输入邮箱 -> 上传头像 -> 确定 -> 更新基本信息。
        """
        (self
         .input_real_name(case.get("real_name", "超级管理员 1 2"))
         .input_phone(case.get("phone", "187284416455"))
         .input_email(case.get("email", "workspace@163.com"))
         .upload_avatar(case.get("avatar_path", "1.jpeg"))
         .click_confirm()
         .click_update_base_info())
        return self
