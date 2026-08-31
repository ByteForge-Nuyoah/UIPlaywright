import os


ENV_VARS = {
    "common": {
        "report_title": "SurgSmart UI自动化测试报告",
        "project_name": "surgsmart",
        "tester": "会飞的🐟",
        "department": "成都研发后台",
        "env": "test",
    },
    "test": {
        "url": "https://app.test.surgsmart.com",
        "host": "https://api.test.surgsmart.com",
        "admin_user_name": os.getenv("SURGSMART_USER", ""),
        "admin_user_password": os.getenv("SURGSMART_PASSWORD", ""),
    },
}
