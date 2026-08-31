from urllib.parse import urlparse

import allure
from playwright.sync_api import expect

from config.global_vars import GLOBAL_VARS
from utils.base_utils.base_page import BasePage


class WorkStationPage(BasePage):
    summary_labels = ("手术数量", "手术时长", "术式种类", "病历数量", "已使用存储")
    recent_surgery_columns = (
        "术式名称",
        "主刀医生",
        "科室",
        "上传状态",
        "AI分析",
        "手术日期",
        "操作",
    )

    @allure.step("访问 SurgSmart 工作台")
    def navigate(self, timeout: int = 30000):
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

    @allure.step("校验工作台摘要与核心区域")
    def assert_summary_is_visible(self, timeout: int = 10000):
        for label in self.summary_labels:
            expect(self.page.get_by_text(label, exact=True).first).to_be_visible(
                timeout=timeout
            )
        expect(
            self.page.get_by_text("手术数量与时长统计", exact=True)
        ).to_be_visible(timeout=timeout)
        expect(self.page.get_by_text("近期手术", exact=True)).to_be_visible(
            timeout=timeout
        )
        return self

    @allure.step("校验近期手术表格列")
    def assert_recent_surgery_table_columns(self, timeout: int = 10000):
        table = self.page.get_by_role("table")
        expect(table).to_be_visible(timeout=timeout)
        for column in self.recent_surgery_columns:
            expect(
                table.get_by_role("columnheader", name=column, exact=True)
            ).to_be_visible(timeout=timeout)
        return self

    @allure.step("校验手术统计日期范围")
    def assert_statistics_date_range_is_available(self, timeout: int = 10000):
        start_date = self.page.get_by_placeholder("开始日期", exact=True)
        end_date = self.page.get_by_placeholder("结束日期", exact=True)
        expect(start_date).to_be_visible(timeout=timeout)
        expect(end_date).to_be_visible(timeout=timeout)
        assert start_date.input_value(), "工作台统计开始日期不应为空"
        assert end_date.input_value(), "工作台统计结束日期不应为空"
        return self

    @allure.step("SurgSmart 工作台页面校验")
    def work_station_assertion_flow(self, case):
        assertions = {
            "summary": self.assert_summary_is_visible,
            "recent_surgery_table": self.assert_recent_surgery_table_columns,
            "statistics_date_range": self.assert_statistics_date_range_is_available,
        }
        assertion_name = case.get("assertion")
        if assertion_name not in assertions:
            raise ValueError(f"不支持的工作台校验类型：{assertion_name}")
        return assertions[assertion_name]()
