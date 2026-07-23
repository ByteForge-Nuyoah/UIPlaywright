# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc: pytest 配置文件

import os
import time
import pytest
import allure
from loguru import logger
from datetime import datetime
from config.global_vars import GLOBAL_VARS
from utils.data_utils.data_handle import data_handle
from config.settings import resolve_window_size
from config.config_path import REPORT_DIR

# 本地插件注册
pytest_plugins = [
    'plugins.allure_playwright_attach',  # 失败用例的截图/视频/trace 自动挂到 Allure
    'plugins.allure_fixture_filter',     # 过滤 Allure Set up/Tear down 区域的内部噪声 fixture
]


# ------------------------------------- START: pytest-playwright fixture 覆写---------------------------------------#

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    pytest-playwright 内置 fixture 覆写
    作用域：session (整个测试会话期间只执行一次)
    """
    window_size = resolve_window_size()
    return {
        **browser_context_args,
        "viewport": window_size,
        "screen": window_size,
        "record_video_size": window_size,  # 录制视频尺寸保持统一，便于对比
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """
    pytest-playwright 内置 fixture 覆写
    作用域：session
    """
    window_size = resolve_window_size()
    args = list(browser_type_launch_args.get("args", []))
    args.extend([
        "--start-maximized",
        f"--window-size={window_size['width']},{window_size['height']}",
    ])

    return {
        **browser_type_launch_args,
        "args": args,
        "devtools": False,
    }

# ------------------------------------- END: pytest-playwright fixture 覆写---------------------------------------#


# ------------------------------------- START: pytest钩子函数处理---------------------------------------#
def pytest_configure(config):
    """
    pytest 钩子函数：初始化配置
    """
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'env', '.env')
    load_dotenv(_env_path)
    config.option.base_url = GLOBAL_VARS.get("url")


def pytest_runtest_call(item):  # noqa
    """
    pytest 钩子函数：测试用例执行时调用
    """
    # 动态添加测试类的 allure.feature()， 注意测试类一定要写文档注释，否则这里会显示为空
    if item.parent._obj.__doc__:  # noqa
        allure.dynamic.feature(item.parent._obj.__doc__)  # noqa


def pytest_collection_modifyitems(config, items):
    """
    pytest 钩子函数：用例收集完成后调用
    参数：items: 收集到的所有测试用例对象列表
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
                f"==================================================\n" \
                f"#### 测试执行结果如下:\n" \
                f"- 用例运行总数: {_TOTAL} 个\n" \
                f"- 跳过用例个数（skipped）: {_SKIPPED} 个\n" \
                f"- 实际执行用例总数: {_PASSED + _FAILED + _XPASSED + _XFAILED} 个\n" \
                f"- 通过用例个数（passed）: {_PASSED} 个\n" \
                f"- 失败用例个数（failed）: {_FAILED} 个\n" \
                f"- 异常用例个数（error）: {_ERROR} 个\n" \
                f"- 重跑的用例数(--reruns的值): {_RERUN} ({reruns_value}) 个\n"
    try:
        # 成功率 = 成功数 / 实际执行数（passed/failed/error/xpassed/xfailed，排除 skipped），
        _executed = _PASSED + _FAILED + _ERROR + _XPASSED + _XFAILED
        _RATE = (_PASSED + _XPASSED) / _executed * 100 if _executed > 0 else 0.0
        test_result = f"- 用例成功率: {_RATE:.2f} %\n"
        logger.success(f"{test_info}{test_result}")
    except ZeroDivisionError:
        test_result = "- 用例成功率: 0.00 %\n"
        logger.critical(f"{test_info}{test_result}")

    # 这里是方便在流水线里面发送测试结果到钉钉/企业微信的
    with open(file=os.path.join(REPORT_DIR, "test_result.txt"), mode="w", encoding="utf-8") as f:
        f.write(f"{test_info}{test_result}")

# ------------------------------------- END: pytest钩子函数处理---------------------------------------#
