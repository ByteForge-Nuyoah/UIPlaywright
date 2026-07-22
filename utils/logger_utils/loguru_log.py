# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : loguru_log.py
# @Software: PyCharm
# @Desc: 日志处理

import os
import sys
from loguru import logger

# 控制台日志按级别着色（24-bit ANSI 精确匹配指定 hex）
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
    """控制台 sink：按日志级别着色整个日志行（24-bit ANSI）。"""
    color = _LEVEL_FG.get(message.record["level"].name, "")
    text = str(message)
    if not text.endswith("\n"):
        text += "\n"
    sys.stderr.write(f"{color}{text}{_RESET}" if color else text)


def capture_logs(log_info: list):
    """
    日志处理
    文档参考：https://zhuanlan.zhihu.com/p/429452898
       基本参数释义：
        sink：可以是一个 file 对象，例如 sys.stderr 或 open('file.log', 'w')，也可以是 str 字符串或者 pathlib.Path 对象，即文件路径，也可以是一个方法，可以自行定义输出实现，也可以是一个 logging 模块的 Handler，比如 FileHandler、StreamHandler 等，还可以是 coroutine function，即一个返回协程对象的函数等。
        level：日志输出和保存级别。
        format：日志格式模板。
        filter：一个可选的指令，用于决定每个记录的消息是否应该发送到 sink。
        colorize：格式化消息中包含的颜色标记是否应转换为用于终端着色的 ansi 代码，或以其他方式剥离。 如果没有，则根据 sink 是否为 tty（电传打字机缩写） 自动做出选择。
        serialize：在发送到 sink 之前，是否应首先将记录的消息转换为 JSON 字符串。
        backtrace：格式化的异常跟踪是否应该向上扩展，超出捕获点，以显示生成错误的完整堆栈跟踪。
        diagnose：异常跟踪是否应显示变量值以简化调试。建议在生产环境中设置 False，避免泄露敏感数据。
        enqueue：要记录的消息是否应在到达 sink 之前首先通过多进程安全队列，这在通过多个进程记录到文件时很有用，这样做的好处还在于使日志记录调用是非阻塞的。
        catch：是否应自动捕获 sink 处理日志消息时发生的错误，如果为 True，则会在 sys.stderr 上显示异常消息，但该异常不会传播到 sink，从而防止应用程序崩溃。
        \kwargs：仅对配置协程或文件接收器有效的附加参数

       日志级别，从低到高：
       logger.trace()   等级5
       logger.debug()   等级10
       logger.info()   等级20
       logger.success()   等级25
       logger.warning()   等级30
       logger.error()   等级40
       logger.critical()   等级50
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

    # 可选结构化日志（JSONL）：设置环境变量 LOG_STRUCTURED=1 时启用，
    # 额外输出 outputs/log/service.jsonl，便于 CI / 日志系统机器解析。默认关闭，非破坏。
    if os.getenv("LOG_STRUCTURED", "").lower() in ("1", "true", "yes"):
        from config.settings import LOG_DIR
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
        logger.info(f"结构化日志（JSON）已启用：{json_path}")
