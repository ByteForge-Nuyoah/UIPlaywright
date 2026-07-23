# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc:

import ast
from loguru import logger


def eval_data(data):
    """
    执行一个字符串表达式，并返回其表达式的值
    """
    try:
        if not isinstance(data, str):
            return data
        if data.isdigit():
            return data
        value = ast.literal_eval(data)
        if hasattr(value, "__call__"):
            return data
        return value
    except Exception as e:
        logger.trace(f"{data} --> 该数据不能被eval\n报错：{e}")
        return data
