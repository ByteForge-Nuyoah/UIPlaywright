# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc    : 项目级 fixture：UI 预登录 + storage_state 注入

import os
import json
import time
import base64
import pytest
import traceback
from loguru import logger
from playwright.sync_api import Browser
from config.global_vars import GLOBAL_VARS
from config.settings import resolve_window_size
from config.config_path import AUTH_DIR, BASE_DIR
from utils.base_utils.request_control import RequestControl
from pages.login_page import LoginPage

PROJECT_NAME = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUTH_STATE_PATH = os.path.join(AUTH_DIR, f"{PROJECT_NAME}_state.json")
INTERFACE_DIR = os.path.join(BASE_DIR, "interfaces")
STORAGE_STATE_TTL = 3600


def pytest_configure(config):
    """注册 clue 项目专属 markers（从 root pytest.ini 下沉，支持多项目隔离）。"""
    for marker in [
        "login: login cases",
        "account: account related cases",
        "data: data page interaction cases",
        "vehicle: vehicle management/list cases",
        "export: export page cases",
        "api: api interface cases",
        "recordings: playwright recorded cases converted to POM",
    ]:
        config.addinivalue_line("markers", marker)


def _jwt_exp(token):
    """
    解码 JWT token 的 payload，返回 exp（过期时间戳）；非 JWT 或无 exp 返回 None。
    仅解码不验签（用于本地过期判断，非安全校验）。
    """
    if not isinstance(token, str):
        return None
    parts = token.split(".")
    if len(parts) != 3:
        return None
    try:
        payload = parts[1] + "=" * (-len(parts[1]) % 4)  # base64 padding
        data = json.loads(base64.urlsafe_b64decode(payload))
        exp = data.get("exp")
        return int(exp) if exp is not None else None
    except Exception:
        return None


def is_storage_state_valid(state_path, ttl=STORAGE_STATE_TTL):
    """
    检查 storage_state 文件是否仍有效（可复用）。
    优先解码 localStorage 中 JWT token 的 exp；无 JWT 则用文件 mtime + ttl 兜底。
    :return: True 有效可复用 / False 需重新登录
    """
    if not os.path.exists(state_path):
        return False
    # 1. 优先：从 localStorage 找 JWT token 的 exp
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
        for origin in state.get("origins", []):
            for item in origin.get("localStorage", []):
                exp = _jwt_exp(item.get("value"))
                if exp is not None:
                    valid = time.time() < exp
                    logger.debug(f"storage_state JWT exp={exp}, 当前={int(time.time())}, 有效={valid}")
                    return valid
    except Exception as e:
        logger.debug(f"解析 storage_state JWT 失败，退化到 mtime 兜底：{e}")
    # 2. 兜底：文件 mtime + ttl
    try:
        mtime = os.path.getmtime(state_path)
        valid = time.time() - mtime < ttl
        logger.debug(f"storage_state mtime 兜底, ttl={ttl}, 有效={valid}")
        return valid
    except Exception:
        return False


def login_and_save_state(page, login, password, state_path):
    """
    在给定 page 上执行 UI 登录并保存 storage_state。
    复用 LoginPage，消除 conftest 内联登录代码重复。
    """
    login_page = LoginPage(page)
    login_page.navigate(timeout=30000)
    login_page.login_on_page_flow(login=login, password=password)
    # 等到 URL 离开登录页（token 已被前端写进 localStorage）
    page.wait_for_url(lambda url: "/user/login" not in url, timeout=15000)
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    page.context.storage_state(path=state_path)
    logger.success(f"登录态已保存至: {state_path}")


def _opts_out_of_storage_state(item) -> bool:
    """用例是否通过 `@pytest.mark.browser_context_args(storage_state=None)` 主动放弃预登录态。"""
    sentinel = object()
    for mark in item.iter_markers("browser_context_args"):
        if mark.kwargs.get("storage_state", sentinel) is None:
            return True
    return False


def _session_needs_storage_state(session) -> bool:
    """Session 中有任一用例没有显式放弃 storage_state 时，需要预登录。"""
    return any(not _opts_out_of_storage_state(item) for item in session.items)


