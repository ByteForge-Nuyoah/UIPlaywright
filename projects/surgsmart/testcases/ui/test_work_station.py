import os

import pytest
from loguru import logger
from playwright.sync_api import Page

from pages.work_station_page import WorkStationPage
from utils.files_utils.yaml_handle import YamlHandle


@pytest.mark.work_station
@pytest.mark.recordings
class TestWorkStation:
    """SurgSmart 工作台录制流程"""

    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
        "work_station.yaml",
    )
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        logger.info("\n\n---------------Start: SurgSmart 工作台测试-------------")
        self.work_station_page = WorkStationPage(page).navigate()
        yield

    @pytest.mark.parametrize("case", cases["work_station_cases"], ids=lambda case: case["title"])
    def test_work_station_page(self, case):
        self.work_station_page.work_station_assertion_flow(case)
