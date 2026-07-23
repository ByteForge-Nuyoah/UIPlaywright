# -*- coding: utf-8 -*-
# Playwright codegen 录制：CRM 我的账号-更新基本信息
#
# 本文件为完整 codegen 测试文件，有两种用途：
#   1. run.py -recording raw   直接作为 pytest 用例运行（def test_x(page) 由 pytest-playwright 注入 page）
#   2. python utils/tools/convert_recordings.py --project crm  转换为 POM 三件套
#
# 注意：本录制为「已在编辑页」的片段（未含 page.goto 导航）。raw 模式直接跑前需先导航到该页，
# 否则首个定位会超时失败。转换产物 pages/my_account_page.py 已手工补全（手机号 exact、头像
# set_input_files 改挂隐藏 input），故再次转换会被「默认跳过」保护，不会覆盖手工修复。

from playwright.sync_api import Page


def test_my_account(page: Page):
    page.get_by_role("textbox", name="真实姓名").click()
    page.get_by_role("textbox", name="真实姓名").fill("超级管理员 1")
    page.get_by_role("textbox", name="手机号", exact=True).click()
    page.get_by_role("textbox", name="邮箱").click()
    page.get_by_role("textbox", name="邮箱").click()
    page.get_by_role("textbox", name="邮箱").click()
    page.get_by_role("textbox", name="邮箱").press("ArrowRight")
    page.get_by_role("textbox", name="邮箱").press("ArrowRight")
    page.get_by_role("textbox", name="邮箱").press("ArrowRight")
    page.get_by_role("textbox", name="邮箱").press("ArrowRight")
    page.get_by_role("textbox", name="邮箱").fill("workspace@qq.com")
    page.get_by_role("textbox", name="邮箱").press("Enter")
    page.get_by_role("textbox", name="邮箱").fill("workspace@qq.com")
    page.locator("figure > .avatar").click()
    page.locator("label").filter(has_text="点击上传头像").click()
    page.get_by_role("button", name="点击上传头像 重新上传").set_input_files("1.jpeg")
    page.get_by_role("button", name="确定").click()
    page.get_by_text("解除绑定微信").click()
    page.get_by_role("button", name="更新基本信息").click()
