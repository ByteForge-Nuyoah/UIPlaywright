# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : path_config.py
# @Software: PyCharm
# @Desc: 项目相关路径

import os
# ------------------------------------ 项目路径 ----------------------------------------------------#
# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 工具类目录
UTILS_DIR = os.path.join(BASE_DIR, "utils")

# 接口池目录
INTERFACE_DIR = os.path.join(BASE_DIR, "interfaces")

# 配置模块目录
CONF_DIR = os.path.join(BASE_DIR, "config")

# 用户登录态保存目录
AUTH_DIR = os.path.join(BASE_DIR, ".auth")
if not os.path.exists(AUTH_DIR):
    os.mkdir(AUTH_DIR)

# 测试过程中所需上传附件目录
FILES_DIR = os.path.join(BASE_DIR, "files")

# 日志/报告保存目录
OUT_DIR = os.path.join(BASE_DIR, "outputs")
if not os.path.exists(OUT_DIR):
    os.mkdir(OUT_DIR)

# 报告保存目录
REPORT_DIR = os.path.join(OUT_DIR, "report")
if not os.path.exists(REPORT_DIR):
    os.mkdir(REPORT_DIR)

# 日志保存目录
LOG_DIR = os.path.join(OUT_DIR, "log")
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

# playwright执行过程中产生的图片，视频保存的目录
TRACING_DIR = os.path.join(OUT_DIR, "tracing")

# 第三方库目录
LIB_DIR = os.path.join(BASE_DIR, "lib")

# Allure报告，测试结果集目录
ALLURE_RESULTS_DIR = os.path.join(REPORT_DIR, "allure_results")

# Allure报告，HTML测试报告目录
ALLURE_HTML_DIR = os.path.join(REPORT_DIR, "allure_html")
