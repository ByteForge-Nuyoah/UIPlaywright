# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_login_api.py
# @Software: PyCharm
# @Desc    : CRM 登录接口用例

import os
import pytest
from playwright.sync_api import Playwright
from config.global_vars import GLOBAL_VARS
from utils.base_utils.request_control import RequestControl

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTERFACE_DIR = os.path.join(PROJECT_DIR, "interfaces")


@pytest.mark.api
class TestLoginApi:
    """CRM 登录接口"""

    def test_crm_login_api(self, playwright: Playwright):
        """
        验证 crm_login.yml 可被 RequestControl 正常加载执行，
        并确认 headers.Origin 中的 ${url} 已按当前环境替换。
        """
        api_request_context = playwright.request.new_context(base_url=GLOBAL_VARS["host"])
        try:
            result = RequestControl(api_request_context=api_request_context).api_request_flow(
                api_file_path=os.path.join(INTERFACE_DIR, "crm_login.yml"),
                key="crm_login",
                global_var={
                    "url": GLOBAL_VARS["url"],
                    "username": GLOBAL_VARS["admin_user_name"],
                    "password": GLOBAL_VARS["admin_user_password"],
                    "appPlatform": "work-space",
                    "appVersion": "1.0.1",
                },
            )
            assert result["headers"]["Origin"] == GLOBAL_VARS["url"]
        finally:
            api_request_context.dispose()
