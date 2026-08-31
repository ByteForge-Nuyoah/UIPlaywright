import os

import pytest
from loguru import logger
from playwright.sync_api import Page

from pages.common_page import CommonPage
from utils.files_utils.yaml_handle import YamlHandle


@pytest.mark.navigation
@pytest.mark.recordings
class TestAuthenticatedNavigation:
    """SurgSmart 登录后侧栏导航录制流程"""

    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
        "authenticated_navigation.yaml",
    )
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        logger.info("\n\n---------------Start: SurgSmart 登录后导航测试-------------")
        self.common_page = CommonPage(page).navigate_to_work_station()
        yield

    @pytest.mark.parametrize("case", cases["navigation_cases"], ids=lambda case: case["title"])
    def test_sidebar_navigation_opens_expected_page(self, case):
        self.common_page.authenticated_navigation_flow(case)
