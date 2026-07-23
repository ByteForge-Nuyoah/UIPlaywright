# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author: 会飞的🐟
# @Desc : 数据库抽象基类，定义统一接口供 MySQL/SQLite/PostgreSQL 等子类实现

from abc import ABC, abstractmethod


class BaseDB(ABC):
    """
    数据库抽象基类，定义统一的查询/插入/更新/关闭接口。
    """

    @abstractmethod
    def query_all(self, sql, params=None):
        """查询所有符合条件的数据，返回 list[dict]。"""

    @abstractmethod
    def query_one(self, sql, params=None):
        """查询第一条数据，返回 dict 或 None。"""

    @abstractmethod
    def insert(self, sql, params=None):
        """插入数据。"""

    @abstractmethod
    def update(self, sql, params=None):
        """更新数据。"""

    @abstractmethod
    def close(self):
        """关闭游标、连接等资源。"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
