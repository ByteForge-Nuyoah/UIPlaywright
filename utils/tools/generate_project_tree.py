# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : generate_project_tree.py
# @Software: PyCharm
# @Desc: TODO: Description

# -*- coding: utf-8 -*-
# @Time    : 2024/7/3 14:16
# @Author  : floraachy
# @File    : 11
# @Software: PyCharm
# @Desc:

import re
from pathlib import Path
from pathlib import WindowsPath
from typing import Optional, List


class DirectionTree:
    def __init__(self,
                 direction_name: str = 'WorkingDirection',
                 direction_path: str = '.',
                 ignore_list: Optional[List[str]] = None):
        self.owner: WindowsPath = Path(direction_path)
        self.tree: str = direction_name + '/\n'
        self.ignore_list = ignore_list
        if ignore_list is None:
            self.ignore_list = []
        self.direction_ergodic(path_object=self.owner, n=0)

    def tree_add(self, path_object: WindowsPath, n=0, last=False):
        if n > 0:
            if last:
                self.tree += '│' + ('    │' * (n - 1)) + '    └────' + path_object.name
            else:
                self.tree += '│' + ('    │' * (n - 1)) + '    ├────' + path_object.name
        else:
            if last:
                self.tree += '└' + ('──' * 2) + path_object.name
            else:
                self.tree += '├' + ('──' * 2) + path_object.name
        if path_object.is_file():
            self.tree += '\n'
            return False
        elif path_object.is_dir():
            self.tree += '/\n'
            return True

    def filter_file(self, file):
        for item in self.ignore_list:
            if re.fullmatch(item, file.name):
                return False
        return True

    def direction_ergodic(self, path_object: WindowsPath, n=0):
        dir_file: list = list(path_object.iterdir())
        dir_file.sort(key=lambda x: x.name.lower())
        dir_file = [f for f in filter(self.filter_file, dir_file)]
        for i, item in enumerate(dir_file):
            if i + 1 == len(dir_file):
                if self.tree_add(item, n, last=True):
                    self.direction_ergodic(item, n + 1)
            else:
                if self.tree_add(item, n, last=False):
                    self.direction_ergodic(item, n + 1)


if __name__ == '__main__':
    from config.path_config import BASE_DIR
    ignore_list = [
        '\.git', '__pycache__', 'venv', '.+\.whl', '\.idea', '.+\.jpg', '.+\.png',
        'css', 'admin', 'tool.py', 'db.sqlite3', "outputs", "lib", ".pytest_cache"
    ]
    tree = DirectionTree(ignore_list=ignore_list, direction_path=BASE_DIR)
    print(tree.tree)