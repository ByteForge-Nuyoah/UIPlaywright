# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : run.py
# @Software: PyCharm
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
import pytest
from loguru import logger
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'env', '.env'))
from config.settings import LOG_INFO, RunConfig
ENV_VARS = {}
from config.global_vars import GLOBAL_VARS
from config.path_config import BASE_DIR, REPORT_DIR, TRACING_DIR, CONF_DIR, ALLURE_RESULTS_DIR, ALLURE_HTML_DIR, AUTH_DIR
from utils.report_utils.send_result_handle import send_result
from utils.logger_utils.loguru_log import capture_logs
from utils.report_utils.allure_handle import generate_allure_report
from utils.report_utils.platform_handle import PlatformHandle
import subprocess
import time


def run(**kwargs):
    """
    框架统一入口函数

    主要职责：
    1. 解析命令行参数（环境 env / 项目 project / 浏览器 browser / 运行模式 mode 等）
    2. 根据 project 动态加载对应项目下的 project_settings.py，获取 ENV_VARS
    3. 将 ENV_VARS 写入 GLOBAL_VARS，供测试用例、Page 对象、前置 fixture 使用
    4. 组装 pytest 命令行参数并执行用例
    5. 按配置生成 Allure 报告，并在非定时任务模式下自动打开报告页面
    """
    try:
        # ------------------------ 捕获日志----------------------------
        capture_logs(log_info=LOG_INFO)

        logger.info("""\n\n ===============UI自动化测试开始了==================""")
        # ------------------------ 处理一下获取到的参数----------------------------
        logger.debug(f"run方法的入参：{kwargs}")
        # env_key：指定运行环境，如 test / live，对应 project_settings 中的 ENV_VARS 键
        env_key = kwargs.get("env", "") or None
        # marks：pytest -m 选择性运行带标记的用例，如 login / account
        marks = kwargs.get("m", "") or None
        # project_name：支持多项目隔离，默认运行 clue 项目
        project_name = kwargs.get("project", "clue")
        # 指定测试路径：文件或目录
        custom_test_path = kwargs.get("path", "") or None
        # 录制脚本运行模式：converted | raw | all
        recording_mode = (kwargs.get("recording", "") or "converted").lower()

        # ------------------------ 动态加载项目配置 ------------------------
        # Load Project Configuration
        # 这一块代码负责根据命令行参数 dynamic load 项目特有的配置和测试用例
        project_test_path = ""
        project_recordings_path = ""
        if project_name:
            # 构造项目根路径：基于仓库根 BASE_DIR，避免依赖调用方的 cwd
            project_path = os.path.join(BASE_DIR, "projects", project_name)
            if os.path.exists(project_path):
                # 将项目路径插入 sys.path，使得我们可以直接 import 该项目下的模块 (如 pages)
                # 这是一个常用的 Python 技巧，用于动态调整模块搜索路径
                sys.path.insert(0, project_path)
                logger.info(f"Loaded project path: {project_path}")

                # 设定测试用例路径：projects/项目名/testcases
                project_test_path = os.path.join(project_path, "testcases")
                # 设定录制脚本路径：projects/项目名/playwrightScript
                project_recordings_path = os.path.join(project_path, "playwrightScript")

                # 加载项目特定的配置文件 project_settings.py
                # 使用 importlib 动态导入模块，避免硬编码 import 语句
                settings_path = os.path.join(project_path, "project_settings.py")
                if os.path.exists(settings_path):
                    spec = importlib.util.spec_from_file_location("project_settings", settings_path)
                    project_settings = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(project_settings)

                    # 提取项目配置中的 ENV_VARS 并覆盖全局 ENV_VARS
                    if hasattr(project_settings, "ENV_VARS"):
                        global ENV_VARS
                        ENV_VARS = project_settings.ENV_VARS
                        logger.info(f"Loaded ENV_VARS from {settings_path}")
            else:
                logger.error(f"Project path not found: {project_path}")
                return

        # 如果命令行没有传递browser， 默认使用RunConfig.browser的值
        browser = kwargs.get("browser", "") or None
        RunConfig.browser = browser if browser else RunConfig.browser

        # 如果命令行没有传递mode， 默认使用RunConfig.mode的值
        mode = kwargs.get("mode", "") or None
        RunConfig.mode = mode.lower() if mode else RunConfig.mode

        # 如果命令行没有传递video， 默认使用RunConfig.video的值
        video = kwargs.get("video", "") or None
        RunConfig.video = video.lower() if video else RunConfig.video

        # ------------------------ 捕获日志----------------------------
        # ------------------------ 设置pytest相关参数 ------------------------
        # 已经清了 allure_results，这里把 tracing 一起清掉，保证 setUp 时是干净状态。
        if os.path.isdir(TRACING_DIR):
            shutil.rmtree(TRACING_DIR, ignore_errors=True)
        os.makedirs(TRACING_DIR, exist_ok=True)
        logger.info(f"已清空测试产物目录：{TRACING_DIR}")

        # -fresh-login：擦掉上一次 run 留下的 storage_state（含 JWT），
        # 缩短 token 静态留存窗口；也作为未来 cache 化的旁路开关。
        if kwargs.get("fresh_login"):
            if os.path.isdir(AUTH_DIR):
                shutil.rmtree(AUTH_DIR, ignore_errors=True)
            os.makedirs(AUTH_DIR, exist_ok=True)
            logger.info(f"已清空登录态目录（-fresh-login）：{AUTH_DIR}")

        # 统一使用列表形式拼接，避免 `"--browser xxx"` 这种字符串被 pytest.main 当成单个参数解析失败
        arg_list = [
            "-vs",
            f"--maxfail={RunConfig.max_fail}",
            f"--reruns={RunConfig.rerun}",
            f"--reruns-delay={RunConfig.reruns_delay}",
            f"--alluredir={ALLURE_RESULTS_DIR}",
            "--clean-alluredir",
            f"--output={TRACING_DIR}",
        ]

        if RunConfig.video:
            arg_list.extend(["--video", RunConfig.video])

        if RunConfig.mode == "headed":
            arg_list.append("--headed")

        # 浏览器支持单字符串或列表（多内核并跑），统一展开为多组 ["--browser", name]
        browsers = RunConfig.browser if isinstance(RunConfig.browser, list) else [RunConfig.browser]
        for b in browsers:
            arg_list.extend(["--browser", str(b).lower()])

        if marks:
            arg_list.extend(["-m", marks])
        
        # Add test path
        if custom_test_path:
            arg_list.append(custom_test_path)
        else:
            # 根据 recording_mode 选择测试来源
            if recording_mode == "raw" and project_recordings_path:
                arg_list.append(project_recordings_path)
            elif recording_mode == "all" and project_recordings_path:
                if project_test_path:
                    arg_list.append(project_test_path)
                arg_list.append(project_recordings_path)
            else:
                if project_test_path:
                    arg_list.append(project_test_path)

        # ------------------------ 设置全局变量 ------------------------
        if not ENV_VARS:
            logger.error("ENV_VARS is empty. Please check project settings.")
            return

        # 根据指定的环境参数，将运行环境所需相关配置数据保存到GLOBAL_VARS
        ENV_VARS["common"]["env"] = ENV_VARS[env_key]["url"]
        GLOBAL_VARS.update(ENV_VARS["common"])
        GLOBAL_VARS.update(ENV_VARS[env_key])
        # ------------------------ pytest执行测试用例 ------------------------
        logger.debug(f"pytest运行的参数：{arg_list}")
        pytest.main(args=arg_list)
        # ------------------------ 生成测试报告 ------------------------
        # ------------------------ 启动报告服务 ------------------------
        if kwargs.get("report") == "yes":
            # generate_allure_report 会将 json 结果转换成 html 报告，并打包成 zip
            report_path, attachment_path = generate_allure_report(allure_results=ALLURE_RESULTS_DIR,
                                                                  allure_report=ALLURE_HTML_DIR,
                                                                  windows_title=ENV_VARS["common"]["项目名称"],
                                                                  report_name=ENV_VARS["common"]["报告标题"],
                                                                  env_info={"运行环境": ENV_VARS["common"]["env"]},
                                                                  allure_config_path=os.path.join(CONF_DIR,
                                                                                                  "allure_config"),
                                                                  attachment_path=os.path.join(REPORT_DIR,
                                                                                               f'autotest_report.zip'))

            # 如果不是定时任务模式，则自动打开报告
            if kwargs.get("scheduled") != "on":
                # 自动打开报告并在60s后关闭
                logger.info("正在打开测试报告...")
                allure_bin = PlatformHandle().allure
                cmd = [allure_bin, "open", ALLURE_HTML_DIR]
                
                # 使用 Popen 非阻塞启动，无需固定端口（allure open 默认随机端口）
                # Popen 允许脚本继续执行而不等待命令结束
                proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logger.info("测试报告已打开，将在20秒后自动关闭服务。")
                
                try:
                    # 保持服务运行一段时间，让用户有时间查看
                    time.sleep(20)
                except KeyboardInterrupt:
                    pass
                finally:
                    # 关闭 allure 服务进程
                    proc.terminate()
                    logger.info("测试报告服务已关闭。")
            else:
                logger.info("定时任务模式，跳过自动打开测试报告。")

            # ------------------------ 发送测试结果 ------------------------

            send_result(report_info=ENV_VARS["common"], report_path=report_path, attachment_path=attachment_path)
    except Exception as e:
        raise e


