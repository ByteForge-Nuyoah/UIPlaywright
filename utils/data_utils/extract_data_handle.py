# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : extract_data_handle.py
# @Software: PyCharm
# @Desc: 提取数据的一些方法

import re
import json
from loguru import logger
from jsonpath import jsonpath
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
        # 用 getattr 链式访问替代 eval，避免任意代码执行
        # 支持 "response.attr" / "response.attr()" / "response.a.b"；不支持索引表达式（如 headers["k"]）
        expr = expr.strip()
        call = expr.endswith("()")
        if call:
            expr = expr[:-2]
        parts = expr.split(".")
        result = response
        for p in parts[1:]:  # 跳过首段 "response"
            if p:
                result = getattr(result, p)
        if call:
            result = result()
        logger.debug(f"\n提取表达式： {expr}{'()' if call else ''}\n"
                     f"提取值类型： {type(result)}\n"
                     f"提取值：{result}\n")
        return result
    except Exception as e:
        logger.debug(f"\n提取表达式： {expr}\n"
                     f"提取对象： {response}\n"
                     f"错误信息：{e}\n")


def extract_by_type(type_key, pairs, *, json_source=None, text_source=None, response=None):
    """
    按单个提取类型 type_key，对 pairs={提取名: 表达式} 执行提取，返回 {提取名: 提取值}。

    统一 type_jsonpath / type_re / type_response 三种提取方式的分发逻辑，
    供 request_control.after_request 等调用方复用，消除各数据来源分支内重复的 type 判断。

    :param type_key: 提取类型，type_jsonpath / type_re / type_response（大小写不敏感）
    :param pairs: {提取名: 表达式} 字典
    :param json_source: type_jsonpath 的数据源（dict/list）
    :param text_source: type_re 的数据源（str）
    :param response: type_response 所需的 APIResponse 对象
    :return: {提取名: 提取值}；类型未知或缺少必要数据源时对应项不写入并记录日志
    """
    results = {}
    if not isinstance(pairs, dict):
        logger.error(f"提取配置 {type_key} 的值不是字典格式：{pairs}")
        return results
    tk = type_key.lower()
    if tk == "type_jsonpath":
        for name, expr in pairs.items():
            results[name] = json_extractor(json_source, expr)
    elif tk == "type_re":
        for name, expr in pairs.items():
            results[name] = re_extract(text_source, expr)
    elif tk == "type_response":
        if response is None:
            logger.error("type_response 提取需要 response 对象，但未传入")
            return results
        for name, expr in pairs.items():
            results[name] = response_extract(response, expr)
    else:
        logger.error(f"提取方式：{type_key} 错误，仅支持 type_jsonpath、type_re、type_response")
    return results


if __name__ == '__main__':
    obj = [{'id': 1, 'user_id': 102, 'action': 'autologin', 'value': 'example_autologin_value'}]
    expre = "'user_id': (.*?),"

    res = re_extract(obj=str(obj), expr=expre)
    print(res)
