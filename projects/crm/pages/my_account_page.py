# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : my_account_page.py
# @Software: PyCharm
# @Desc    : CRM 我的账号页（个人基本信息编辑）

import allure
from utils.base_utils.base_page import BasePage


class MyAccountPage(BasePage):
    """
    CRM 我的账号页：编辑真实姓名/手机号/邮箱/头像、解除绑定微信、更新基本信息。
    定位器由 Playwright codegen 录制转换（get_by_role textbox -> xpath label-following-input，
    button -> xpath button，get_by_text -> text=），与 po_style_converter 产出保持一致。
    """

    # 表单输入框：ant-design Form 的 label 文本定位
    locator_input_real_name = "xpath=//label[contains(normalize-space(), '真实姓名')]//following::input[1]"
    # 录制为 get_by_role("textbox", name="手机号", exact=True)，转换器未识别 exact=True，手工补
    locator_input_phone = "xpath=//label[contains(normalize-space(), '手机号')]//following::input[1]"
    locator_input_email = "xpath=//label[contains(normalize-space(), '邮箱')]//following::input[1]"
    # 头像上传：ant-design Upload 的隐藏 input[type=file]，set_input_files 直接作用其上
    # （录制把 set_input_files 挂在 button「点击上传头像 重新上传」上，运行时会报
    #   "Node is not an HTMLInputElement"，故改挂到隐藏 input）
    locator_input_avatar_upload = "xpath=(//input[@type='file'])[1]"
    # 头像裁剪/确认弹窗的「确定」按钮
    locator_btn_confirm = "xpath=//button[span[normalize-space()='确定'] or normalize-space()='确定']"
    locator_text_unbind_wechat = "text=解除绑定微信"
    locator_btn_update_base_info = "xpath=//button[span[normalize-space()='更新基本信息'] or normalize-space()='更新基本信息']"
    # 「我的账号」入口（登录后首页，录制未覆盖导航段），需按真实 DOM 校验
    locator_entry_my_account = "xpath=//div[normalize-space()='我的账号']"

    @allure.step("输入真实姓名：{real_name}")
    def input_real_name(self, real_name):
        self.input(self.locator_input_real_name, real_name)
        return self

    @allure.step("点击手机号输入框")
    def click_phone(self):
        # 录制中仅 click 未 fill：手机号为预填/只读，点击聚焦即可
        self.click(self.locator_input_phone)
        return self

    @allure.step("输入邮箱：{email}")
    def input_email(self, email):
        self.input(self.locator_input_email, email)
        return self

    @allure.step("上传头像：{file_path}")
    def upload_avatar(self, file_path):
        # 直接对隐藏 input[type=file] 设置文件，无需触发 figure/label 点击；
        # 录制中 figure.avatar / label「点击上传头像」的点击为触发系统文件选择器的试错操作，
        # set_input_files 本身已绕过文件选择器直接落文件，故省略。
        self.upload_file(self.locator_input_avatar_upload, file_path)
        return self

    @allure.step("点击【确定】")
    def click_confirm(self):
        self.click(self.locator_btn_confirm)
        return self

    @allure.step("点击【解除绑定微信】")
    def click_unbind_wechat(self):
        self.click(self.locator_text_unbind_wechat)
        return self

    @allure.step("点击【更新基本信息】")
    def click_update_base_info(self):
        self.click(self.locator_btn_update_base_info)
        return self

    @allure.step("点击进入【我的账号】")
    def navigate(self):
        """从登录后首页点击「我的账号」入口进入编辑页（录制未覆盖导航段，定位器需按真实 DOM 校验）。"""
        self.click(self.locator_entry_my_account)
        return self

    # --------------------- 流程 -------------------------------------
    @allure.step("我的账号-更新基本信息流程")
    def my_account_update_flow(self, case):
        """
        还原 codegen 录制的我的账号编辑流程：输入真实姓名 -> 点击手机号
        -> 输入邮箱 -> 上传头像 -> 确定 -> 解除绑定微信 -> 更新基本信息。

        录制中的试错冗余已合并省略：
        - 邮箱：3 次 click + 4 次 press ArrowRight + press Enter + 重复 fill，
          最终值即 fill 内容，单次 input 即可；
        - 头像：figure.avatar / label「点击上传头像」的点击省略，直接 set_input_files。
        """
        (self
         .input_real_name(case.get("real_name", "超级管理员 1"))
         .click_phone()
         .input_email(case.get("email", "workspace@qq.com"))
         .upload_avatar(case.get("avatar_path", "1.jpeg"))
         .click_confirm()
         .click_unbind_wechat()
         .click_update_base_info())
        return self
