# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc: 断言方法

import allure
from typing import Any, Union, Text


@allure.step("预期结果：{expect_value}  == 实际结果：{actual_value}")
def equals(expect_value: Any, actual_value: Any, message: Text = ""):
    """
    判断是否相等
    """
    assert expect_value == actual_value, message


@allure.step("预期结果：{expect_value} < 实际结果：{actual_value}")
def less_than(expect_value: Union[int, float], actual_value: Union[int, float], message: Text = ""):
    """
    判断预期结果小于实际结果
    """
    assert expect_value < actual_value, message


@allure.step("预期结果：{expect_value} <= 实际结果：{actual_value}")
def less_than_or_equals(expect_value: Union[int, float], actual_value: Union[int, float], message: Text = ""):
    """
    判断预期结果小于等于实际结果
    """
    assert expect_value <= actual_value, message


@allure.step("预期结果：{expect_value} > 实际结果：{actual_value}")
def greater_than(expect_value: Union[int, float], actual_value: Union[int, float], message: Text = ""):
    """
    判断预期结果大于实际结果
    """
    assert expect_value > actual_value, message


@allure.step("预期结果：{expect_value} >= 实际结果：{actual_value}")
def greater_than_or_equals(expect_value: Union[int, float], actual_value: Union[int, float], message: Text = ""):
    """
    判断预期结果大于等于实际结果
    """
    assert expect_value >= actual_value, message


@allure.step("预期结果：{expect_value} != 实际结果：{actual_value}")
def not_equals(expect_value: Any, actual_value: Any, message: Text = ""):
    """
    判断预期结果不等于实际结果
    """
    assert expect_value != actual_value, message


@allure.step("预期结果：{expect_value}  == 实际结果：{actual_value}")
def string_equals(expect_value: Any, actual_value: Text, message: Text = ""):
    """
    判断字符串是否相等
    """
    assert expect_value == actual_value, message


@allure.step("长度相等 --> 预期结果：{expect_value}  == 实际结果：{actual_value}")
def length_equals(expect_value: int, actual_value: Text, message: Text = ""):
    """
    判断长度是否相等
    """
    assert isinstance(
        expect_value, int
    ), "expect_value 需要为 int 类型"
    assert expect_value == len(actual_value), message


@allure.step("长度大于 --> 预期结果：{expect_value}  > 实际结果：{actual_value}")
def length_greater_than(expect_value: Union[int, float], actual_value: Text, message: Text = ""):
    """
    判断长度大于
    """
    assert isinstance(
        expect_value, (float, int)
    ), "expect_value 需要为 float/int 类型"
    assert expect_value > len(str(actual_value)), message


@allure.step("长度大于等于 --> 预期结果：{expect_value}  >= 实际结果：{actual_value}")
def length_greater_than_or_equals(expect_value: Union[int, float], actual_value: Text, message: Text = ""):
    """
    判断长度大于等于
    """
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value 需要为 float/int 类型"
    assert expect_value >= len(actual_value), message


@allure.step("长度小于 --> 预期结果：{expect_value}  < 实际结果：{actual_value}")
def length_less_than(expect_value: Union[int, float], actual_value: Text, message: Text = ""):
    """
    判断长度小于
    """
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value 需要为 float/int 类型"
    assert expect_value < len(actual_value), message


@allure.step("长度小于等于 --> 预期结果：{expect_value}  <= 实际结果：{actual_value}")
def length_less_than_or_equals(expect_value: Union[int, float], actual_value: Text, message: Text = ""):
    """判断长度小于等于"""
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value 需要为 float/int 类型"
    assert expect_value <= len(actual_value), message


@allure.step("预期结果：{expect_value}  in 实际结果：{actual_value}")
def contains(expect_value: Any, actual_value: Any, message: Text = ""):
    """
    判断预期结果内容被实际结果包含
    """
    assert isinstance(
        actual_value, (list, tuple, dict, str, bytes)
    ), "actual_value 需要为  list/tuple/dict/str/bytes  类型"
    assert expect_value in actual_value, message


@allure.step("实际结果：{actual_value}  in 预期结果：{expect_value}")
def contained_by(expect_value: Any, actual_value: Any, message: Text = ""):
    """
    判断预期结果包含实际结果
    """
    assert isinstance(
        actual_value, (list, tuple, dict, str, bytes)
    ), "actual_value 需要为  list/tuple/dict/str/bytes  类型"

    assert actual_value in expect_value, message


@allure.step("实际结果：{actual_value}  是以  预期结果： {expect_value} 开头的")
def startswith(expect_value: Any, actual_value: Any, message: Text = ""):
    """
    检查实际结果的开头是否和预期结果内容的开头相等
    """
    assert str(actual_value).startswith(str(expect_value)), message


@allure.step("实际结果：{actual_value}  是以  预期结果： {expect_value} 结尾的")
def endswith(expect_value: Any, actual_value: Any, message: Text = ""):
    """
    检查实际结果的结尾是否和预期结果内容相等
    """
    assert str(actual_value).endswith(str(expect_value)), message
