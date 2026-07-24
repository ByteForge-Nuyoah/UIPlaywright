# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @File    : allure_step_flatten.py
# @Desc    : 把 Allure step 树拍平成单层：仅保留 BasePage 叶子动作（标题以「--> 」开头）
#            作为原生 step；flow / 中间 page 方法的 @allure.step 变为 no-op，不再包裹叶子，
#            故叶子 step 直接挂在用例根下，无多层嵌套。
#
#            必须在 BasePage 被导入前生效：由 root conftest 的 pytest_plugins 注册，
#            模块顶层在 projects/*/conftest 导入 pages（-> BasePage）之前执行。

import re
import allure
from functools import wraps

_real_step = allure.step            # 原始 allure.step（保留给叶子用）
_LEAF_PREFIX = "--> "
_LEAF_STRIP = re.compile(r"^-->\s*")  # 去掉叶子标题里的「--> 」日志前缀，报告更干净


class _NoOpStep:
    """非叶子方法的 @allure.step：不进入 step 上下文（消除嵌套），装饰器/with 均透传。"""

    def __init__(self, title):
        self.title = title

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper


def _patched_step(title=""):
    # BasePage 叶子：保留原生 step（去掉「--> 」前缀，标题更清爽）
    if isinstance(title, str) and title.startswith(_LEAF_PREFIX):
        return _real_step(_LEAF_STRIP.sub("", title, count=1))
    # flow / 中间方法：no-op，不建 step
    return _NoOpStep(title)


def _install():
    if getattr(allure, "step", None) is _patched_step:
        return
    allure.step = _patched_step


# 模块导入即安装（早于 BasePage 装饰器应用）
_install()


def pytest_configure(config):
    """重复执行无副作用。"""
    _install()
