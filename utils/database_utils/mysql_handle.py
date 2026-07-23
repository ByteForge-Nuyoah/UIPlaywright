# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc: 使用pymysql模块连接mysql数据库的公共方法

import json
import pymysql
from loguru import logger
from typing import Union
from datetime import datetime
from sshtunnel import SSHTunnelForwarder  # pip install sshtunnel
from utils.tools.sensitive_handle import mask_sensitive
from utils.database_utils.base_db import BaseDB


class MysqlServer(BaseDB):
    """
    初始化数据库连接(支持通过SSH隧道的方式连接)，并指定查询的结果集以字典形式返回
    """

    def __init__(self, db_host, db_port, db_user, db_pwd, db_database, ssh=False,
                 ssh_local_port=5143, **kwargs):
        """
        初始化方法中， 连接mysql数据库， 根据ssh参数决定是否走SSH隧道方式连接mysql数据库
        """
        logger.debug("\n===============数据库配置信息=====================\n" \
                     f"db_host: {db_host}\n" \
                     f"db_port: {db_port}\n" \
                     f"db_user: {db_user}\n" \
                     "db_pwd: <redacted>\n" \
                     f"db_database: {db_database}\n" \
                     f"ssh: {ssh}\n" \
                     f"kwargs: {kwargs}\n")
        self.server = None
        try:
            if ssh:
                self.server = SSHTunnelForwarder(
                    ssh_address_or_host=(kwargs.get("ssh_host"), int(kwargs.get("ssh_port"))),  # ssh 目标服务器 ip 和 port
                    ssh_username=kwargs.get("ssh_user"),  # ssh 目标服务器用户名
                    ssh_password=kwargs.get("ssh_pwd"),  # ssh 目标服务器用户密码
                    remote_bind_address=(db_host, db_port),  # mysql 服务ip 和 part
                    local_bind_address=('127.0.0.1', ssh_local_port),  # ssh 本地绑定端口，默认 5143，可配置（传 0 让系统自动分配空闲端口）
                )
                self.server.start()
                db_host = self.server.local_bind_host  # server.local_bind_host 是 参数 local_bind_address 的 ip
                db_port = self.server.local_bind_port  # server.local_bind_port 是 参数 local_bind_address 的 port
            # 建立连接
            self.conn = pymysql.connect(host=db_host,
                                        port=db_port,
                                        user=db_user,
                                        password=db_pwd,
                                        database=db_database,
                                        charset="utf8",
                                        cursorclass=pymysql.cursors.DictCursor  # 加上pymysql.cursors.DictCursor这个返回的就是字典
                                        )
            # 创建一个游标对象
            self.cursor = self.conn.cursor()
        except Exception as e:
            logger.error(f"数据库连接失败：{e}")

    def close(self):
        """
        关闭游标、连接、SSH 隧道。半初始化（连接失败）时安全跳过。
        推荐用 `with MysqlServer(...) as mysql:` 确定性释放；__del__ 亦调用本方法兜底。
        """
        try:
            cursor = getattr(self, "cursor", None)
            conn = getattr(self, "conn", None)
            server = getattr(self, "server", None)
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            if server:
                server.close()
        except Exception as error:
            logger.error(f"关闭数据库连接异常：{error}")

    def __del__(self):
        """
        对象销毁前兜底关闭连接（不可靠，优先用 `with` 语句）。
        """
        self.close()

    def query_all(self, sql, params=None):
        """
        查询所有符合sql条件的数据
        :param sql: 执行的sql
        :return: 查询结果
        """
        try:
            self.conn.commit()
            self.cursor.execute(sql, params)
            data = self.cursor.fetchall()
            logger.debug("\n==========数据库执行结果=============\n" \
                         f"SQL: {sql}\n" \
                         f"result: {mask_sensitive(data)}\n")
            return data
        except Exception as e:
            logger.error(f"{sql} --> 报错: {e}")
            raise e

    def query_one(self, sql, params=None):
        """
        查询符合sql条件的数据的第一条数据
        :param sql: 执行的sql
        :return: 返回查询结果的第一条数据
        """
        try:
            self.conn.commit()
            self.cursor.execute(sql, params)
            data = self.cursor.fetchone()
            logger.debug("\n==============数据库执行结果================\n" \
                         f"SQL: {sql}\n" \
                         f"result: {mask_sensitive(data)}\n")
            return data
        except Exception as e:
            logger.error(f"{sql} --> 报错: {e}")
            raise e

    def insert(self, sql, params=None):
        """
        插入数据
        :param sql: 执行的sql
        """
        try:
            self.cursor.execute(sql, params)
            # 提交  只要数据库更新就要commit
            self.conn.commit()
            logger.debug("\n=========数据库执行结果===========\n" \
                         f"SQL: {sql}\n" \
                         "插入数据成功！\n")
        except Exception as e:
            logger.error(f"{sql} --> 报错: {e}")
            raise e

    def update(self, sql, params=None):
        """
        更新数据
        :param sql: 执行的sql
        """
        try:
            self.cursor.execute(sql, params)
            # 提交 只要数据库更新就要commit
            self.conn.commit()
            logger.debug("\n==========数据库执行结果============\n" \
                         f"SQL: {sql}\n" \
                         "更新数据成功！\n")
        except Exception as e:
            logger.error(f"{sql} --> 报错: {e}")
            raise e

    def query(self, sql, params=None, one=True):
        """
        根据传值决定查询一条数据还是所有
        :param sql: 查询的SQL语句（可用 %s 占位符，配合 params 参数化防注入）
        :param params: 参数化查询的参数序列，为 None 时按原样执行
        :param one: 默认True. True查一条数据，否则查所有
        :return:
        """
        try:
            if one:
                return self.query_one(sql, params)
            else:
                return self.query_all(sql, params)
        except Exception as e:
            logger.error(f"{sql} --> 报错: {e}")
            raise e

    def verify(self, result: dict) -> Union[dict, None]:
        """验证结果能否被json.dumps序列化"""
        # 尝试变成字符串，解决datetime 无法被json 序列化问题
        try:
            json.dumps(result)
        except TypeError:  # TypeError: Object of type datetime is not JSON serializable
            for k, v in result.items():
                if isinstance(v, datetime):
                    result[k] = str(v)
        return result