@pytest.fixture(scope="session")
def storage_state_path(request, browser: Browser):
    """
    会话级前置：在一个独立的浏览器 context 里跑一次完整 UI 登录，
    把登录态以 storage_state（cookies + localStorage）形式落盘到 .auth/<project>_state.json，
    返回该路径供 `browser_context_args` 注入。
    """
    # 按需触发：检测 session 中是否还有用例需要预登录的 storage_state
    if not _session_needs_storage_state(request.session):
        logger.info("Session 中所有用例均已显式 storage_state=None，跳过预登录")
        return None

    # 提前检测管理员账号密码是否注入，避免空凭据登录导致 15s 超时与下游用例混乱失败
    if not GLOBAL_VARS.get("admin_user_name") or not GLOBAL_VARS.get("admin_user_password"):
        raise RuntimeError(
            "CLUE_ADMIN_USER / CLUE_ADMIN_PASSWORD 未配置，请通过本地 .env 或 CI Secret 注入"
            "（参考 config/env/.env.example）"
        )

    # 复用未过期的登录态，避免每次会话都重新 UI 登录
    if is_storage_state_valid(AUTH_STATE_PATH):
        logger.info(f"复用未过期的登录态：{AUTH_STATE_PATH}，跳过 UI 预登录")
        return AUTH_STATE_PATH

    logger.info("\n-------------- Start: 预登录以获取 storage_state ----------------")
    context = browser.new_context(
        base_url=GLOBAL_VARS["url"],
        viewport=resolve_window_size(),
    )
    page = context.new_page()
    try:
        login_and_save_state(
            page=page,
            login=GLOBAL_VARS["admin_user_name"],
            password=str(GLOBAL_VARS["admin_user_password"]),
            state_path=AUTH_STATE_PATH,
        )
        return AUTH_STATE_PATH
    except Exception as e:
        logger.error(f"UI 预登录失败：{e}")
        logger.error(traceback.format_exc())
        pytest.fail(f"UI 预登录失败，跳过所有业务用例：{e}")
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


@pytest.fixture(scope="function")
def admin_page(new_context):
    """
    管理员用户的独立浏览器上下文（function 级）。

    与 session 级 storage_state_path 隔离：使用独立的 .auth/clue_admin_state.json，
    适合需要 admin 在独立 context 中操作、且不影响 session 共享态的用例。
    未过期复用，过期或不存在则重新 UI 登录。
    """
    state_path = os.path.join(AUTH_DIR, f"{PROJECT_NAME}_admin_state.json")
    if is_storage_state_valid(state_path):
        logger.info(f"admin_page 复用未过期登录态：{state_path}")
        context = new_context(storage_state=state_path)
    else:
        logger.info("admin_page 登录态缺失或过期，重新 UI 登录")
        # storage_state=None 显式覆盖 session 级 browser_context_args 注入的登录态
        context = new_context(storage_state=None)
        page = context.new_page()
        login_and_save_state(
            page=page,
            login=GLOBAL_VARS["admin_user_name"],
            password=str(GLOBAL_VARS["admin_user_password"]),
            state_path=state_path,
        )
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="function")
def user_page(new_context):
    """
    普通用户 page fixture（预留）。

    从 GLOBAL_VARS 读取 user_name / user_password；未配置则 skip。
    未来新增普通用户时，在 project_settings.py 的 ENV_VARS 里加：
        "user_name": os.getenv("CLUE_USER", ""),
        "user_password": os.getenv("CLUE_USER_PASSWORD", ""),
    即可使用本 fixture。
    """
    user_name = GLOBAL_VARS.get("user_name")
    user_password = GLOBAL_VARS.get("user_password")
    if not user_name or not user_password:
        pytest.skip("未配置普通用户凭据（user_name / user_password），跳过")
    state_path = os.path.join(AUTH_DIR, f"{PROJECT_NAME}_user_state.json")
    if is_storage_state_valid(state_path):
        context = new_context(storage_state=state_path)
    else:
        context = new_context(storage_state=None)
        page = context.new_page()
        login_and_save_state(
            page=page,
            login=user_name,
            password=str(user_password),
            state_path=state_path,
        )
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="session")
def api_session_setup(browser: Browser):
    """
    会话级 API 数据准备 fixture。
    :return: API 登录的响应数据（dict）；失败/跳过返回 None
    """
    result = None
    api_browser_context = None

    login_api_cfg = GLOBAL_VARS.get("login_api")

    if not GLOBAL_VARS.get("admin_user_name") or not GLOBAL_VARS.get("admin_user_password"):
        logger.warning("未配置 admin 凭据，跳过 API 会话准备")
    elif not login_api_cfg:
        logger.info("未配置 login_api，跳过 API 会话准备")
    else:
        login_api = os.path.join(INTERFACE_DIR, login_api_cfg["file"])
        if not os.path.exists(login_api):
            logger.warning(f"接口定义不存在：{login_api}，跳过 API 会话准备")
        else:
            # 以 GLOBAL_VARS 为基础，按 var_map 把凭据等字段映射成接口 payload 变量名，再补 extra_vars
            global_var = {**GLOBAL_VARS}
            for payload_key, source_key in login_api_cfg.get("var_map", {}).items():
                global_var[payload_key] = GLOBAL_VARS.get(source_key, "")
            global_var.update(login_api_cfg.get("extra_vars", {}))
            api_browser_context = browser.new_context(
                base_url=GLOBAL_VARS.get("host")
            )
            try:
                result = RequestControl(
                    api_request_context=api_browser_context.request
                ).api_request_flow(
                    api_file_path=login_api,
                    key=login_api_cfg["key"],
                    global_var=global_var,
                )
                logger.success("API 会话准备完成（API 登录成功）")
            except Exception as e:
                logger.warning(f"API 会话准备失败，不影响 UI 用例：{e}")
    try:
        yield result
    finally:
        if api_browser_context is not None:
            api_browser_context.close()
