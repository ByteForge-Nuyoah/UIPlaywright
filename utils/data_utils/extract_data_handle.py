# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : extract_data_handle.py
# @Software: PyCharm
# @Desc: 提取数据的一些方法

import re
import json
from jsonpath import jsonpath
from loguru import logger
from playwright.sync_api import APIResponse
from utils.data_utils.data_handle import data_handle


def json_extractor(obj, expr: str = '.'):
    """
    从目标对象obj, 根据表达式expr提取指定的值
    :param obj :json/dict类型数据
    :param expr: 表达式, . 提取字典所有内容， $.test_api_case 提取一级字典case， $.test_api_case.data 提取case字典下的data
    :return result: 提取的结果，未提取到返回 None
    """
    try:
        result = jsonpath(obj, expr)[0] if len(jsonpath(obj, expr)) == 1 else jsonpath(obj, expr)
        result = data_handle(obj=result)
        logger.debug(f"\n提取对象：{obj}\n"
                     f"提取表达式： {expr} \n"
                     f"提取值类型： {type(result)}\n"
                     f"提取值：{result}\n")
        return result
    except Exception as e:
        logger.error(f"\n提取对象：{obj}\n"
                     f"提取表达式： {expr}\n"
                     f"错误信息：{e}\n")


def re_extract(obj: str, expr: str = '.'):
    """
    从目标对象obj, 根据表达式expr提取指定的值
    :param obj : 字符串数据
    :param expr: 正则表达式
    :return result: 提取的结果，未提取到返回 None
    """
    try:
        # 如果提取后的数据长度为1，则取第一个元素（返回str），否则返回列表
        result = re.findall(expr, obj)[0] if len(re.findall(expr, obj)) == 1 else re.findall(expr, obj)
        # 由于提取出来的数据都是str格式，将eval一样，还原数据格式
        result = data_handle(obj=result)
        logger.debug(f"\n提取对象：{obj}\n"
                     f"提取表达式： {expr}\n"
                     f"提取值类型： {type(result)}\n"
                     f"提取值：{result}\n")
        return result
    except Exception as e:
        logger.error(f"\n提取对象：{obj}\n"
                     f"提取表达式： {expr}\n"
                     f"错误信息：{e}\n")


def response_extract(response: APIResponse, expr: str = '.'):
    """
    从response响应对象提取cookies之类
    :param response : response对象
    :param expr: 提取表达式。部分参考：response.status_code， response.cookies, response.text, response.headers, response.is_redirect
    :return result: 提取的结果，未提取到返回 None
    """
    try:
        result = eval(expr)
        logger.debug(f"\n提取表达式： {expr}\n"
                     f"提取值类型： {type(result)}\n"
                     f"提取值：{result}\n")
        return result
    except Exception as e:
        logger.debug(f"\n提取表达式： {expr}\n"
                     f"提取对象： {response}\n"
                     f"错误信息：{e}\n")


if __name__ == '__main__':
    obj = [{'id': 1, 'user_id': 102, 'action': 'autologin', 'value': '3734462a398eedd9ab7448c4e2880ddd3f9bb2cb'}]
    expre = "'user_id': (.*?),"

    res = re_extract(obj=str(obj), expr=expre)
    print(res)
