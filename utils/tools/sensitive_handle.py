# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @File    : sensitive_handle.py
# @Desc    : 日志脱敏：递归遮蔽 dict/list 中敏感字段的值，避免明文打印到日志/报告

import re

# 命中即脱敏的 key 正则（大小写不敏感）
_SENSITIVE_KEY_PATTERN = re.compile(
    r"(password|passwd|pwd|token|authorization|secret|cookie|api[_-]?key|access[_-]?key|private[_-]?key)",
    re.IGNORECASE,
)

_MASK = "***"


def mask_sensitive(obj):
    if isinstance(obj, dict):
        return {
            k: (_MASK if _is_sensitive(k) else mask_sensitive(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [mask_sensitive(item) for item in obj]
    if isinstance(obj, tuple):
        return tuple(mask_sensitive(item) for item in obj)
    return obj


def _is_sensitive(key):
    return bool(_SENSITIVE_KEY_PATTERN.search(str(key)))


# webhook url 中的凭据参数（access_token / key / sign / timestamp 等）
_WEBHOOK_SECRET_PATTERN = re.compile(
    r"(access_token|key|sign|timestamp)=[^&]+",
    re.IGNORECASE,
)


def mask_webhook_url(url):
    if not isinstance(url, str):
        return url
    return _WEBHOOK_SECRET_PATTERN.sub(lambda m: f"{m.group(1)}=***", url)
