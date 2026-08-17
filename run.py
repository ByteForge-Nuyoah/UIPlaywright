# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc: 框架主入口

"""
说明：
1、用例创建原则，测试文件名必须以“test”开头，测试函数必须以“test”开头。
2、运行方式：
  > python run.py  默认在test环境使用无头模式浏览器运行测试用例, 生成allure html report
  > python run.py -m demo 在test环境使用无头模式浏览器运行打了标记demo用例， 生成allure html report
  > python run.py -env live 在live环境运行测试用例
  > python run.py -env=test 在test环境运行测试用例
  > python run.py -browser webkit 使用webkit浏览器运行测试用例
  > python run.py -browser chromium webkit 使用chromium和webkit浏览器运行测试用例
  > python run.py -report=yes   生成allure html report
  > python run.py -mode=headed   使用有头模式运行
  > python run.py -env test -m 'projects or login' -report no -mode headless  在test环境，使用无头模式浏览器运行标记了project或者login的用例，并且生成allure html report
"""

import os
import argparse
import shutil
import sys
import importlib.util
import subprocess
import time
import pytest
from loguru import logger
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'env', 'config/env/.env'))
from config.settings import LOG_INFO, RunConfig
from config.config_path import BASE_DIR, REPORT_DIR, TRACING_DIR, ALLURE_RESULTS_DIR, \
    ALLURE_HTML_DIR, AUTH_DIR, LIB_DIR
from config.global_vars import GLOBAL_VARS
from utils.report_utils.send_result_handle import send_result
from utils.logger_utils.loguru_log import capture_logs
from utils.report_utils.allure_handle import generate_allure_report
from utils.report_utils.platform_handle import PlatformHandle
ENV_VARS = {}


def _load_project_config(project_name):
    global ENV_VARS
    project_test_path = ""
    project_recordings_path = ""
    if not project_name:
        return project_test_path, project_recordings_path
    project_path = os.path.join(BASE_DIR, "projects", project_name)
    if not os.path.exists(project_path):
        logger.error(f"Project path not found: {project_path}")
        return None, None
    sys.path.insert(0, project_path)
    logger.info(f"Loaded project path: {project_path}")
    project_test_path = os.path.join(project_path, "testcases")
    recordings_dir = os.path.join(project_path, "recordings")
    project_recordings_path = recordings_dir if os.path.isdir(recordings_dir) else ""
    settings_path = os.path.join(project_path, "project_settings.py")
    if os.path.exists(settings_path):
        spec = importlib.util.spec_from_file_location("project_settings", settings_path)
        project_settings = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(project_settings)
        if hasattr(project_settings, "ENV_VARS"):
            ENV_VARS = project_settings.ENV_VARS
            logger.info(f"Loaded ENV_VARS from {settings_path}")
    return project_test_path, project_recordings_path


def _apply_run_config(kwargs):
    """将命令行参数应用到 RunConfig（browser/mode/video/screenshot/tracing）。"""
    browser = kwargs.get("browser", "") or None
    RunConfig.browser = browser if browser else RunConfig.browser
    mode = kwargs.get("mode", "") or None
    RunConfig.mode = mode.lower() if mode else RunConfig.mode
    video = kwargs.get("video", "") or None
    RunConfig.video = video.lower() if video else RunConfig.video
    screenshot = kwargs.get("screenshot", "") or None
    RunConfig.screenshot = screenshot.lower() if screenshot else RunConfig.screenshot
    tracing = kwargs.get("tracing", "") or None
    RunConfig.tracing = tracing.lower() if tracing else RunConfig.tracing


def _resolve_env(env_key, env_vars):
    valid_envs = [k for k in env_vars.keys() if k != "common"]
    if not env_key:
        env_key = valid_envs[0] if valid_envs else None
        logger.warning(f"未指定 -env，默认使用环境：{env_key}")
    if env_key not in env_vars or env_key == "common":
        logger.error(f"环境 '{env_key}' 不存在，可用环境: {valid_envs}")
        return None
    if not env_vars[env_key].get("url"):
        logger.error(f"环境 '{env_key}' 的 url 未配置，请检查 project_settings.py")
        return None
    env_vars["common"]["env"] = env_key
    env_vars["common"]["env_url"] = env_vars[env_key]["url"]
    GLOBAL_VARS.update(env_vars["common"])
    GLOBAL_VARS.update(env_vars[env_key])
    return env_key


