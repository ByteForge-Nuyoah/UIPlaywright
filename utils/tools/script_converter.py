# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : script_converter.py
# @Software: PyCharm
# @Desc: Playwright录制脚本转换工具

"""
功能：将 Playwright codegen 录制的 pytest 脚本转换为 Page Object 模式的测试代码

使用方法：
    python script_converter.py --input recorded_script.py --output ./output --page-name LoginPage

转换规则：
    1. 解析录制脚本中的 page 操作（goto, click, fill, etc.）
    2. 将操作步骤封装为 Page 对象的方法
    3. 生成对应的测试用例文件
    4. 自动生成定位器和操作方法
"""

import os
import re
import ast
import argparse
from typing import List, Dict, Tuple
from dataclasses import dataclass
from loguru import logger


@dataclass
class LocatorInfo:
    """定位器信息"""
    name: str
    selector: str
    locator_type: str


@dataclass
class ActionInfo:
    """操作信息"""
    action_type: str
    locator: str
    value: str = ""
    description: str = ""


@dataclass
class TestCaseInfo:
    """测试用例信息"""
    name: str
    description: str
    actions: List[ActionInfo]
    assertions: List[str]


class ScriptParser:
    """录制脚本解析器"""
    
    def __init__(self, script_content: str):
        self.script_content = script_content
        self.test_cases: List[TestCaseInfo] = []
    
    def parse(self) -> List[TestCaseInfo]:
        """
        解析录制脚本，提取测试用例信息
        """
        tree = ast.parse(self.script_content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_case = self._parse_test_function(node)
                self.test_cases.append(test_case)
        
        return self.test_cases
    
    def _parse_test_function(self, node: ast.FunctionDef) -> TestCaseInfo:
        """
        解析单个测试函数
        """
        test_name = node.name
        description = ast.get_docstring(node) or ""
        actions = []
        assertions = []
        
        for stmt in node.body:
            if isinstance(stmt, ast.Expr):
                if isinstance(stmt.value, ast.Call):
                    action = self._parse_action(stmt.value)
                    if action:
                        actions.append(action)
            elif isinstance(stmt, ast.Assign):
                pass
        
        return TestCaseInfo(
            name=test_name,
            description=description,
            actions=actions,
            assertions=assertions
        )
    
    def _parse_action(self, call_node: ast.Call) -> ActionInfo:
        """
        解析单个操作调用
        """
        if not isinstance(call_node.func, ast.Attribute):
            return None
        
        func_name = call_node.func.attr
        locator = ""
        value = ""
        
        if func_name in ['goto']:
            if call_node.args:
                value = self._get_string_value(call_node.args[0])
            return ActionInfo(
                action_type='navigate',
                locator='',
                value=value,
                description=f'访问页面: {value}'
            )
        
        elif func_name in ['click', 'fill', 'type', 'check', 'uncheck']:
            locator = self._extract_locator(call_node)
            if func_name == 'fill' and len(call_node.args) > 1:
                value = self._get_string_value(call_node.args[1])
            
            return ActionInfo(
                action_type=func_name,
                locator=locator,
                value=value,
                description=f'{func_name}操作: {locator}'
            )
        
        elif func_name in ['hover', 'focus', 'press']:
            locator = self._extract_locator(call_node)
            return ActionInfo(
                action_type=func_name,
                locator=locator,
                value=value,
                description=f'{func_name}操作: {locator}'
            )
        
        return None
    
    def _extract_locator(self, call_node: ast.Call) -> str:
        """
        提取定位器表达式
        """
        if isinstance(call_node.func, ast.Attribute):
            if isinstance(call_node.func.value, ast.Call):
                inner_call = call_node.func.value
                if isinstance(inner_call.func, ast.Attribute):
                    method = inner_call.func.attr
                    if method in ['locator', 'get_by_role', 'get_by_text', 'get_by_label', 
                                  'get_by_placeholder', 'get_by_test_id', 'get_by_title']:
                        if inner_call.args:
                            arg = inner_call.args[0]
                            if isinstance(arg, ast.Constant):
                                return f'{method}={repr(arg.value)}'
                            elif isinstance(arg, ast.Str):
                                return f'{method}={repr(arg.s)}'
        
        if call_node.args:
            arg = call_node.args[0]
            if isinstance(arg, ast.Constant):
                return f'selector={repr(arg.value)}'
            elif isinstance(arg, ast.Str):
                return f'selector={repr(arg.s)}'
        
        return ""
    
    def _get_string_value(self, node) -> str:
        """
        获取字符串值
        """
        if isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Str):
            return node.s
        return ""


