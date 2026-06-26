# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : assert_control.py
# @Software: PyCharm
# @Desc: 断言类型封装，支持json响应断言、正则表达式响应断言、数据库断言

import types
import allure
from loguru import logger
from utils.models import AssertMethod
from playwright.sync_api import APIResponse
from utils.assertion_utils import assert_function
from utils.database_utils.mysql_handle import MysqlServer
from utils.data_utils.extract_data_handle import json_extractor, re_extract



class AssertUtils:

    def __init__(self, assert_data, response: APIResponse = None, db_info: dict = None):
        """
        断言处理
        :param assert_data: 断言数据
        :param response: 接口响应数据
        :param db_info: 数据库信息
        """

        self.assert_data = assert_data
        self.response = response
        if assert_data and db_info:
            self.db_connect = MysqlServer(**db_info)

    @property
    def get_message(self):
        """
        获取断言描述，如果未填写，则返回 `None`
        :return:
        """
        return self.assert_data.get("message", "")

    @property
    def get_assert_type(self):
        """
        检查assert_type是否是模型类AssertMethod中指定的值
        """
        assert 'assert_type' in self.assert_data.keys(), (
                " 断言数据: '%s' 中缺少 `assert_type` 属性 " % self.assert_data
        )

        # 获取断言类型对应的枚举值
        name = AssertMethod(self.assert_data.get("assert_type")).name
        return name

    @property
    def get_sql_result(self):
        """
        通过数据库查询获取查询结果
        """
        if "sql" not in self.assert_data.keys() or self.assert_data["sql"] is None:
            logger.error(f"断言数据: {self.assert_data} 缺少 'sql' 属性或 'sql' 为空")
            raise ValueError("断言数据: {self.assert_data} 缺少 'sql' 属性或 'sql' 为空")
        return self.db_connect.query_all(sql=self.assert_data["sql"])

    def get_actual_value_by_response(self):
        """
        通过jsonpath表达式从响应数据中获取实际结果
        通过jsonpath表达式从响应数据中获取实际结果
        """
        if "type_jsonpath" in self.assert_data and self.assert_data["type_jsonpath"]:
            try:
                result = self.response.json()
                return json_extractor(obj=result, expr=self.assert_data["type_jsonpath"])
            except Exception as e:
                logger.error(f"响应数据 处理成json格式报错，错误信息：{e}\n{self.response.text()}")
                raise ValueError(f"响应数据处理成json格式报错，错误信息：{e}\n{self.response.text()}")
        if "type_re" in self.assert_data and self.assert_data["type_re"]:
            return re_extract(obj=self.response.text(), expr=self.assert_data["type_re"])
        else:
            logger.debug(f"实际的值2：{self.response.text()}")
            return self.response.text()

    def get_actual_value_by_sql(self):
        """
        通过jsonpath表达式从数据库查询结果中获取实际结果
        通过正则表达式从数据库查询结果中获取实际结果
        """
        if "type_jsonpath" in self.assert_data and self.assert_data["type_jsonpath"]:
            return json_extractor(obj=self.get_sql_result, expr=self.assert_data["type_jsonpath"])
        elif "type_re" in self.assert_data and self.assert_data["type_re"]:
            return re_extract(obj=str(self.get_sql_result), expr=self.assert_data["type_re"])
        else:
            return self.get_sql_result

    @property
    def get_expect_value(self):
        """
        获取预期结果， 断言数据中应该存在key=expect_value
        """
        assert 'expect_value' in self.assert_data.keys(), (
            f"断言数据: {self.assert_data} 中缺少 `value` 属性 "
        )
        return self.assert_data.get("expect_value")

    @property
    def assert_function_mapping(self):
        """
        断言方法匹配, 获取utils\assertion_utils\assert_function.py中的方法并返回
        """
        # 从 module中获取方法的名称和所在的内存地址 """
        module_functions = {}

        for name, item in vars(assert_function).items():
            if isinstance(item, types.FunctionType):
                module_functions[name] = item
        return module_functions

    def assert_handle(self):
        """
        断言处理
        """
        if "sql" in self.assert_data.keys():
            actual_value = self.get_actual_value_by_sql()

        else:
            actual_value = self.get_actual_value_by_response()

        expect_value = self.get_expect_value
        message = str(self.get_message)
        assert_type = self.get_assert_type
        logger.info(f"\nmessage: {message}\n"
                     f"assert_type: {assert_type}\n"
                     f"expect_value: {expect_value}\n"
                     f"actual_value: {actual_value}\n")
        message = message or f"断言 --> 预期结果：{type(expect_value)} || {expect_value} 实际结果：{type(actual_value)} || {actual_value}"
        with allure.step(message):
            # 调用utils.assertion_utils.assert_type里面的方法
            self.assert_function_mapping[assert_type](expect_value=expect_value, actual_value=actual_value,
                                                      message=message)


class AssertHandle(AssertUtils):
    def get_assert_data_list(self):
        """
        获取所有的断言数据，并以列表的形式返回
        """
        assert_list = []
        if self.assert_data and isinstance(self.assert_data, dict):
            for k, v in self.assert_data.items():
                if k.lower() == "status_code":
                    with allure.step("断言 --> 响应状态码"):
                        assert_function.equals(expect_value=v, actual_value=self.response.status)
                else:
                    assert_list.append(v)
        else:
            logger.info(f"断言数据为空或者不是字典格式，跳过断言！\n"
                         f"断言数据：{self.assert_data}")
        return assert_list

    def assert_handle(self):
        """
        将收集到的断言数据逐一进行断言
        """
        for value in self.get_assert_data_list():
            self.assert_data = value
            super().assert_handle()
