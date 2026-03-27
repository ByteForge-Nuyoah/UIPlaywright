# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : platform_handle.py
# @Software: PyCharm
# @Desc: 跨平台的支持allure，用于生成allure测试报告

import os.path
import platform
import shutil
from config.path_config import LIB_DIR


class PlatformHandle:
    """跨平台的支持allure, webdriver"""

    @property
    def allure(self):
        """
        获取当前环境下可用的 Allure 命令行工具路径。

        查找顺序：
        1. 优先从框架自带的 LIB_DIR 目录中查找打包的 Allure 版本
        2. 如果未找到，则从系统 PATH 中查找已安装的 allure 可执行文件
        3. 两处都不存在时抛出 FileNotFoundError，提醒用户在本机或流水线中安装 Allure

        这么设计的原因：
        - 本地演示或离线环境可以使用项目自带的 Allure 发行包
        - CI/CD 环境通常通过包管理器或脚本预装 Allure，更适合直接从 PATH 中获取
        """
        # 1. 优先检查 LIB_DIR 下是否有 allure
        if os.path.exists(LIB_DIR):
            allure_dirs = [i for i in os.listdir(LIB_DIR) if i.startswith("allure")]
            if allure_dirs:
                allure_bin = os.path.join(LIB_DIR, allure_dirs[0], "bin")
                if platform.system() == "Windows":
                    allure_path = os.path.join(allure_bin, "allure.bat")
                else:
                    allure_path = os.path.join(allure_bin, "allure")
                    # 尝试赋予执行权限
                    try:
                        os.chmod(allure_path, 0o755)
                    except Exception:
                        pass
                return allure_path

        # 2. 如果 LIB_DIR 下没有，检查系统环境变量
        system_allure = shutil.which("allure")
        if system_allure:
            return system_allure

        # 3. 都没有则抛出异常或返回 None
        raise FileNotFoundError("Allure commandline tool not found in LIB_DIR or PATH.")


if __name__ == '__main__':
    res = PlatformHandle().allure
    print(res)
