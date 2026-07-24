import os

# ------------------------------------ 测试数据配置 ----------------------------------------------------#
ENV_VARS = {
    "common": {
        "report_title": "UI自动化测试报告-Clue",
        "project_name": "clueSystem",
        "tester": "会飞的🐟",
        "department": "成都研发后台",
        "env": "test",
        # API 登录接口配置（供 testcases/conftest.py 的 api_session_setup 使用）；
        # file 相对项目根 interfaces/ 目录，var_map 把 GLOBAL_VARS 字段映射成接口 payload 变量名
        "login_api": {
            "file": "clue_login.txt",
            "key": "clue_login",
            "var_map": {
                "user_name": "admin_user_name",
                "password": "admin_user_password",
            },
            "extra_vars": {},
        },
    },
    "test": {
        # 测试环境前端域名
        "url": "https://clue-dev.spreadwin.cn",
        # 测试环境接口域名
        "host": "https://clueapi-dev.spreadwin.cn",
        # 超级管理员（必须通过环境变量或本地 .env 注入，避免代码中保留默认明文账号密码）
        "admin_user_name": os.getenv("CLUE_ADMIN_USER", ""),
        "admin_user_password": os.getenv("CLUE_ADMIN_PASSWORD", ""),
        "login_type": "PASSWD",
        "uuid": "",
        "sms_state": "LOGIN"
    },
    "prod": {
        # 生产环境前端域名
        "url": "https://clue.spreadwin.cn",
        # 生产环境接口域名
        "host": "https://clueapi.spreadwin.cn",
        # 超级管理员
        "admin_user_name": os.getenv("CLUE_ADMIN_USER", ""),
        "admin_user_password": os.getenv("CLUE_ADMIN_PASSWORD", ""),
        # 以下字段与 test 对齐，供 API 登录等用例在 prod 下取值
        "login_type": "PASSWD",
        "uuid": "",
        "sms_state": "LOGIN"
    }
}