if __name__ == '__main__':
    # 定义命令行参数
    parser = argparse.ArgumentParser(description="框架主入口")
    parser.add_argument("-env", default="test", help="输入运行环境：test 或 live")
    parser.add_argument("-m", help="选择需要运行的用例：python.ini配置的名称")
    parser.add_argument("-browser", nargs='*', help="浏览器驱动类型配置，支持如下类型：chromium, firefox, webkit")
    parser.add_argument("-mode", help="浏览器驱动类型配置，支持如下类型：headless, headed")
    parser.add_argument("-report", default="yes",
                        help="是否生成allure html report，支持如下类型：yes, no")
    parser.add_argument("-scheduled", default="off", help="是否开启定时任务模式：on, off")
    parser.add_argument("-project", default="clue", help="指定运行的项目名称")
    parser.add_argument("-path", help="指定测试文件或目录路径")
    parser.add_argument("-recording", default="converted",
                        help="选择运行录制脚本模式：converted（默认）| raw | all")
    parser.add_argument("-video", default="off", help="是否开启视频录制：on, off, retain-on-failure")
    parser.add_argument("-fresh-login", dest="fresh_login", action="store_true",
                        help="启动前清空 .auth/（含上次 run 留下的 JWT），强制重新走 UI 登录")
    args = parser.parse_args()
    run(**vars(args))

