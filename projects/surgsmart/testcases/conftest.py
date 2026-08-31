import base64
import json
import os
import time
from urllib.parse import urlparse
import pytest
from loguru import logger
from playwright.sync_api import Browser
from config.config_path import AUTH_DIR
from config.global_vars import GLOBAL_VARS
from config.settings import resolve_window_size
from pages.login_page import LoginPage

AUTH_STATE_PATH = os.path.join(AUTH_DIR, "surgsmart_state.json")
STORAGE_STATE_TTL = 3600

def pytest_configure(config):
    for marker in (
        "login: SurgSmart login cases",
        "work_station: SurgSmart work station cases",
        "navigation: SurgSmart authenticated navigation cases",
        "recordings: converted Playwright recordings",
    ):
        config.addinivalue_line("markers", marker)


def _jwt_exp(token):
    if not isinstance(token, str):
        return None
    parts = token.split(".")
    if len(parts) != 3:
        return None
    try:
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        exp = json.loads(base64.urlsafe_b64decode(payload)).get("exp")
        return int(exp) if exp is not None else None
    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def _storage_state_is_valid(state_path, ttl=STORAGE_STATE_TTL):
    if not os.path.exists(state_path):
        return False
    try:
        with open(state_path, "r", encoding="utf-8") as state_file:
            state = json.load(state_file)
        if not state.get("cookies") and not state.get("origins"):
            return False
        for origin in state.get("origins", []):
            for item in origin.get("localStorage", []):
                exp = _jwt_exp(item.get("value"))
                if exp is not None:
                    return time.time() < exp
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        pass
    return time.time() - os.path.getmtime(state_path) < ttl


def _opts_out_of_storage_state(item):
    sentinel = object()
    return any(
        marker.kwargs.get("storage_state", sentinel) is None
        for marker in item.iter_markers("browser_context_args")
    )


@pytest.fixture(scope="session")
def storage_state_path(request, browser: Browser):
    if all(_opts_out_of_storage_state(item) for item in request.session.items):
        return None
    if not GLOBAL_VARS.get("admin_user_name") or not GLOBAL_VARS.get("admin_user_password"):
        pytest.skip("SURGSMART_USER / SURGSMART_PASSWORD 未配置")
    if _storage_state_is_valid(AUTH_STATE_PATH):
        logger.info(f"复用 SurgSmart 登录态：{AUTH_STATE_PATH}")
        return AUTH_STATE_PATH

    logger.info("创建 SurgSmart 登录态")
    context = browser.new_context(
        base_url=GLOBAL_VARS["url"],
        viewport=resolve_window_size(),
        locale="zh-CN",
    )
    page = context.new_page()
    try:
        login_case = {
            "login": GLOBAL_VARS["admin_user_name"],
            "password": str(GLOBAL_VARS["admin_user_password"]),
            "captcha_distance": 167.4,
        }
        (
            LoginPage(page)
            .prepare_deterministic_captcha()
            .navigate()
            .login_with_slider_captcha_flow(login_case)
        )
        page.wait_for_url(
            lambda url: urlparse(url).path.rstrip("/") == "/work-station",
            timeout=15000,
        )
        os.makedirs(os.path.dirname(AUTH_STATE_PATH), exist_ok=True)
        page.context.storage_state(path=AUTH_STATE_PATH)
        return AUTH_STATE_PATH
    finally:
        context.close()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, storage_state_path):
    context_args = {**browser_context_args, "locale": "zh-CN"}
    if storage_state_path is None:
        return context_args
    return {**context_args, "storage_state": storage_state_path}