class PageObjectGenerator:
    """Page对象生成器"""
    
    def __init__(self, page_name: str, test_cases: List[TestCaseInfo]):
        self.page_name = page_name
        self.test_cases = test_cases
        self.locators: Dict[str, LocatorInfo] = {}
    
    def generate(self) -> str:
        """
        生成Page对象代码
        """
        self._extract_locators()
        
        code_lines = [
            f'# -*- coding: utf-8 -*-',
            f'# @Version: Python 3.13',
            f'# @Author  : 会飞的🐟',
            f'# @File    : {self._get_page_filename()}',
            f'# @Software: PyCharm',
            f'# @Desc: {self.page_name}页面对象（自动生成）',
            f'',
            f'from utils.base_utils.base_page import BasePage',
            f'from playwright.sync_api import Page',
            f'from loguru import logger',
            f'',
            f'',
            f'class {self.page_name}Page(BasePage):',
            f'    """{self.page_name}页面"""',
            f'',
        ]
        
        code_lines.extend(self._generate_locators())
        code_lines.append('')
        code_lines.extend(self._generate_methods())
        
        return '\n'.join(code_lines)
    
    def _extract_locators(self):
        """
        提取所有定位器
        """
        locator_count = {}
        
        for test_case in self.test_cases:
            for action in test_case.actions:
                if action.locator:
                    locator_key = self._generate_locator_key(action.locator, locator_count)
                    if locator_key not in self.locators:
                        locator_type = self._get_locator_type(action.locator)
                        self.locators[locator_key] = LocatorInfo(
                            name=locator_key,
                            selector=action.locator,
                            locator_type=locator_type
                        )
    
    def _generate_locator_key(self, locator: str, count_dict: Dict) -> str:
        """
        生成定位器变量名
        """
        if 'get_by_role=' in locator:
            match = re.search(r'get_by_role=(.+)', locator)
            if match:
                role = match.group(1).strip("'\"")
                key = f'locator_{role.replace(" ", "_")}'
        elif 'get_by_text=' in locator:
            match = re.search(r'get_by_text=(.+)', locator)
            if match:
                text = match.group(1).strip("'\"")
                key = f'locator_{text.replace(" ", "_")}'
        elif 'selector=' in locator:
            match = re.search(r'selector=(.+)', locator)
            if match:
                selector = match.group(1).strip("'\"")
                if selector.startswith('#'):
                    key = f'locator_{selector[1:]}'
                elif selector.startswith('.'):
                    key = f'locator_{selector[1:].replace(".", "_")}'
                else:
                    key = f'locator_element'
        else:
            key = 'locator_element'
        
        count_dict[key] = count_dict.get(key, 0) + 1
        if count_dict[key] > 1:
            return f'{key}_{count_dict[key]}'
        return key
    
    def _get_locator_type(self, locator: str) -> str:
        """
        获取定位器类型
        """
        if 'get_by_role' in locator:
            return 'role'
        elif 'get_by_text' in locator:
            return 'text'
        elif 'get_by_label' in locator:
            return 'label'
        elif 'get_by_placeholder' in locator:
            return 'placeholder'
        else:
            return 'selector'
    
    def _generate_locators(self) -> List[str]:
        """
        生成定位器定义
        """
        lines = ['    # 定位器']
        for locator_info in self.locators.values():
            locator_code = self._format_locator_code(locator_info)
            lines.append(f'    {locator_info.name} = {locator_code}')
        return lines
    
    def _format_locator_code(self, locator_info: LocatorInfo) -> str:
        """
        格式化定位器代码
        """
        selector = locator_info.selector
        if selector.startswith('get_by_role='):
            value = selector.split('=', 1)[1].strip("'\"")
            return f'"role={value}"'
        elif selector.startswith('get_by_text='):
            value = selector.split('=', 1)[1].strip("'\"")
            return f'"text={value}"'
        elif selector.startswith('get_by_label='):
            value = selector.split('=', 1)[1].strip("'\"")
            return f'"label={value}"'
        elif selector.startswith('get_by_placeholder='):
            value = selector.split('=', 1)[1].strip("'\"")
            return f'"placeholder={value}"'
        elif selector.startswith('selector='):
            value = selector.split('=', 1)[1].strip("'\"")
            return f'"{value}"'
        else:
            return f'"{selector}"'
    
    def _generate_methods(self) -> List[str]:
        """
        生成操作方法
        """
        lines = []
        
        for idx, test_case in enumerate(self.test_cases, 1):
            method_name = test_case.name.replace('test_', '').replace('_example', '')
            lines.append(f'    def {method_name}_flow(self):')
            lines.append(f'        """')
            lines.append(f'        {test_case.description or f"执行{method_name}流程"}')
            lines.append(f'        """')
            
            for action in test_case.actions:
                if action.action_type == 'navigate':
                    lines.append(f'        self.visit("{action.value}")')
                elif action.action_type == 'click':
                    locator_var = self._find_locator_var(action.locator)
                    lines.append(f'        self.click(self.{locator_var})')
                elif action.action_type == 'fill':
                    locator_var = self._find_locator_var(action.locator)
                    lines.append(f'        self.input(self.{locator_var}, "{action.value}")')
                elif action.action_type == 'type':
                    locator_var = self._find_locator_var(action.locator)
                    lines.append(f'        self.type(self.{locator_var}, "{action.value}")')
                elif action.action_type == 'hover':
                    locator_var = self._find_locator_var(action.locator)
                    lines.append(f'        self.hover(self.{locator_var})')
                elif action.action_type == 'check':
                    locator_var = self._find_locator_var(action.locator)
                    lines.append(f'        self.check(self.{locator_var})')
                elif action.action_type == 'uncheck':
                    locator_var = self._find_locator_var(action.locator)
                    lines.append(f'        self.uncheck(self.{locator_var})')
                elif action.action_type == 'focus':
                    locator_var = self._find_locator_var(action.locator)
                    lines.append(f'        self.focus(self.{locator_var})')
                elif action.action_type == 'clear':
                    locator_var = self._find_locator_var(action.locator)
                    lines.append(f'        self.clear(self.{locator_var})')
                elif action.action_type == 'select_option':
                    locator_var = self._find_locator_var(action.locator)
                    lines.append(f'        self.select_option(self.{locator_var}, "{action.value}")')
                elif action.action_type == 'upload':
                    lines.append(f'        self.upload_file("{action.locator}", "{action.value}")')
            
            lines.append(f'        logger.info("{method_name}流程执行完成")')
            lines.append('')
        
        return lines
    
    def _find_locator_var(self, locator: str) -> str:
        """
        查找定位器变量名
        """
        for locator_info in self.locators.values():
            if locator_info.selector == locator:
                return locator_info.name
        return 'locator_element'
    
    def _get_page_filename(self) -> str:
        """
        获取Page文件名
        """
        name = re.sub(r'([A-Z])', r'_\1', self.page_name).lower()
        return f'{name}_page.py'


