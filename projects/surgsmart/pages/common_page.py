from urllib.parse import urlparse

import allure
from playwright.sync_api import expect

from config.global_vars import GLOBAL_VARS
from utils.base_utils.base_page import BasePage


class CommonPage(BasePage):
    @allure.step("访问 SurgSmart 工作台")
    def navigate_to_work_station(self, timeout: int = 30000):
        self.page.goto(
            GLOBAL_VARS["url"] + "/work-station",
            timeout=timeout,
            wait_until="domcontentloaded",
        )
        self.page.wait_for_url(
            lambda url: urlparse(url).path.rstrip("/") == "/work-station",
            timeout=timeout,
        )
        expect(self.page.get_by_role("heading", name="工作台", exact=True)).to_be_visible()
        return self

    @allure.step("从侧栏进入：{heading}")
    def open_section(self, path: str, heading: str, timeout: int = 10000):
        link = self.page.locator(f'a[href="{path}"]').first
        expect(link).to_be_visible(timeout=timeout)
        link.click()
        self.page.wait_for_url(
            lambda url: urlparse(url).path.rstrip("/") == path,
            timeout=timeout,
        )
        expect(
            self.page.get_by_role("heading", name=heading, exact=True)
        ).to_be_visible(timeout=timeout)
        return self

    @allure.step("SurgSmart 登录后侧栏导航")
    def authenticated_navigation_flow(self, case):
        return self.open_section(case["path"], case["heading"])
