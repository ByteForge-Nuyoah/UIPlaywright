import re
from playwright.sync_api import Page, expect


def test_example(page: Page) -> None:
    page.goto("https://app.test.surgsmart.com/login?from=/work-station")
    page.get_by_text("密码登录").click()
    page.locator("input[type=\"text\"]").click()
    page.locator("input[type=\"text\"]").fill("${admin_user_name}")
    page.locator("input[type=\"password\"]").click()
    page.locator("input[type=\"password\"]").fill("${admin_user_password}")
    page.get_by_role("checkbox").click()
    page.get_by_role("button", name="登录", exact=True).click()
    page.get_by_text("拖动滑块完成验证").click()
