# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : mysql_handle.py
# @Software: PyCharm
# @Desc: 使用pymysql模块连接mysql数据库的公共方法

import json
import pymysql
from loguru import logger
from typing import Union
from datetime import datetime
from sshtunnel import SSHTunnelForwarder  # pip install sshtunnel


class MysqlServer:
    """
    初始化数据库连接(支持通过SSH隧道的方式连接)，并指定查询的结果集以字典形式返回
    """

    def __init__(self, db_host, db_port, db_user, db_pwd, db_database, ssh=False,
                 **kwargs):
        """
        初始化方法中， 连接mysql数据库， 根据ssh参数决定是否走SSH隧道方式连接mysql数据库
        """
        logger.debug("\n======================================================\n" \
                     "-------------数据库配置信息--------------------\n"
                     f"db_host: {db_host}\n" \
                     f"db_port: {db_port}\n" \
                     f"db_user: {db_user}\n" \
                     f"db_pwd: {db_pwd}\n" \
                     f"db_database: {db_database}\n" \
                     f"ssh: {ssh}\n" \
                     f"kwargs: {kwargs}\n" \
                     "=====================================================")
        self.server = None
        try:
            if ssh:
                self.server = SSHTunnelForwarder(
                    ssh_address_or_host=(kwargs.get("ssh_host"), int(kwargs.get("ssh_port"))),  # ssh 目标服务器 ip 和 port
                    ssh_username=kwargs.get("ssh_user"),  # ssh 目标服务器用户名
                    ssh_password=kwargs.get("ssh_pwd"),  # ssh 目标服务器用户密码
                    remote_bind_address=(db_host, db_port),  # mysql 服务ip 和 part
                    local_bind_address=('127.0.0.1', 5143),  # ssh 目标服务器的用于连接 mysql 或 redis 的端口，该 ip 必须为 127.0.0.1
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

    def __del__(self):
        """
        在对象销毁前，断开游标，关闭数据库连接
        """
        try:
            # 关闭游标
            self.cursor.close()
            # 关闭数据库链接
            self.conn.close()
            # 如果开启了SSH隧道，则关闭
            if self.server:
                self.server.close()
        except AttributeError as error:
            logger.error("数据库连接失败，失败原因 %s", error)

    def query_all(self, sql):
        """
        查询所有符合sql条件的数据
        :param sql: 执行的sql
        :return: 查询结果
        """
        try:
            self.conn.commit()
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            logger.debug("\n======================================================\n" \
                         "-------------数据库执行结果--------------------\n"
                         f"SQL: {sql}\n" \
                         f"result: {data}\n" \
                         "=====================================================")
            return data
        except Exception as e:
            logger.error(f"{sql} --> 报错: {e}")
            raise e

    def query_one(self, sql):
        """
        查询符合sql条件的数据的第一条数据
        :param sql: 执行的sql
        :return: 返回查询结果的第一条数据
        """
        try:
            self.conn.commit()
            self.cursor.execute(sql)
            data = self.cursor.fetchone()
            logger.debug("\n======================================================\n" \
                         "-------------数据库执行结果--------------------\n"
                         f"SQL: {sql}\n" \
                         f"result: {data}\n" \
                         "=====================================================")
            return data
        except Exception as e:
            logger.error(f"{sql} --> 报错: {e}")
            raise e

    def insert(self, sql):
        """
        插入数据
        :param sql: 执行的sql
        """
        try:
            self.cursor.execute(sql)
            # 提交  只要数据库更新就要commit
            self.conn.commit()
            logger.debug("\n======================================================\n" \
                         "-------------数据库执行结果--------------------\n"
                         f"SQL: {sql}\n" \
                         "插入数据成功！\n" \
                         "=====================================================")
        except Exception as e:
            logger.error(f"{sql} --> 报错: {e}")
            raise e

    def update(self, sql):
        """
        更新数据
        :param sql: 执行的sql
        """
        try:
            self.cursor.execute(sql)
            # 提交 只要数据库更新就要commit
            self.conn.commit()
            logger.debug("\n======================================================\n" \
                         "-------------数据库执行结果--------------------\n"
                         f"SQL: {sql}\n" \
                         "更新数据成功！\n" \
                         "=====================================================")
        except Exception as e:
            logger.error(f"{sql} --> 报错: {e}")
            raise e

    def query(self, sql, one=True):
        """
        根据传值决定查询一条数据还是所有
        :param sql: 查询的SQL语句
        :param one: 默认True. True查一条数据，否则查所有
        :return:
        """
        try:
            if one:
                return self.query_one(sql)
            else:
                return self.query_all(sql)
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
