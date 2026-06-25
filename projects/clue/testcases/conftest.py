# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : conftest.py
# @Software: PyCharm
# @Desc    : 项目级 fixture：UI 预登录 + storage_state 注入

import os
import traceback

import pytest
from loguru import logger
from playwright.sync_api import Browser

from config.global_vars import GLOBAL_VARS
from config.path_config import AUTH_DIR

AUTH_STATE_PATH = os.path.join(AUTH_DIR, "clue_state.json")


@pytest.fixture(scope="session")
def storage_state_path(browser: Browser):
    """
    会话级前置：在一个独立的浏览器 context 里跑一次完整 UI 登录，
    把登录态以 storage_state（cookies + localStorage）形式落盘到 .auth/clue_state.json，
    返回该路径供 `browser_context_args` 注入。

    为什么走 UI 而不是 API：
    本项目鉴权是 token-in-body，前端 JS 在登录成功回调里把 token 写进 localStorage。
    纯 API 登录拿不到这份 localStorage，下游用例会被认为未登录。
    走一次 UI 登录由前端自己完成 token 落盘，最稳妥。

    设计要点：
    1. 整个会话只执行一次，所有用例共享生成的 storage_state 文件。
    2. 创建独立 context，不复用 `browser_context_args`，避免循环依赖
       （browser_context_args 反过来要依赖本 fixture）。
    3. 失败时返回 None，浏览器以未登录态启动，让具体业务断言报真实错误。
    """
    logger.info("\n-------------- Start: 预登录以获取 storage_state ----------------")
    context = browser.new_context(
        base_url=GLOBAL_VARS["url"],
        viewport={"width": 1920, "height": 1080},
    )
    page = context.new_page()
    try:
        page.goto("/user/login", timeout=30000)
        page.wait_for_load_state("domcontentloaded")

        page.fill("id=user_name", GLOBAL_VARS["admin_user_name"])
        page.fill("id=password", str(GLOBAL_VARS["admin_user_password"]))
        page.click("xpath=//*[@id='root']/div/div/form/button")

        # 等到 URL 离开登录页（说明 token 已被前端写进 localStorage）
        page.wait_for_url(lambda url: "/user/login" not in url, timeout=15000)

        os.makedirs(os.path.dirname(AUTH_STATE_PATH), exist_ok=True)
        context.storage_state(path=AUTH_STATE_PATH)
        logger.success(f"登录态已保存至: {AUTH_STATE_PATH}")
        return AUTH_STATE_PATH
    except Exception as e:
        logger.error(f"UI 预登录失败，浏览器将以未登录态运行：{e}")
        logger.error(traceback.format_exc())
        return None
    finally:
        context.close()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, storage_state_path):
    """
    项目级覆写 pytest-playwright 的 browser_context_args fixture：
    在父级配置（root conftest 的 viewport / record_video_size 等）基础上注入 storage_state，
    使本项目下所有用例的 `page` fixture 默认携带登录态。

    单测如需未登录上下文（例如登录用例本身），可在用例 / 类上加：
        @pytest.mark.browser_context_args(storage_state=None)
    pytest-playwright 会用该 marker 的 kwargs 覆盖 session 级配置。
    """
    extra = {}
    if storage_state_path:
        extra["storage_state"] = storage_state_path
    return {**browser_context_args, **extra}
