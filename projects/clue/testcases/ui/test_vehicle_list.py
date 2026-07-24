# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_vehicle_list.py
# @Software: PyCharm
# @Desc    : 车辆管理/车辆列表用例

import os
import pytest
from loguru import logger
from pages.common_page import CommonPage
from pages.vehicle_list_page import VehicleListPage
from playwright.sync_api import Page
from config.global_vars import GLOBAL_VARS
from utils.files_utils.yaml_handle import YamlHandle


@pytest.mark.vehicle
class TestVehicleList:
    """车辆管理/车辆列表"""

    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "vehicle_list.yaml")
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        """
        page fixture 已通过项目级 conftest 注入 storage_state（默认携带登录态）。
        打开首页后，由 CommonPage 经左侧菜单导航到车辆列表页面。
        """
        logger.info("\n\n---------------Start: 车辆列表测试-------------")
        page.goto(GLOBAL_VARS["url"])
        # 持有 CommonPage：左侧菜单等跨页布局与导航的统一入口
        self.common_page = CommonPage(page)
        yield

    @pytest.mark.parametrize("case", cases["vehicle_filter_export_page"], ids=lambda x: x["title"])
    def test_vehicle_list_filter_and_export(self, case):
        """车辆列表：设备号查询、重置、关联状态筛选、导出脱敏/敏感数据。"""
        # 操作步骤：经左侧菜单进入车辆列表页 → 按设备号筛选 → 导出脱敏数据与敏感数据
        desensitized_download, sensitive_download = (
            self.common_page
            .goto(VehicleListPage, CommonPage.locator_menu_vehicle_management, CommonPage.locator_link_vehicle_list)
            .vehicle_list_filter_export_flow(device_no=case["device_no"])
        )

        # 断言：导出文件已生成且落盘（文件名非空 + 文件存在 + 大小 > 0）
        for download, desc in ((desensitized_download, "脱敏"), (sensitive_download, "敏感")):
            assert download.suggested_filename, f"{desc}数据导出文件名不应为空"
            path = download.path()
            assert path and os.path.exists(path) and os.path.getsize(path) > 0, \
                f"{desc}数据导出文件未落盘或为空: {path}"
