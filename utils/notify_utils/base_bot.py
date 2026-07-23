# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc    : 通知机器人基类

from loguru import logger
from requests import request
from utils.tools.sensitive_handle import mask_webhook_url


class BaseNotifyBot:
    """
    webhook 机器人基类。
    """

    def __init__(self, webhook_url, headers=None, timeout=10):
        """
        :param webhook_url: 机器人 webhook 地址（可能含 access_token / key / sign 等凭据）
        :param headers: 请求头；不传时使用默认 JSON 头
        :param timeout: 发送超时秒数，默认 10
        """
        self.webhook_url = webhook_url
        self.headers = headers if headers is not None else {
            "Content-Type": "application/json",
            "Charset": "UTF-8",
        }
        self.timeout = timeout

    def send_message(self, payload, timeout=None):
        """
        发送消息：POST webhook，按 errcode 判定成功与否。
        :param payload: 请求 json 数据
        :param timeout: 超时秒数；为 None 时用实例 timeout（默认 10）
        :return: True 成功 / False 失败
        """
        msgtype = payload.get("msgtype", "") if isinstance(payload, dict) else ""
        logger.debug("\n================ 发送机器人消息 ================\n"
                     f"Webhook_Url: {mask_webhook_url(self.webhook_url)}\n"
                     f"内容: {payload}\n")
        try:
            response = request(
                url=self.webhook_url,
                json=payload,
                headers=self.headers,
                method="POST",
                timeout=timeout if timeout is not None else self.timeout,
            )
            resp_json = response.json()
        except Exception as e:
            logger.error(f"发送{msgtype}消息异常或响应非JSON：{e}")
            return False
        if resp_json.get("errcode") == 0:
            logger.debug("\n=============== 发送机器人消息 ===============\n"
                         f"发送{msgtype}消息成功：{resp_json}\n")
            return True
        logger.error(f"发送{msgtype}消息失败：{response.text}")
        return False
