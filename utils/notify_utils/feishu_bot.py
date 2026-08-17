# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc: 飞书机器人

import time
import hmac
import hashlib
import base64
from utils.notify_utils.base_bot import BaseNotifyBot


class FeishuBot(BaseNotifyBot):
    """
    飞书自定义机器人
    官方文档：https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot
    支持文本（text）、富文本（post）、图片（image）、消息卡片（interactive）等消息类型。
    安全设置支持自定义关键词、IP 白名单、加签三种模式，加签模式需传入 secret。
    """

    def __init__(self, webhook_url, secret=None):
        """
        :param webhook_url: 机器人的 WebHook_url
        :param secret: 安全设置-加签模式的密钥；启用加签时必填，其余模式留空即可
        """
        self.secret = secret
        super().__init__(webhook_url=webhook_url)

    def _is_success(self, resp_json):
        """
        飞书响应成功标识：新版为 code=0，旧版为 StatusCode=0
        """
        return resp_json.get("code", resp_json.get("StatusCode")) == 0

    def _build_sign(self, timestamp):
        """
        生成加签签名。
        签名校验：把 "timestamp\\nsecret" 作为签名字符串，使用 HmacSHA256 算法计算签名，再进行 Base64 encode。
        :param timestamp: 当前时间戳（秒，字符串）
        :return: 签名字符串
        """
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            self.secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256).digest()
        return base64.b64encode(hmac_code).decode("utf-8")

    def _with_sign(self, payload):
        """
        启用加签时，在请求体中追加 timestamp 与 sign 字段。
        """
        if self.secret:
            timestamp = str(round(time.time()))
            payload["timestamp"] = timestamp
            payload["sign"] = self._build_sign(timestamp)
        return payload

    def send_text(self, content):
        """
        发送文本消息
        :param content: 文本内容，最长不超过 4096 个字节
        """
        payload = self._with_sign({
            "msg_type": "text",
            "content": {
                "text": content
            }
        })
        return self.send_message(payload)

    def send_markdown(self, title, content):
        """
        发送消息卡片（interactive），卡片内使用 markdown 元素渲染富文本。
        飞书卡片 markdown 支持的语法子集：加粗、斜体、删除线、链接、有序/无序列表等，
        不支持 # 标题语法，标题请通过 card.header 设置。
        :param title: 卡片标题
        :param content: markdown 内容
        """
        payload = self._with_sign({
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": content
                    }
                ]
            }
        })
        return self.send_message(payload)
