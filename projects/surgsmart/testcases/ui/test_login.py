import os

import pytest
from loguru import logger
from playwright.sync_api import Page

from pages.login_page import LoginPage
from utils.files_utils.yaml_handle import YamlHandle


@pytest.mark.login
@pytest.mark.recordings
@pytest.mark.browser_context_args(storage_state=None)
class TestLogin:
    """SurgSmart 密码登录录制流程"""

    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
        "login.yaml",
    )
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        logger.info("\n\n---------------Start: SurgSmart 登录测试-------------")
        self.login_page = LoginPage(page)
        self.login_page.prepare_deterministic_captcha().navigate()
        yield
        page.context.clear_cookies()

    @pytest.mark.parametrize("case", cases["login_cases"], ids=lambda case: case["title"])
    def test_password_login_with_slider_captcha(self, case):
        if not case.get("login") or not case.get("password"):
            pytest.skip("SURGSMART_USER / SURGSMART_PASSWORD 未配置")

        self.login_page.login_with_slider_captcha_flow(case)
