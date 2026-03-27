# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : conftest.py
# @Software: PyCharm
# @Desc: 这是文件的描述信息

import time
import os
from datetime import datetime
from loguru import logger
import pytest
import allure
from config.path_config import REPORT_DIR
from config.global_vars import GLOBAL_VARS
from config.settings import RunConfig
from utils.data_utils.data_handle import data_handle

# 本地插件注册
pytest_plugins = ['plugins.pytest_playwright']  # noqa
"""
添加本地插件后需要在 pytest.ini 中禁用 pip 安装的 pytest-playwright 插件
[pytest]
addopts = -p no:playwright
"""


# ------------------------------------- START: pytest-playwright fixture 覆写---------------------------------------#

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    pytest-playwright 内置 fixture 覆写
    作用域：session (整个测试会话期间只执行一次)
    功能：
    1. 在演示模式（headed）下，自适应当前屏幕尺寸（viewport=None）
    2. 在回归/CI 模式（headless）下使用固定分辨率，保证结果稳定
    """
    # 默认窗口尺寸配置，用于回归/CI 等非演示场景
    window_size = GLOBAL_VARS.get("window_size", {"width": 1920, "height": 1080})

    # headed 模式下：让 Playwright 使用真实窗口尺寸，自适应屏幕大小
    if RunConfig.mode == "headed":
        viewport = None
    else:
        viewport = window_size

    return {
        **browser_context_args,
        "viewport": viewport,
        "record_video_size": window_size,  # 录制视频尺寸保持统一，便于对比
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """
    pytest-playwright 内置 fixture 覆写
    作用域：session
    功能：配置浏览器启动参数，如是否最大化窗口、是否开启开发者工具等
    """
    return {
        **browser_type_launch_args,
        "args": ["--start-maximized"],  # 浏览器窗口最大化
        "devtools": False,
    }

# ------------------------------------- END: pytest-playwright fixture 覆写---------------------------------------#


# ------------------------------------- START: pytest钩子函数处理---------------------------------------#
def pytest_configure(config):
    """
    pytest 钩子函数：初始化配置
    功能：在测试运行前，将全局变量中的 URL 设置为 pytest 的 base_url
    """
    config.option.base_url = GLOBAL_VARS.get("url")


def pytest_runtest_call(item):  # noqa
    """
    pytest 钩子函数：测试用例执行时调用
    功能：动态读取测试类的文档字符串 (docstring)，并将其设置为 Allure 报告的 Feature 名称
    这使得报告结构更清晰，直接复用代码注释
    """
    # 动态添加测试类的 allure.feature()， 注意测试类一定要写文档注释，否则这里会显示为空
    if item.parent._obj.__doc__:  # noqa
        allure.dynamic.feature(item.parent._obj.__doc__)  # noqa


def pytest_collection_modifyitems(config, items):
    """
    pytest 钩子函数：用例收集完成后调用
    功能：
    1. 根据用例数据中的 'run' 字段决定是否跳过该用例
    2. 对用例数据进行预处理 (变量替换)，实现数据驱动中的动态值注入
    
    参数：
    - items: 收集到的所有测试用例对象列表
    """
    for item in items:
        # 注意这里的"case"需要与@pytest.mark.parametrize("case", cases)中传递的保持一致
        if "case" in item.fixturenames:
            case = item.callspec.params["case"]
            # 判断用例是否需要执行，如果不执行则跳过
            if not case.get("run"):
                item.add_marker(pytest.mark.skip(reason="用例数据中，标记了该用例为false，不执行"))
            # 对用例数据进行处理，将关键字${key}， 与全局变量GLOBAL_VARS中的值进行替换。例如${login}， 替换成GLOBAL_VARS["login"]的值。
            item.callspec.params["case"] = data_handle(case, GLOBAL_VARS)


def pytest_terminal_summary(terminalreporter, config):
    """
    pytest 钩子函数：测试会话结束后的摘要统计
    功能：
    1. 统计通过、失败、跳过、重跑的用例数量
    2. 计算成功率
    3. 将统计结果输出到日志和文件 (test_result.txt)，用于后续通知发送
    """
    _RERUN = len([i for i in terminalreporter.stats.get('rerun', []) if i.when != 'teardown'])
    try:
        # 获取pytest传参--reruns的值
        reruns_value = int(config.getoption("--reruns"))
        _RERUN = int(_RERUN / reruns_value)
    except Exception:
        reruns_value = "未配置--reruns参数"
        _RERUN = len([i for i in terminalreporter.stats.get('rerun', []) if i.when != 'teardown'])

    _PASSED = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    _ERROR = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    _FAILED = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    _SKIPPED = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    _XPASSED = len([i for i in terminalreporter.stats.get('xpassed', []) if i.when != 'teardown'])
    _XFAILED = len([i for i in terminalreporter.stats.get('xfailed', []) if i.when != 'teardown'])

    _TOTAL = terminalreporter._numcollected

    if hasattr(terminalreporter, '_sessionstarttime'):
        _start_timestamp = terminalreporter._sessionstarttime
    else:
        _start_timestamp = time.time()

    _DURATION = time.time() - _start_timestamp

    session_start_time = datetime.fromtimestamp(_start_timestamp)
    _START_TIME = f"{session_start_time.year}年{session_start_time.month}月{session_start_time.day}日 " \
                  f"{session_start_time.hour}:{session_start_time.minute}:{session_start_time.second}"

    test_info = f"各位同事, 大家好:\n" \
                f"自动化用例于 {_START_TIME}- 开始运行，运行时长：{_DURATION:.2f} s， 目前已执行完成。\n" \
                f"--------------------------------------\n" \
                f"#### 执行结果如下:\n" \
                f"- 用例运行总数: {_TOTAL} 个\n" \
                f"- 跳过用例个数（skipped）: {_SKIPPED} 个\n" \
                f"- 实际执行用例总数: {_PASSED + _FAILED + _XPASSED + _XFAILED} 个\n" \
                f"- 通过用例个数（passed）: {_PASSED} 个\n" \
                f"- 失败用例个数（failed）: {_FAILED} 个\n" \
                f"- 异常用例个数（error）: {_ERROR} 个\n" \
                f"- 重跑的用例数(--reruns的值): {_RERUN} ({reruns_value}) 个\n"
    try:
        _RATE = (_PASSED + _XPASSED) / (_PASSED + _FAILED + _XPASSED + _XFAILED) * 100
        test_result = f"- 用例成功率: {_RATE:.2f} %\n"
        logger.success(f"{test_info}{test_result}")
    except ZeroDivisionError:
        test_result = "- 用例成功率: 0.00 %\n"
        logger.critical(f"{test_info}{test_result}")

    # 这里是方便在流水线里面发送测试结果到钉钉/企业微信的
    with open(file=os.path.join(REPORT_DIR, "test_result.txt"), mode="w", encoding="utf-8") as f:
        f.write(f"{test_info}{test_result}")

# ------------------------------------- END: pytest钩子函数处理---------------------------------------#
