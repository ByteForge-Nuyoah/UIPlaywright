# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : project_settings.py
# @Software: PyCharm
# @Desc    : CRM 项目配置

import os

# ------------------------------------ 测试数据配置 ----------------------------------------------------#
ENV_VARS = {
    "common": {
        "report_title": "UI自动化测试报告-CRM",
        "project_name": "crmSystem",
        "tester": "会飞的🐟",
        "department": "成都研发后台",
        "env": "test",
        # API 登录接口配置（供 testcases/conftest.py 的 api_session_setup 使用）；
        # file 相对项目根 interfaces/ 目录，var_map 把 GLOBAL_VARS 字段映射成接口 payload 变量名
        "login_api": {
            "file": "crm_login.yml",
            "key": "crm_login",
            "var_map": {
                "username": "admin_user_name",
                "password": "admin_user_password",
            },
            "extra_vars": {
                "appPlatform": "work-space",
                "appVersion": "1.0.1",
            },
        },
    },
    "test": {
        # 测试环境前端域名
        "url": "https://workspace-dev.spreadwin.cn",
        # 测试环境接口域名
        "host": "https://crmapi-dev.spreadwin.cn",
        # 管理员账号（必须通过环境变量或本地 .env 注入，避免代码中保留默认明文账号密码）
        "admin_user_name": os.getenv("CRM_ADMIN_USER", ""),
        "admin_user_password": os.getenv("CRM_ADMIN_PASSWORD", ""),
    },
    "prod": {
        # TODO: 待补 prod 环境域名
        "url": "https://workspace.spreadwin.cn",
        "host": "https://crmapi.spreadwin.cn",
        "admin_user_name": os.getenv("CRM_ADMIN_USER", ""),
        "admin_user_password": os.getenv("CRM_ADMIN_PASSWORD", ""),
    },
}
