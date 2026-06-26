# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : func_handle.py
# @Software: PyCharm
# @Desc: 函数装饰器，它接受一个字符串参数docstring，
def add_docstring(docstring):
    """
    函数装饰器，它接受一个字符串参数docstring，
    并返回一个装饰器函数。装饰器函数接受一个函数参数func，
    并将func的__doc__属性设置为docstring。
    """
    def decorator(func):
        func.__doc__ = docstring
        return func

    return decorator


class AddCLassDocstring:
    """
    类装饰器，它接受一个字符串参数docstring，
    并返回一个装饰器函数。装饰器函数接受一个函数参数func，
    并将func的__doc__属性设置为docstring。
    """
    def __init__(self, docstring):
        self.docstring = docstring

    def __call__(self, func):
        func.__doc__ = self.docstring
        return func