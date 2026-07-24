# 登录
page.goto("https://workspace-dev.spreadwin.cn/login")
    page.get_by_role("textbox", name="账号").click()
    page.get_by_role("textbox", name="账号").fill("admin")
    page.get_by_role("textbox", name="密码").click()
    page.get_by_role("textbox", name="密码").fill("123123")
    page.get_by_role("button", name="登录").click()