class TestCaseGenerator:
    """测试用例生成器"""
    
    def __init__(self, page_name: str, test_cases: List[TestCaseInfo]):
        self.page_name = page_name
        self.test_cases = test_cases
    
    def generate(self) -> str:
        """
        生成测试用例代码
        """
        code_lines = [
            f'# -*- coding: utf-8 -*-',
            f'# @Version: Python 3.13',
            f'# @Author  : 会飞的🐟',
            f'# @File    : test_{self._get_test_filename()}.py',
            f'# @Software: PyCharm',
            f'# @Desc: {self.page_name}测试用例（自动生成）',
            f'',
            f'import pytest',
            f'from loguru import logger',
            f'from playwright.sync_api import Page',
            f'from pages.login_page import LoginPage',
            f'from pages.{self._get_page_import()} import {self.page_name}Page',
            f'from config.global_vars import GLOBAL_VARS',
            f'',
            f'',
            f'@pytest.mark.{self.page_name.lower()}',
            f'class Test{self.page_name}:',
            f'    """{self.page_name}测试"""',
            f'',
            f'    @pytest.fixture(autouse=True)',
            f'    def setup_teardown_for_each(self, page: Page):',
            f'        """测试前置：登录并初始化页面"""',
            f'        logger.info("\\n\\n---------------Start: 开始测试{self.page_name}-------------")',
            f'        # 登录',
            f'        self.login_page = LoginPage(page)',
            f'        self.login_page.navigate()',
            f'        self.login_page.login_on_page_flow(',
            f'            login=GLOBAL_VARS.get("admin_user_name"),',
            f'            password=str(GLOBAL_VARS.get("admin_user_password"))',
            f'        )',
            f'        # 初始化页面',
            f'        self.{self.page_name.lower()}_page = {self.page_name}Page(page)',
            f'        yield',
            f'        page.context.clear_cookies()',
            f'',
        ]
        
        code_lines.extend(self._generate_test_methods())
        
        return '\n'.join(code_lines)
    
    def _generate_test_methods(self) -> List[str]:
        """
        生成测试方法
        """
        lines = []
        
        for test_case in self.test_cases:
            method_name = test_case.name
            lines.append(f'    def {method_name}(self):')
            lines.append(f'        """')
            lines.append(f'        {test_case.description or "测试用例"}')
            lines.append(f'        """')
            
            flow_name = test_case.name.replace('test_', '').replace('_example', '')
            lines.append(f'        self.{self.page_name.lower()}_page.{flow_name}_flow()')
            lines.append('')
        
        return lines
    
    def _get_test_filename(self) -> str:
        """
        获取测试文件名
        """
        name = re.sub(r'([A-Z])', r'_\1', self.page_name).lower()
        return f'{name}'
    
    def _get_page_import(self) -> str:
        """
        获取Page导入路径
        """
        name = re.sub(r'([A-Z])', r'_\1', self.page_name).lower()
        return f'{name}/{name}_page'


