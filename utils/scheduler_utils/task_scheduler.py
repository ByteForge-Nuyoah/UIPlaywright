# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : task_scheduler.py
# @Software: PyCharm
# @Desc: 定时任务

import os
import sys

# 确保项目根目录在 sys.path 中，使得直接以脚本方式启动（python .../task_scheduler.py）时
# 也能正确解析 from config.settings import ...
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import time
import schedule
import subprocess
from loguru import logger
from datetime import datetime

from config.settings import scheduler, BASE_DIR


def run_automation_task():
    """
    Execute the automation test run command.
    """
    logger.info(f"Starting scheduled task at {datetime.now()}")
    try:
        # Use the current python executable
        python_executable = sys.executable

        # 用 BASE_DIR 拼接 run.py 绝对路径，避免依赖启动时的工作目录；
        # 运行参数统一由 config.settings.scheduler["run_args"] 配置，注意此处不传 -scheduled 以免与调度器递归
        run_script = os.path.join(BASE_DIR, "run.py")
        cmd = [python_executable, run_script] + scheduler["run_args"]

        logger.info(f"Executing command: {' '.join(cmd)}")

        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)

        logger.info(f"Task finished. Return code: {result.returncode}")

        if result.stdout:
            logger.info(f"Output:\n{result.stdout}")

        if result.stderr:
            logger.warning(f"Errors/Warnings:\n{result.stderr}")

    except Exception as e:
        logger.error(f"Failed to run scheduled task: {e}")


def start_scheduler():
    """
    按 config.settings.scheduler["time"] 配置的时间每天触发一次自动化任务。
    """
    logger.info("Scheduler service started. Waiting for tasks...")
    logger.info(f"Task scheduled for every day at {scheduler['time']}")

    # 每天到点执行，执行时间由 scheduler["time"] 配置
    schedule.every().day.at(scheduler["time"]).do(run_automation_task)

    while True:
        try:
            schedule.run_pending()
            time.sleep(scheduler["interval"])  # 轮询间隔由 scheduler["interval"] 配置
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user.")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(scheduler["interval"])


if __name__ == '__main__':
    start_scheduler()
