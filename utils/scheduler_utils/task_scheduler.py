# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : task_scheduler.py
# @Software: PyCharm
# @Desc: TODO: Description

import schedule
import time
import subprocess
import sys
from loguru import logger
from datetime import datetime

def run_automation_task():
    """
    Execute the automation test run command.
    """
    logger.info(f"Starting scheduled task at {datetime.now()}")
    try:
        # Use the current python executable
        python_executable = sys.executable
        
        # Command to run tests in test environment
        # Note: Avoid recursion by ensuring we don't pass the scheduler flag here
        cmd = [python_executable, "run.py", "-env", "test", "-report", "yes", "-mode", "headless", "-project", "clue"]
        
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
    Start the scheduler to run the task every day at 23:00.
    """
    logger.info("Scheduler service started. Waiting for tasks...")
    logger.info("Task scheduled for every day at 23:00")
    
    # Schedule the task for 23:00
    schedule.every().day.at("23:00").do(run_automation_task)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user.")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(60)
