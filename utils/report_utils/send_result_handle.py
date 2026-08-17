# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc: 根据配置文件，发送指定通知

from loguru import logger
from utils.models import NotificationType
from utils.data_utils.data_handle import data_handle
from utils.notify_utils.wechat_bot import WechatBot
from utils.notify_utils.dingding_bot import DingTalkBot
from utils.notify_utils.feishu_bot import FeishuBot
from utils.notify_utils.yagmail_bot import YagEmailServe
from utils.report_utils.get_results_handle import get_test_results_from_allure_report
from config.settings import SEND_RESULT_TYPE, email, ding_talk, wechat, feishu, email_subject, email_content, \
    ding_talk_title, ding_talk_content, wechat_content, feishu_content

def send_email(user, pwd, host, subject, content, to, attachments):
    """
    发送邮件
    """
    try:
        yag = YagEmailServe(user=user, password=pwd, host=host)
        info = {
            "subject": subject,
            "contents": content,
            "to": to,
            "attachments": attachments

        }
        yag.send_email(info)
    except Exception as e:
        logger.error(f"发送邮件通知异常， 错误信息：{e}")


def send_dingding(webhook_url, secret, title, content):
    """
    发送钉钉消息
    """
    try:
        dingding = DingTalkBot(webhook_url=webhook_url, secret=secret)
        res = dingding.send_markdown(title=title, text=content, is_at_all=True)
        if res:
            logger.info(f"发送钉钉通知成功~")
        else:
            logger.error(f"发送钉钉通知失败~")
    except Exception as e:
        logger.error(f"发送钉钉通知异常， 错误信息：{e}")


def send_wechat(webhook_url, content, attachment=None):
    """
    发送企业微信消息
    """
    try:
        wechat = WechatBot(webhook_url=webhook_url)
        msg = wechat.send_markdown(content=content)
        if msg:
            if attachment:
                file = wechat.send_file(wechat.upload_file(attachment))
                if file:
                    logger.info(f"发送企业微信通知(包括文本以及附件)成功~")
                else:
                    logger.error(f"发送企业微信通知(附件)失败~")
        else:
            logger.error(f"发送企业微信（文本）失败~")
    except Exception as e:
        logger.error(f"发送企业微信通知异常， 错误信息：{e}")


def send_feishu(webhook_url, secret, content):
    """
    发送飞书消息
    """
    try:
        feishu = FeishuBot(webhook_url=webhook_url, secret=secret)
        res = feishu.send_text(content)
        if res:
            logger.info(f"发送飞书通知成功~")
        else:
            logger.error(f"发送飞书通知失败~")
    except Exception as e:
        logger.error(f"发送飞书通知异常， 错误信息：{e}")


def send_result(report_info: dict, report_path: str, attachment_path: str = None):
    """
    发送测试结果通知
    :param report_info: 报告元数据 (测试人员、部门、环境等)
    :param report_path: Allure HTML 报告的根目录路径
    :param attachment_path: 附件路径 (通常是 zip 压缩包)
    """
    # 默认不发送任何通知
    if SEND_RESULT_TYPE == NotificationType.DEFAULT.value:
        logger.debug(f"SEND_RESULT_TYPE={SEND_RESULT_TYPE}， 配置了不发送任何邮件")
        return

    # 从 Allure 报告中提取统计信息 (passed, failed, duration 等)
    results = get_test_results_from_allure_report(report_path)
    # 合并传入的 report_info
    for k, v in report_info.items():
        results[k] = v

    # 建立发送消息的内容、函数以及参数的映射关系
    # 这是一个策略模式的简单实现，将不同的通知方式封装成配置项
    notification_mappings = {
        NotificationType.EMAIL.value: {
            'sender': send_email,
            'sender_args': {
                'user': email.get("user"),
                'pwd': email.get("password"),
                'host': email.get("host"),
                'subject': email_subject,
                'content': email_content,
                'to': email.get("to"),
                'attachments': attachment_path,
            }
        },
        NotificationType.DING_TALK.value: {
            'sender': send_dingding,
            'sender_args': {
                'webhook_url': ding_talk["webhook_url"],
                'secret': ding_talk["secret"],
                'title': ding_talk_title,
                'content': ding_talk_content,
            }
        },
        NotificationType.WECHAT.value: {
            'sender': send_wechat,
            'sender_args': {
                'webhook_url': wechat["webhook_url"],
                'content': wechat_content,
                'attachment': attachment_path,
            }
        },
        NotificationType.FEISHU.value: {
            'sender': send_feishu,
            'sender_args': {
                'webhook_url': feishu["webhook_url"],
                'secret': feishu["secret"],
                'content': feishu_content,
            }
        }
    }
    # 单一渠道发送消息
    if SEND_RESULT_TYPE in notification_mappings:
        notification = notification_mappings[SEND_RESULT_TYPE]
        # data_handle 函数用于将模板中的 ${key} 替换为 results 中的实际值
        notification['sender_args']['content'] = data_handle(obj=notification['sender_args']['content'],
                                                             source=results)
        # 获取消息发送函数
        sender = notification['sender']
        # 获取对应消息发送函数的参数
        sender_args = notification['sender_args']
        # 调用消息发送函数
        sender(**sender_args)
    # 全渠道发送消息 (SEND_RESULT_TYPE 为 ALL 或其他未定义的值时，尝试发送所有配置的渠道)
    else:
        # 遍历所有消息发送方式
        for notification in notification_mappings.values():
            # 获取消息内容并替换
            notification['sender_args']['content'] = data_handle(obj=notification['sender_args']['content'],
                                                                 source=results)
            # 获取消息发送函数
            sender = notification['sender']
            # 获取对应消息发送函数的参数
            sender_args = notification['sender_args']
            # 调用消息发送函数
            sender(**sender_args)
