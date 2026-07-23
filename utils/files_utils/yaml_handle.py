# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc: 从日志文件中提取响应数据

import yaml  # pip install pyyaml
from loguru import logger


class YamlHandle:

    def __init__(self, filename):
        """
        初始化用例文件
        :param filename: 文件绝对路径，如：D:\test\test.yaml
        """
        self.filename = filename

    @property
    def read_yaml(self):
        try:
            with open(file=self.filename, mode="r", encoding="utf-8") as fp:
                return yaml.safe_load(fp.read())
        except FileNotFoundError as e:
            logger.error(f"YAML file ({self.filename}) not found: {e}")
            raise e
        except yaml.YAMLError as e:
            logger.error(f"Error while reading YAML file ({self.filename}): {e}")
            raise e

    def write(self, data, mode="a"):
        """
        往yaml文件中写入数据，默认是追加写入
        :param data: 要写入的数据
        :param mode: 写入模式
        :return:
        """
        try:
            with open(self.filename, mode=mode, encoding="utf-8") as f:
                yaml.dump(data, f)
        except yaml.YAMLError as e:
            logger.error(f"Error while writing to YAML file ({self.filename}): {e}")
            raise e
