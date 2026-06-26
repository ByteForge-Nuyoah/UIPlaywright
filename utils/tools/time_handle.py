# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : time_handle.py
# @Software: PyCharm
# @Desc: 时间处理

import time


def timestamp_strftime(timestamp, style="%Y-%m-%d %H:%M:%S"):
    """
    将时间戳转换为指定格式日期
    """
    try:
        if isinstance(timestamp, str):
            timestamp = eval(timestamp)
        return time.strftime(style, time.localtime(float(timestamp / 1000)))
    except Exception as e:
        return f"timestamp或者style格式错误：{e}"