"""
pytest相关参数：以下也可通过pytest.ini配置
     --reruns: 失败重跑次数
     --reruns-delay 失败重跑间隔时间
     --count: 重复执行次数
    -v: 显示错误位置以及错误的详细信息
    -s: 等价于 pytest --capture=no 可以捕获print函数的输出
    -q: 简化输出信息
    -m: 运行指定标签的测试用例
    -x: 一旦错误，则停止运行
    --maxfail: 设置最大失败次数，当超出这个阈值时，则不会在执行测试用例
    "--reruns=3", "--reruns-delay=2"
    -s：这个选项表示关闭捕获输出，即将输出打印到控制台而不是被 pytest 截获。这在调试测试时很有用，因为可以直接查看打印的输出。

    --cache-clear：这个选项表示在运行测试之前清除 pytest 的缓存。缓存包括已运行的测试结果等信息，此选项可用于确保重新执行所有测试。

    --capture=sys：这个选项表示将捕获标准输出和标准错误输出，并将其显示在 pytest 的测试报告中。

    --self-contained-html：这个选项表示生成一个独立的 HTML 格式的测试报告文件，其中包含了所有的样式和资源文件。这样，您可以将该文件单独保存，在没有其他依赖的情况下查看测试结果。

    --reruns=0：这个选项表示在测试失败的情况下不重新运行测试。如果设置为正整数，例如 --reruns=3，会在测试失败时重新运行测试最多 3 次。

    --reruns-delay=5：这个选项表示重新运行测试的延迟时间，单位为秒。默认情况下，如果使用了 --reruns 选项，pytest 会立即重新执行失败的测试。如果指定了 --reruns-delay，pytest 在重新运行之前会等待指定的延迟时间。

    -p no:faulthandler 是 pytest 的命令行选项之一，用于禁用 pytest 插件 faulthandler。

    faulthandler 是一个 pytest 插件，它用于跟踪和报告 Python 进程中的崩溃和异常情况。它可以在程序遇到严重错误时打印堆栈跟踪信息，并提供一些诊断功能。

    使用 -p no:faulthandler 选项可以禁用 faulthandler 插件的加载和运行。这意味着 pytest 将不会使用该插件来处理和报告崩溃和异常情况。如果您确定不需要 faulthandler 插件的功能，或者遇到与其加载有关的问题，可以使用这个选项来禁用它。

    请注意，-p no:faulthandler 选项只会禁用 faulthandler 插件，其他可能存在的插件仍然会正常加载和运行。如果您想禁用所有插件，可以使用 -p no:all 选项。
    
    
    pytest-playwright 插件有3 个参数，可以在用例失败的时候调用。
        --tracing 是否为每个测试记录轨迹。on、off或retain-on-failure（默认值：off）。
        --video 是否为每次测试录制视频。on、off或retain-on-failure（默认值：off）。
        --screenshot 是否在每次测试后自动捕获屏幕截图。on、off或only-on-failure（默认值：
off）。

 allure相关参数：
    –-alluredir这个选项用于指定存储测试结果的路径
    
-m标记：
    在pytest中，如果需要为-m参数传递多个值，可以使用以下方式：
    
    pytest -m "value1 and value2"
    这里使用双引号将多个值括起来，并使用and关键字连接它们。这将告诉pytest只运行标记为value1和value2的测试。
    
    如果你想要运行标记为value1或value2的测试，可以使用or关键字：
    
    pytest -m "value1 or value2"
    你还可以使用not关键字来排除某个标记。例如，下面的命令将运行除了标记为value1的所有其他测试：
    
    pytest -m "not value1"
    这样，你就可以根据需要在pytest中使用-m参数传递多个值，并根据标记运行相应的测试。
    

如何解决pytest参数化时出现的Unicode编码问题？
    这个问题的原因是Pytest默认将IDs视为ASCII字符串，并在测试报告中按原样显示。由于中文字符不属于ASCII字符范围，因此Pytest会将其转换为Unicode编码表示。

    解决方案:
    我们可以在pytest.ini文件中加上如下配置：disable_test_id_escaping_and_forfeit_all_rights_to_community_support = True

"""
