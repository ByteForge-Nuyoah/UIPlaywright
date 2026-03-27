# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : request_control.py
# @Software: PyCharm
# @Desc: TODO: Description

import os
import allure
from loguru import logger
from playwright.sync_api import sync_playwright, BrowserContext, Page, APIRequestContext, APIResponse
from utils.base_utils.base_request import BaseRequest
from utils.data_utils.data_handle import data_handle, eval_data
from utils.data_utils.extract_data_handle import json_extractor, re_extract, response_extract
from utils.report_utils.allure_handle import allure_step
from utils.assertion_utils.assert_control import AssertHandle
from utils.files_utils.yaml_handle import YamlHandle
from utils.files_utils.files_handle import get_files
from utils.database_utils.mysql_handle import MysqlServer


class RequestControl(BaseRequest):
    """
    进行请求，请求后的参数提取处理
    """

    def __init__(self, api_page: Page = None, api_context: BrowserContext = None,
                 api_request_context: APIRequestContext = None):
        super().__init__(api_page=api_page, api_context=api_context, api_request_context=api_request_context)

    def get_api_data(self, api_file_path: str, key: str):
        """
        根据指定的yaml文件路径，以及key值，获取对应的接口
        :param:api_file_path 接口yaml文件路径，可以是目录，也可以是文件
        :param:key 对应接口的id
        """
        api_data = []
        if os.path.isdir(api_file_path):
            logger.debug(f"获取接口数据的目标路径是一个目录：{api_file_path}")
            api_files = get_files(target=api_file_path, end=".yaml") + get_files(target=api_file_path, end=".yml")
            for api_file in api_files:
                api_data.append(YamlHandle(filename=api_file).read_yaml)
        elif os.path.isfile(api_file_path):
            logger.debug(f"获取接口数据的目标路径是一个文件：{api_file_path}")
            api_data.append(YamlHandle(filename=api_file_path).read_yaml)

        else:
            logger.error(f"目标路径错误，请检查！api_file_path={api_file_path}")
            return None

        for single_api_file in api_data:
            for single_api in single_api_file:
                if single_api["id"].lower() == key.lower():
                    logger.debug("\n----------匹配到的api----------\n"
                                 f"匹配文件路径：{api_file_path}\n"
                                 f"匹配接口key：{key}\n"
                                 f"类型：{type(single_api)}\n"
                                 f"值：{single_api}\n")
                    return single_api
        logger.warning(f"路径： {api_file_path}， 未找到id为{key}的接口， 返回值是None")
        raise Exception(f"路径： {api_file_path}， 未找到id为{key}的接口， 返回值是None")

    def before_request(self, request_data: dict, source_data: dict = None):
        """
        针请求前，对接口数据进行处理，识别用例数据中的关键字${xxxx}，使用全局变量进行替换或者执行关键字中的方法替换为具体值
        """
        try:
            logger.debug(f"\n======================================================\n" \
                         "-------------用例数据处理前--------------------\n"
                         f"用例ID:  {type(request_data.get('id', None))} || {request_data.get('id', None)}\n" \
                         f"用例标题(title):  {type(request_data.get('title', None))} || {request_data.get('title', None)}\n" \
                         f"请求路径(url): {type(request_data.get('url', None))} || {request_data.get('url', None)}\n" \
                         f"请求方式(method): {type(request_data.get('method', None))} || {request_data.get('method', None)}\n" \
                         f"请求头(headers): {type(request_data.get('headers', None))} || {request_data.get('headers', None)}\n" \
                         f"请求类型(request_type): {type(request_data.get('request_type', None))} || {request_data.get('request_type', None)}\n" \
                         f"请求参数(payload): {type(request_data.get('payload', None))} || {request_data.get('payload', None)}\n" \
                         f"响应断言(assert_response): {type(request_data.get('assert_response', None))} || {request_data.get('assert_response', None)}\n" \
                         f"后置提取参数(extract): {type(request_data.get('extract', None))} || {request_data.get('extract', None)}\n")

            new_request_data = data_handle(obj=request_data, source=source_data)

            logger.debug("\n-------------用例数据处理后--------------------\n"
                         f"用例ID:  {type(new_request_data.get('id', None))} || {new_request_data.get('id', None)}\n" \
                         f"用例标题(title):  {type(new_request_data.get('title', None))} || {new_request_data.get('title', None)}\n" \
                         f"请求路径(url): {type(new_request_data.get('url', None))} || {new_request_data.get('url', None)}\n" \
                         f"请求方式(method): {type(new_request_data.get('method', None))} || {new_request_data.get('method', None)}\n" \
                         f"请求头(headers): {type(new_request_data.get('headers', None))} || {new_request_data.get('headers', None)}\n" \
                         f"请求类型(request_type): {type(new_request_data.get('request_type', None))} || {new_request_data.get('request_type', None)}\n" \
                         f"请求参数(payload): {type(new_request_data.get('payload', None))} || {new_request_data.get('payload', None)}\n" \
                         f"响应断言(assert_response): {type(new_request_data.get('assert_response', None))} || {new_request_data.get('assert_response', None)}\n" \
                         f"后置提取参数(extract): {type(new_request_data.get('extract', None))} || {new_request_data.get('extract', None)}\n" \
                         "=====================================================")
            return new_request_data
        except Exception as e:
            logger.error(f"接口数据处理异常：{e}")
            raise f"接口数据处理异常：\n{e}"

    @classmethod
    def api_step_record(cls, **kwargs) -> None:
        """
        在allure/logger中记录请求数据
        """
        key = kwargs.get("id")
        title = kwargs.get("title")
        url = kwargs.get("url")
        method = kwargs.get("method")
        headers = kwargs.get("headers")
        request_type = kwargs.get("request_type")
        payload = kwargs.get("payload")
        files = kwargs.get("files")
        status_code = kwargs.get("status_code")
        response_header = kwargs.get("response_header")
        response_body = kwargs.get("response_body")
        response_result = kwargs.get("response_result")

        _res = ("\n-------------发送请求--------------------\n" \
                f"ID: {key}\n" \
                f"标题: {title}\n" \
                f"请求URL: {url}\n" \
                f"请求方式: {method}\n" \
                f"请求头:   {headers}\n" \
                f"请求关键字: {request_type}\n" \
                f"请求参数: {payload}\n" \
                f"响应码: {status_code}\n" \
                f"响应header: {response_header}\n"
                # f"响应body: {response_body}\n" \
                f"响应结果: {response_result}\n")
        logger.info(_res)
        allure_step(f"ID: {key}")
        allure_step(f"标题: {title}")
        allure_step(f"请求URL: {url}")
        allure_step(f"请求方式: {method}")
        allure_step(f"请求头: {headers}")
        allure_step(f"请求关键字: {request_type}")
        allure_step(f"请求参数: {payload}")
        allure_step(f"请求文件: {files}")
        allure_step(f"响应码: {status_code}")
        allure_step(f"响应header: {response_header}")
        # allure_step(f"响应body: {response_body}")
        allure_step(f"响应结果: {response_result}")

    def api_request_flow(self, request_data: dict = None, global_var: dict = None, api_file_path: str = None,
                         key: str = None, db_info: dict = None):
        """
        发送请求并进行后置参数提取操作。

        :param request_data: 请求数据字典，包含请求所需的所有信息。
        :param global_var: 包含全局变量的字典，这些变量用于替换到请求数据的关键字:${}
        :param api_file_path: 接口所在的目录或者文件路径
        :param key: 接口的ID
        :param db_info: 数据库连接信息，用于数据库断言/数据库提取数据时连接数据库
        :return: 接口数据以及响应数据，通常是一个字典。
        :raises ValueError: 如果请求数据无效或缺失。
        """
        if request_data:
            api_info = request_data

        elif api_file_path and key:
            api_info = self.get_api_data(api_file_path=api_file_path, key=key)
        else:
            logger.error("请求数据异常")
            raise ValueError("请求数据异常")

        with allure.step(f"--> 发送接口请求, 接口名称：{api_info.get('title')} ({api_info.get('id')})"):
            new_api_data = self.before_request(request_data=api_info, source_data=global_var)

            response = self.send_request(new_api_data)

            new_api_data["status_code"] = response.status
            new_api_data["response_header"] = response.headers
            new_api_data["response_body"] = response.body().decode('utf-8')

            try:
                new_api_data["response_result"] = response.json()
            except:
                new_api_data["response_result"] = response.text()

            self.api_step_record(**new_api_data)

            # 进行响应断言
            AssertHandle(assert_data=new_api_data["assert_response"], response=response).assert_handle()

            # 进行响应参数提取，并返回提取后的数据
            if new_api_data.get("extract"):
                extract_results = self.after_request(response=response, api_data=new_api_data, db_info=db_info)
                new_api_data.update(extract_results)
            logger.debug(f"接口请求完成后，接口请求数据，响应数据 & 提取数据：{new_api_data}")
            return new_api_data

    def after_request(self, response: APIResponse, api_data, db_info=None):
        """
        请求结束后提取参数，目前支持从响应数据、数据库、用例数据中提取
        :param api_data: 接口用例数据
        :param db_info: 据库连接信息，用于数据库断言/数据库提取数据时连接数据库
        :param response: Response 响应对象
        :param api_data: 接口数据需要提取的参数字典 '{"k1": "$.data"}' 或 '{"k1": "data:(.*?)$"}'
        :return:

       """
        extract = api_data.get("extract")
        logger.info(f"断言成功后需要进行提取操作，extract={extract}")

        case_results = {}
        response_results = {}
        database_results = {}
        default_results = {}

        for k, v in extract.items():
            if k.lower() == "case":
                logger.info(f"数据来源：{k}")
                # 将用例数据作为来源
                for _k, _v in v.items():
                    if _k.lower() == "type_jsonpath":
                        for i, j in _v.items():
                            case_results[i] = json_extractor(api_data, j)

                    elif _k.lower() == "type_re":
                        for i, j in _v.items():
                            case_results[i] = re_extract(str(api_data), j)
                    else:
                        logger.error(f"提取方式： {_k} 错误，仅支持type_jsonpath、type_re两种")
                logger.info(f"数据来源：{k}， 提取结果：{case_results} --")
            elif k.lower() == "database":
                logger.info(f"数据来源：{k}")
                # 将数据库SQL执行结果作为来源
                if v.get("sql"):
                    mysql = MysqlServer(**db_info)
                    sql_result = mysql.query_all(v["sql"])
                    v.pop("sql")
                else:
                    sql_result = None
                    logger.error(f"数据库提取参数必须传入sql")
                if sql_result:
                    for _k, _v in v.items():
                        if _k.lower() == "type_jsonpath":
                            for i, j in _v.items():
                                database_results[i] = json_extractor(sql_result, j)

                        elif _k.lower() == "type_re":
                            for i, j in _v.items():
                                database_results[i] = re_extract(str(sql_result), j)
                        else:
                            logger.error(f"提取方式： {_k} 错误，仅支持type_jsonpath、type_re两种")
                logger.info(f"数据来源：{k}， 提取结果：{database_results} --")
            elif k.lower() == "response":
                logger.info(f"数据来源：{k}")
                # 来源=response
                for _k, _v in v.items():
                    if _k.lower() == "type_jsonpath":
                        for i, j in _v.items():
                            response_results[i] = json_extractor(response.json(), j)
                    elif _k.lower() == "type_re":
                        for i, j in _v.items():
                            response_results[i] = re_extract(response.text, j)
                    elif _k.lower() == "type_response":
                        for i, j in _v.items():
                            response_results[i] = response_extract(response, j)
                    else:
                        logger.error(f"提取方式： {_k} 错误，仅支持type_jsonpath、type_re、type_response三种")
                logger.info(f"数据来源：{k}， 提取结果：{response_results} --")
            else:
                logger.info(f"数据来源：Response对象")
                # 直接k=type_jsonpath, type_re, type_response, 来源默认是response
                if k.lower() == "type_jsonpath":
                    for i, j in v.items():
                        default_results[i] = json_extractor(response.json(), j)
                elif k.lower() == "type_re":
                    for i, j in v.items():
                        default_results[i] = re_extract(response.text, j)
                elif k.lower() == "type_response":
                    for i, j in v.items():
                        default_results[i] = response_extract(response, j)
                else:
                    logger.error(
                        f"数据来源默认是Response对象， 提取方式： {k} 错误，仅支持type_jsonpath、type_re、type_response三种")

                logger.info(f"数据来源：Response对象， 提取结果：{default_results}")

        return {**case_results, **response_results, **database_results, **default_results}


if __name__ == '__main__':
    import getpass

    with sync_playwright() as p:
        # 获取 google chrome 的本地缓存文件
        USER_DIR_PATH = f"C:\\Users\\{getpass.getuser()}\\AppData\Local\Google\Chrome\\User Data"
        browser = p.chromium.launch_persistent_context(
            headless=False,
            # 指定本机用户缓存地址
            user_data_dir=USER_DIR_PATH,
            # 接收下载事件
            accept_downloads=True,
            bypass_csp=True,
            slow_mo=1000,
            channel="chrome",

        )

        page = browser.new_page()
        api_data = {
            "request_type": "json",
            "url": f"https://www.gitlink.org.cn/api/v1/floraachy/openCC/issues",
            "method": "POST",
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "payload": {
                "description": "playwright test",
                "subject": "1",
                "status_id": "1",
                "priority_id": "2",
                "start_date": "",
                "due_date": "",
                "receivers_login": []
            },
            "extract": {
                "type_jsonpath": {
                    "issue_id": "$.project_issues_index"
                }
            }
        }
        rc = RequestControl(api_page=page).api_request_flow(request_data=api_data)
        print(rc)
