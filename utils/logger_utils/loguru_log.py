# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc: 日志处理

import os
import sys
from loguru import logger

# 控制台颜色
_LEVEL_FG = {
    "TRACE": "\033[38;2;136;136;136m",    # #888888 灰
    "DEBUG": "\033[38;2;0;153;204m",      # #0099cc 青蓝
    "INFO": "\033[38;2;51;187;51m",       # #33bb33 绿
    "SUCCESS": "\033[38;2;51;187;51m",    # 与 INFO 同色
    "WARNING": "\033[38;2;255;170;0m",    # #ffaa00 橙黄
    "ERROR": "\033[38;2;238;34;34m",      # #ee2222 红
    "CRITICAL": "\033[38;2;153;0;0m",     # #990000 暗红（FATAL）
}
_RESET = "\033[0m"


def _console_sink(message):
    color = _LEVEL_FG.get(message.record["level"].name, "")
    text = str(message)
    if not text.endswith("\n"):
        text += "\n"
    sys.stderr.write(f"{color}{text}{_RESET}" if color else text)


def capture_logs(log_info: list):
    """
    :param log_info 接受3个参数：
        filename: 日志文件名
        filter_type: 日志过滤，如：将日志级别为ERROR的单独记录到一个文件中
        level: 日志级别设置
    """
    logger.remove()  # 移除默认的 handler，避免重复打印
    # 添加控制台输出，只添加一次，并开启颜色
    logger.add(
        sink=_console_sink,
        level="DEBUG",  # 控制台默认输出 DEBUG 级别及以上
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {module}.{function}.{line} : {message}",
        colorize=False,  # 着色由 _console_sink 按 24-bit ANSI 处理
    )
    for log in log_info:
        level = log.get("level", "TRACE").upper()
        filename = log.get("filename", "./")
        filter_type = log.get("filter_type", None)
        if level in ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]:
            level = level
        else:
            logger.error(f"level={level}, 值错误\n"
                         f"level的可选值是：TRACE DEBUG INFO SUCCESS WARNING ERROR  CRITICAL\n"
                         f"将默认level=trace收集日志")
            level = "TRACE"

        dic = dict(sink=filename,  # 日志保存路径
                   rotation='3 MB',
                   retention='3 days',
                   format="{time:YYYY-MM-DD HH:mm:ss} | {level} | From {module}.{function}.{line} : {message}",  # 日志输出格式
                   encoding='utf-8',
                   level=level,  # 日志级别设置
                   enqueue=True
                   )
        if filter_type:
            dic["filter"] = lambda x, ft=filter_type: x["level"].name == ft

        logger.add(**dic)

    if os.getenv("LOG_STRUCTURED", "").lower() in ("1", "true", "yes"):
        from config.config_path import LOG_DIR
        json_path = os.path.join(LOG_DIR, "service.jsonl")
        logger.add(
            sink=json_path,
            level="DEBUG",
            serialize=True,
            rotation="3 MB",
            retention="3 days",
            encoding="utf-8",
            enqueue=True,
        )
        logger.info(f"结构化日志已启用：{json_path}")
