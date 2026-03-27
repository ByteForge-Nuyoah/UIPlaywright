import os

# ------------------------------------ 测试数据配置 ----------------------------------------------------#
ENV_VARS = {
    "common": {
        "报告标题": "UI自动化测试报告-Clue",
        "项目名称": "clueSystem",
        "tester": "会飞的🐟",
        "department": "成都研发后台",  
        "env": "test"  
    },
    "test": {
        # 测试环境前端域名
        "url": "https://clue-dev.spreadwin.cn",
        # 测试环境接口域名
        "host": "https://clueapi-dev.spreadwin.cn",
        # 超级管理员
        "admin_user_name": os.getenv("CLUE_ADMIN_USER", "xiaojing"),
        "admin_user_password": os.getenv("CLUE_ADMIN_PASSWORD", "qwer123"),
        "login_type": "PASSWD",
        "uuid": "",
        "sms_state": "LOGIN"
    },
    "prod": {
        # 生产环境前端域名
        "url": "https://clue-dev.spreadwin.cn",
        # 生产环境接口域名
        "host": "https://clueapi-dev.spreadwin.cn",
        # 超级管理员
        "admin_user_name": os.getenv("CLUE_ADMIN_USER", ""),
        "admin_user_password": os.getenv("CLUE_ADMIN_PASSWORD", ""),
    }
}