class ScriptConverter:
    """脚本转换器主类"""
    
    def __init__(self, input_file: str, output_dir: str, page_name: str):
        self.input_file = input_file
        self.output_dir = output_dir
        self.page_name = page_name
        self.parser = None
        self.test_cases = []
    
    def convert(self):
        """
        执行转换
        """
        logger.info(f"开始转换录制脚本: {self.input_file}")
        
        self._read_script()
        self._parse_script()
        self._generate_files()
        
        logger.info(f"转换完成！输出目录: {self.output_dir}")
    
    def _read_script(self):
        """
        读取录制脚本
        """
        with open(self.input_file, 'r', encoding='utf-8') as f:
            self.script_content = f.read()
        logger.info("录制脚本读取成功")
    
    def _parse_script(self):
        """
        解析录制脚本
        """
        self.parser = ScriptParser(self.script_content)
        self.test_cases = self.parser.parse()
        logger.info(f"解析完成，共发现 {len(self.test_cases)} 个测试用例")
    
    def _generate_files(self):
        """
        生成文件
        """
        os.makedirs(self.output_dir, exist_ok=True)
        
        page_generator = PageObjectGenerator(self.page_name, self.test_cases)
        page_code = page_generator.generate()
        page_file = os.path.join(self.output_dir, f'{self._get_page_filename()}')
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(page_code)
        logger.info(f"Page对象已生成: {page_file}")
        
        test_generator = TestCaseGenerator(self.page_name, self.test_cases)
        test_code = test_generator.generate()
        test_file = os.path.join(self.output_dir, f'test_{self._get_test_filename()}.py')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_code)
        logger.info(f"测试用例已生成: {test_file}")
    
    def _get_page_filename(self) -> str:
        """
        获取Page文件名
        """
        name = re.sub(r'([A-Z])', r'_\1', self.page_name).lower()
        return f'{name}_page.py'
    
    def _get_test_filename(self) -> str:
        """
        获取测试文件名
        """
        name = re.sub(r'([A-Z])', r'_\1', self.page_name).lower()
        return name


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description='Playwright录制脚本转换工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python script_converter.py --input recorded.py --output ./output --page-name Login
    
    转换后的文件结构:
        output/
          ├── login_page.py      # Page对象
          └── test_login.py      # 测试用例
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='输入的录制脚本文件路径'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='./converted',
        help='输出目录（默认: ./converted）'
    )
    
    parser.add_argument(
        '--page-name', '-p',
        required=True,
        help='Page对象名称（如: Login, Order, User）'
    )
    
    args = parser.parse_args()
    
    converter = ScriptConverter(
        input_file=args.input,
        output_dir=args.output,
        page_name=args.page_name
    )
    
    converter.convert()


if __name__ == '__main__':
    main()
