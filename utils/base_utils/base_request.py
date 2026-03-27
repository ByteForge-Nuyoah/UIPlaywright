# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : base_request.py
# @Software: PyCharm
# @Desc: TODO: Description

from typing import Optional, Dict, Any
from playwright.sync_api import BrowserContext, Page, APIRequestContext
from loguru import logger


class BaseRequest:
    """
     playwright_发起接口请求
     Playwright下发起接口请求有三种方法:
        1) browser_context.request
        2) page.request发起请求
        3) 手动创建一个新的APIRequest上下文实例发起请求（不需要打开浏览器）。
        前两种属于通过浏览器发起请求，需要驱动浏览器。如果不想驱动浏览器直接发起接口请求可以使用第三种。
    另外每个Playwright浏览器上下文都有与其关联的APIRequestContext实例，该实例与浏览器上下文共享cookie存储，所以在接口与接口之间不需要手动管理cookie，这一点就跟requests库下的session类的作用一样。
    """

    def __init__(self, api_page: Page = None, api_context: BrowserContext = None,
                 api_request_context: APIRequestContext = None):
        if api_context:
            # context对象创建接口请求实例
            self.api = api_context.request
        elif api_page:
            # page对象创建接口请求实例
            self.api = api_page.request
        else:
            # api_request对象创建接口请求实例
            self.api = api_request_context

    def send_request(self, req_data):
        """
        处理请求数据，转换成可用数据发送请求
        :param req_data: 请求数据
        :return: 响应对象
        """
        try:

            return self.send_api(
                request_type=req_data.get("request_type").lower(),
                url=req_data.get("url"),
                method=req_data.get("method").lower(),
                headers=req_data.get("headers", None),
                payload=req_data.get("payload", None))
        except Exception as e:
            logger.error(f"请求出错，{str(e)}")
            raise ValueError(f"请求出错，{str(e)}")

    def send_api(self, request_type: str, url: str, method: str, headers: Dict[str, str],
                 payload: Optional[Dict[str, Any]] = None):
        """
        发送不同类型的接口请求，并处理响应。

        :param request_type: 请求的类型（json、form、multipart、params）
        :param url: 请求的URL
        :param method: 请求的方法（GET、POST等）
        :param headers: 请求的头部信息
        :param payload: 请求的负载信息
        :return: 响应结果
            body():获取响应正文，字节码格式。
            body().decode('utf-8'):可以在正文后用decode(‘utf-8’)将字节码转为字符串
            text():获取响应正文，字符串格式
            json()：获取响应为json格式的正文
            headers:获取响应头
            headers_array:获取响应头，列表格式
            Ok：判断接口是否正常访问;正常访问则返回True，访问失败则返回False
            status：获取接口访问状态码
        """
        if request_type == "json":
            """
            当Content-Type的值为application/json,说明接口的数据格式为json格式，这个时候需要使用data
            """
            return self.api.fetch(url_or_request=url, method=method, headers=headers,
                                  data=payload)
        elif request_type == "form":
            """
            当Content-Type的值为application/x-www-form-urlencoded,说明接口的数据格式为form格式
            """
            return self.api.fetch(url_or_request=url, method=method, headers=headers,
                                  form=payload)
        elif request_type == "multipart":
            """
            当Content-Type的值为multipart/form-data,说明接口传递的数据为表单数据且有多部分构成，这个时候需要使用multipart
            """
            return self.api.fetch(url_or_request=url, method=method, headers=headers,
                                  multipart=payload)
        elif request_type == "params":
            return self.api.fetch(url_or_request=url, method=method, headers=headers, params=payload)
        else:
            logger.error("不支持的请求类型: {request_type}, request_type可选关键字为params, json, form, multipart")
            raise ValueError(
                f"不支持的请求类型: {request_type}, request_type可选关键字为params, json, form, multipart")


if __name__ == '__main__':
    # ------------------- 第三种方法 ---------------------#
    """通过调用api_request.new_context（）手动创建一个新的APIRequest上下文实例发起请求"""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        context = p.request.new_context()
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
            }
        }
        res = BaseRequest(api_request_context=context).send_request(api_data)
        print(res.json())

    # ------------------- 第二种方法 ---------------------#
    """page.request发起请求"""
    import getpass

    with sync_playwright() as p:
        # 获取 google chrome 的本地缓存文件，只需要在浏览器上登录后，就能获取到用户信息。注意：使用的时候需要关闭掉浏览器所有窗口，否则会报错
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
        # browser = p.chromium.launch(headless=False, slow_mo=1000, channel="chrome")
        page = browser.new_page()

        api = BaseRequest(api_page=page)
        api_data = {
            "request_type": "json",
            "url": f"https://www.gitlink.org.cn/admins/users/134/reset_login_times",
            "method": "POST",
            "headers": {"Content-Type": "application/json; charset=utf-8"},
        }
        res = api.send_api(**api_data)
        print(res.text())