def _build_pytest_args(kwargs, project_test_path, project_recordings_path):
    """组装 pytest 命令行参数。"""
    marks = kwargs.get("m", "") or None
    custom_test_path = kwargs.get("path", "") or None
    recording_mode = (kwargs.get("recording", "") or "converted").lower()

    arg_list = [
        "-vs", "--cache-clear",
        f"--maxfail={RunConfig.max_fail}",
        f"--reruns={RunConfig.rerun}",
        f"--reruns-delay={RunConfig.reruns_delay}",
        f"--alluredir={ALLURE_RESULTS_DIR}",
        "--clean-alluredir",
        f"--output={TRACING_DIR}",
        f"--screenshot={RunConfig.screenshot}",
        f"--tracing={RunConfig.tracing}",
    ]
    if RunConfig.video:
        arg_list.extend(["--video", RunConfig.video])
    if RunConfig.mode == "headed":
        arg_list.append("--headed")

    browsers = RunConfig.browser if isinstance(RunConfig.browser, list) else [RunConfig.browser]
    for b in browsers:
        arg_list.extend(["--browser", str(b).lower()])
    if marks:
        arg_list.extend(["-m", marks])
    if custom_test_path:
        arg_list.append(custom_test_path)
    else:
        if recording_mode == "raw" and project_recordings_path:
            arg_list.append(project_recordings_path)
        elif recording_mode == "all" and project_recordings_path:
            if project_test_path:
                arg_list.append(project_test_path)
            arg_list.append(project_recordings_path)
        else:
            if project_test_path:
                arg_list.append(project_test_path)
    return arg_list


def _post_run_report(kwargs, env_vars):
    """生成 Allure 报告 + 自动打开 + 发送通知。"""
    report_path, attachment_path = generate_allure_report(
        allure_results=ALLURE_RESULTS_DIR,
        allure_report=ALLURE_HTML_DIR,
        windows_title=env_vars["common"]["project_name"],
        report_name=env_vars["common"]["report_title"],
        env_info={
            "运行环境": env_vars["common"]["env_url"],
            "测试人员": env_vars["common"]["tester"],
        },
        allure_config_path=os.path.join(LIB_DIR, "allure_config"),
        attachment_path=os.path.join(REPORT_DIR, "autotest_report.zip"),
    )
    if kwargs.get("scheduled") != "on":
        logger.info("正在打开测试报告...")
        allure_bin = PlatformHandle().allure
        proc = subprocess.Popen([allure_bin, "open", ALLURE_HTML_DIR],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            time.sleep(20)
        except KeyboardInterrupt:
            pass
        finally:
            proc.terminate()
    else:
        logger.info("定时任务模式，跳过自动打开测试报告。")
    send_result(report_info=env_vars["common"], report_path=report_path, attachment_path=attachment_path)


def run(**kwargs):
    """
    框架统一入口函数（编排：加载配置 -> 应用参数 -> 清理 -> 解析环境 -> 执行 pytest -> 生成报告）。
    """
    capture_logs(log_info=LOG_INFO)
    logger.info("""===============UI自动化测试开始了==================""")
    logger.debug(f"run方法的入参：{kwargs}")

    env_key = kwargs.get("env", "") or None
    project_name = kwargs.get("project", "clue")

    # 1. 动态加载项目配置
    project_test_path, project_recordings_path = _load_project_config(project_name)
    if project_test_path is None:
        return

    # 2. 应用运行参数到 RunConfig
    _apply_run_config(kwargs)

    # 3. 清理测试产物目录
    if os.path.isdir(TRACING_DIR):
        shutil.rmtree(TRACING_DIR, ignore_errors=True)
    os.makedirs(TRACING_DIR, exist_ok=True)
    if kwargs.get("fresh_login"):
        if os.path.isdir(AUTH_DIR):
            shutil.rmtree(AUTH_DIR, ignore_errors=True)
        os.makedirs(AUTH_DIR, exist_ok=True)
        # logger.info(f"已清空登录态目录（-fresh-login）：{AUTH_DIR}")

    if not ENV_VARS:
        logger.error("ENV_VARS is empty. Please check project settings.")
        return
    env_key = _resolve_env(env_key, ENV_VARS)
    if env_key is None:
        return

    arg_list = _build_pytest_args(kwargs, project_test_path, project_recordings_path)
    logger.debug(f"pytest运行的参数：{arg_list}")
    pytest.main(args=arg_list)

    if kwargs.get("report") == "yes":
        _post_run_report(kwargs, ENV_VARS)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="框架主入口")
    parser.add_argument("-env", default="test", help="输入运行环境：test 或 live")
    parser.add_argument("-m", help="选择需要运行的用例：python.ini配置的名称")
    parser.add_argument("-browser", nargs='*', help="浏览器驱动类型配置，支持如下类型：chromium, firefox, webkit")
    parser.add_argument("-mode", help="浏览器驱动类型配置，支持如下类型：headless, headed")
    parser.add_argument("-report", default="yes", help="是否生成allure html report，支持如下类型：yes, no")
    parser.add_argument("-scheduled", default="off", help="是否开启定时任务模式：on, off")
    parser.add_argument("-project", default="clue", help="指定运行的项目名称")
    parser.add_argument("-path", help="指定测试文件或目录路径")
    parser.add_argument("-recording", default="converted", help="选择运行录制脚本模式：converted（默认）| raw | all")
    parser.add_argument("-video", default="off", help="是否开启视频录制：on, off, retain-on-failure")
    parser.add_argument("-screenshot", default="on", help="截图策略：on, off, only-on-failure")
    parser.add_argument("-tracing", default="retain-on-failure", help="trace 策略：on, off, retain-on-failure")
    parser.add_argument("-fresh-login", dest="fresh_login", action="store_true",
                        help="启动前清空 .auth/（含上次 run 留下的 JWT），强制重新走 UI 登录")
    args = parser.parse_args()
    run(**vars(args))
