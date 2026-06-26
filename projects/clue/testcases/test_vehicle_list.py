# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_vehicle_list.py
# @Software: PyCharm
# @Desc    : 车辆管理/车辆列表用例

import os
import pytest
from loguru import logger
from pages.home_page import HomePage
from playwright.sync_api import Page
from config.global_vars import GLOBAL_VARS
from utils.files_utils.yaml_handle import YamlHandle


@pytest.mark.vehicle
@pytest.mark.recordings
class TestVehicleList:
    """车辆管理/车辆列表"""

    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "vehicle_list.yaml")
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        """
        page fixture 已通过项目级 conftest 注入 storage_state（默认携带登录态）。
        入口统一通过 HomePage 派发到车辆列表页面。
        """
        logger.info("\n\n---------------Start: 车辆列表测试-------------")
        page.goto(GLOBAL_VARS["url"])
        self.home_page = HomePage(page)
        yield

    @pytest.mark.parametrize("case", cases["vehicle_list_cases"], ids=lambda x: x["title"])
    def test_vehicle_list_filter_and_export(self, case):
        """
        车辆列表：设备号查询、重置、关联状态筛选、导出脱敏/敏感数据。
        """
        desensitized_download, sensitive_download = (
            self.home_page
            .goto_vehicle_list()
            .vehicle_list_filter_export_flow(device_no=case["device_no"])
        )

        assert desensitized_download.suggested_filename
        assert sensitive_download.suggested_filename
