# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : raw_script_converter.py
# @Software: PyCharm
# @Desc: Playwright原始录制脚本转换工具（支持clue.md格式）

"""
功能：将 Playwright codegen 录制的原始操作序列（如 clue.md）转换为 Page Object 模式的测试代码

使用方法：
    python raw_script_converter.py --input clue.md --output ./output --page-name Welcome

转换规则：
    1. 解析原始操作序列（page.goto, page.click, page.fill, etc.）
    2. 根据注释自动分割测试场景
    3. 将操作步骤封装为 Page 对象的方法
    4. 生成对应的测试用例文件
"""

import os
import re
import argparse
from typing import List, Dict, Tuple
from dataclasses import dataclass
from loguru import logger


@dataclass
class ActionInfo:
    """操作信息"""
    action_type: str
    locator: str = ""
    value: str = ""
    raw_code: str = ""
    description: str = ""


@dataclass
class ScenarioInfo:
    """场景信息"""
    name: str
    description: str
    actions: List[ActionInfo]


class RawScriptParser:
    """原始脚本解析器"""
    
    def __init__(self, script_content: str):
        self.script_content = script_content
        self.scenarios: List[ScenarioInfo] = []
    
    def parse(self) -> List[ScenarioInfo]:
        """
        解析原始脚本，提取测试场景信息
        """
        lines = self.script_content.strip().split('\n')
        current_scenario = None
        current_actions = []
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行
            if not line:
                continue
            
            # 检测注释（场景分隔符）
            if line.startswith('#'):
                # 保存前一个场景
                if current_scenario and current_actions:
                    self.scenarios.append(ScenarioInfo(
                        name=current_scenario,
                        description=current_scenario,
                        actions=current_actions
                    ))
                
                # 开始新场景
                current_scenario = line[1:].strip()
                current_actions = []
                continue
            
            # 解析操作
            action = self._parse_action(line)
            if action:
                current_actions.append(action)
        
        # 保存最后一个场景
        if current_scenario and current_actions:
            self.scenarios.append(ScenarioInfo(
                name=current_scenario,
                description=current_scenario,
                actions=current_actions
            ))
        
        return self.scenarios
    
    def _parse_action(self, line: str) -> ActionInfo:
        """
        解析单个操作
        """
        # 匹配 page.goto()
        if 'page.goto(' in line:
            match = re.search(r'page\.goto\("([^"]+)"', line)
            if match:
                return ActionInfo(
                    action_type='navigate',
                    value=match.group(1),
                    raw_code=line,
                    description=f'访问页面: {match.group(1)}'
                )
        
        # 匹配 page.get_by_role().click()
        elif 'page.get_by_role(' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("([^"]+)",?\s*name="([^"]+)"?\)', line)
            if match:
                role = match.group(1)
                name = match.group(2) if match.group(2) else ""
                return ActionInfo(
                    action_type='click',
                    locator=f'role={role}',
                    value=name,
                    raw_code=line,
                    description=f'点击角色为"{role}"的元素'
                )
        
        # 匹配 page.get_by_role().fill()
        elif 'page.get_by_role(' in line and '.fill(' in line:
            match = re.search(r'page\.get_by_role\("([^"]+)",?\s*name="([^"]+)"?\)\.fill\("([^"]+)"\)', line)
            if match:
                role = match.group(1)
                name = match.group(2) if match.group(2) else ""
                value = match.group(3)
                return ActionInfo(
                    action_type='fill',
                    locator=f'role={role}',
                    value=value,
                    raw_code=line,
                    description=f'在角色为"{role}"的元素中输入: {value}'
                )
        
        # 匹配 page.get_by_text().click()
        elif 'page.get_by_text(' in line and '.click()' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)"', line)
            if match:
                text = match.group(1)
                # 检查是否有 .first 或 .nth()
                if '.first' in line:
                    locator = f'text={text}'
                    index = 'first'
                elif '.nth(' in line:
                    nth_match = re.search(r'\.nth\((\d+)\)', line)
                    index = nth_match.group(1) if nth_match else '0'
                    locator = f'text={text}[{index}]'
                else:
                    locator = f'text={text}'
                    index = None
                
                return ActionInfo(
                    action_type='click',
                    locator=locator,
                    value=text,
                    raw_code=line,
                    description=f'点击文本为"{text}"的元素'
                )
        
        # 匹配 page.locator().click()
        elif 'page.locator(' in line and '.click()' in line:
            match = re.search(r'page\.locator\("([^"]+)"', line)
            if match:
                selector = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=selector,
                    raw_code=line,
                    description=f'点击元素: {selector}'
                )
        
        # 匹配 page.locator().filter().click()
        elif 'page.locator(' in line and '.filter(' in line and '.click()' in line:
            match = re.search(r'page\.locator\("([^"]+)"\)\.filter\(has_text=([^)]+)\)', line)
            if match:
                selector = match.group(1)
                filter_text = match.group(2)
                return ActionInfo(
                    action_type='click',
                    locator=f'{selector}[has_text={filter_text}]',
                    raw_code=line,
                    description=f'点击筛选后的元素: {selector}'
                )
        
        # 匹配 page.get_by_role().check()
        elif 'page.get_by_role(' in line and '.check()' in line:
            match = re.search(r'page\.get_by_role\("([^"]+)",?\s*name="([^"]+)"?\)', line)
            if match:
                role = match.group(1)
                name = match.group(2) if match.group(2) else ""
                return ActionInfo(
                    action_type='check',
                    locator=f'role={role}',
                    value=name,
                    raw_code=line,
                    description=f'勾选角色为"{role}"的元素'
                )
        
        # 匹配 page.get_by_role().press()
        elif 'page.get_by_role(' in line and '.press(' in line:
            match = re.search(r'page\.get_by_role\("([^"]+)",?\s*name="([^"]+)"?\)\.press\("([^"]+)"\)', line)
            if match:
                role = match.group(1)
                name = match.group(2) if match.group(2) else ""
                key = match.group(3)
                return ActionInfo(
                    action_type='press',
                    locator=f'role={role}',
                    value=key,
                    raw_code=line,
                    description=f'按下按键: {key}'
                )
        
        # 匹配 page.get_by_text().nth().click()
        elif 'page.get_by_text(' in line and '.nth(' in line and '.click()' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)"\)\.nth\((\d+)\)', line)
            if match:
                text = match.group(1)
                index = match.group(2)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}[{index}]',
                    value=text,
                    raw_code=line,
                    description=f'点击第{index}个文本为"{text}"的元素'
                )
        
        # 匹配 page.locator().filter().set_input_files()
        elif '.set_input_files(' in line:
            match = re.search(r'\.set_input_files\("([^"]+)"\)', line)
            if match:
                file_path = match.group(1)
                return ActionInfo(
                    action_type='upload',
                    value=file_path,
                    raw_code=line,
                    description=f'上传文件: {file_path}'
                )
        
        # 匹配 page.get_by_role("combobox", name="").click()
        elif 'page.get_by_role("combobox"' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("combobox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'combobox={name}',
                    raw_code=line,
                    description=f'点击下拉框: {name}'
                )
        
        # 匹配 page.get_by_role("spinbutton", name="").click()
        elif 'page.get_by_role("spinbutton"' in line:
            match = re.search(r'page\.get_by_role\("spinbutton",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'spinbutton={name}',
                    raw_code=line,
                    description=f'点击数字输入框: {name}'
                )
        
        # 匹配 page.get_by_role("link", name="").click()
        elif 'page.get_by_role("link"' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("link",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'link={name}',
                    raw_code=line,
                    description=f'点击链接: {name}'
                )
        
        # 匹配 page.get_by_role("row", name="").get_by_role("button").click()
        elif 'page.get_by_role("row"' in line:
            match = re.search(r'page\.get_by_role\("row",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'row={name}',
                    raw_code=line,
                    description=f'点击行: {name}'
                )
        
        # 匹配 page.get_by_role("menu").get_by_text().click()
        elif 'page.get_by_role("menu"' in line:
            match = re.search(r'page\.get_by_role\("menu"\)\.get_by_text\("([^"]+)"\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'menu={text}',
                    raw_code=line,
                    description=f'点击菜单项: {text}'
                )
        
        # 匹配 page.locator("span").filter().click()
        elif 'page.locator("span")' in line and '.filter(' in line:
            match = re.search(r'\.filter\(has_text=re\.compile\(r"([^"]+)"\)\)', line)
            if match:
                pattern = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'span[regex={pattern}]',
                    raw_code=line,
                    description=f'点击匹配正则的span元素: {pattern}'
                )
        
        # 匹配 page.locator("i").filter().click()
        elif 'page.locator("i")' in line and '.filter(' in line:
            match = re.search(r'\.filter\(has_text="([^"]+)"\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'i[has_text={text}]',
                    raw_code=line,
                    description=f'点击图标: {text}'
                )
        
        # 匹配 page.locator("a").filter().click()
        elif 'page.locator("a")' in line and '.filter(' in line:
            match = re.search(r'\.filter\(has_text="([^"]+)"\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'a[has_text={text}]',
                    raw_code=line,
                    description=f'点击链接: {text}'
                )
        
        # 匹配 page.locator("div").filter().nth().set_input_files()
        elif 'page.locator("div")' in line and '.filter(' in line:
            match = re.search(r'\.filter\(has_text="([^"]+)"\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'div[has_text={text}]',
                    raw_code=line,
                    description=f'点击div元素: {text}'
                )
        
        # 匹配 page.get_by_role("button", name="").click()
        elif 'page.get_by_role("button"' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("tab", name="").click()
        elif 'page.get_by_role("tab"' in line:
            match = re.search(r'page\.get_by_role\("tab",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'tab={name}',
                    raw_code=line,
                    description=f'点击标签页: {name}'
                )
        
        # 匹配 page.get_by_role("link", name="highlight").click()
        elif 'page.get_by_role("link"' in line:
            match = re.search(r'page\.get_by_role\("link",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'link={name}',
                    raw_code=line,
                    description=f'点击链接: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="").click()
        elif 'page.get_by_role("textbox"' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'textbox={name}',
                    raw_code=line,
                    description=f'点击文本框: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="").fill()
        elif 'page.get_by_role("textbox"' in line and '.fill(' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)\.fill\("([^"]+)"\)', line)
            if match:
                name = match.group(1)
                value = match.group(2)
                return ActionInfo(
                    action_type='fill',
                    locator=f'textbox={name}',
                    value=value,
                    raw_code=line,
                    description=f'在文本框"{name}"中输入: {value}'
                )
        
        # 匹配 page.get_by_role("radio", name="").check()
        elif 'page.get_by_role("radio"' in line:
            match = re.search(r'page\.get_by_role\("radio",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='check',
                    locator=f'radio={name}',
                    raw_code=line,
                    description=f'选择单选框: {name}'
                )
        
        # 匹配 page.get_by_role("checkbox", name="").check()
        elif 'page.get_by_role("checkbox"' in line:
            match = re.search(r'page\.get_by_role\("checkbox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='check',
                    locator=f'checkbox={name}',
                    raw_code=line,
                    description=f'勾选复选框: {name}'
                )
        
        # 匹配 page.locator(".ant-select-selection-overflow").click()
        elif 'page.locator(".ant-picker' in line or 'page.locator(".ant-select' in line:
            match = re.search(r'page\.locator\("([^"]+)"\)', line)
            if match:
                selector = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=selector,
                    raw_code=line,
                    description=f'点击元素: {selector}'
                )
        
        # 匹配 page.locator("div > .anticon > svg").click()
        elif 'page.locator(' in line and '.click()' in line:
            match = re.search(r'page\.locator\("([^"]+)"\)', line)
            if match:
                selector = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=selector,
                    raw_code=line,
                    description=f'点击元素: {selector}'
                )
        
        # 匹配 page.locator("#corporation").get_by_text().click()
        elif 'page.locator("#' in line and '.get_by_text(' in line:
            match = re.search(r'page\.locator\("#([^"]+)"\)\.get_by_text\("([^"]+)"\)', line)
            if match:
                container = match.group(1)
                text = match.group(2)
                return ActionInfo(
                    action_type='click',
                    locator=f'#{container} text={text}',
                    raw_code=line,
                    description=f'在#{container}中点击文本: {text}'
                )
        
        # 匹配 page.get_by_text("text", exact=True).click()
        elif 'page.get_by_text(' in line and 'exact=True' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)",\s*exact=True\)', line)
            if match:
                text = match.group(1)
                # 检查是否有 .nth()
                if '.nth(' in line:
                    nth_match = re.search(r'\.nth\((\d+)\)', line)
                    index = nth_match.group(1) if nth_match else '0'
                    locator = f'text={text}[exact][{index}]'
                else:
                    locator = f'text={text}[exact]'
                
                return ActionInfo(
                    action_type='click',
                    locator=locator,
                    value=text,
                    raw_code=line,
                    description=f'点击精确文本: {text}'
                )
        
        # 匹配 page.get_by_text("text").nth().click()
        elif 'page.get_by_text(' in line and '.nth(' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)"\)\.nth\((\d+)\)', line)
            if match:
                text = match.group(1)
                index = match.group(2)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}[{index}]',
                    value=text,
                    raw_code=line,
                    description=f'点击第{index}个文本为"{text}"的元素'
                )
        
        # 匹配 page.get_by_text("text").click()
        elif 'page.get_by_text(' in line and '.click()' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)"\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}',
                    value=text,
                    raw_code=line,
                    description=f'点击文本: {text}'
                )
        
        # 匹配 page.get_by_text("text").nth(1).click()
        elif 'page.get_by_text(' in line and '.nth(' in line and '.click()' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)"\)\.nth\((\d+)\)', line)
            if match:
                text = match.group(1)
                index = match.group(2)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}[{index}]',
                    value=text,
                    raw_code=line,
                    description=f'点击第{index}个文本为"{text}"的元素'
                )
        
        # 匹配 page.get_by_role("button", name="Close").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("link", name="").click()
        elif 'page.get_by_role("link"' in line:
            match = re.search(r'page\.get_by_role\("link",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'link={name}',
                    raw_code=line,
                    description=f'点击链接: {name}'
                )
        
        # 匹配 page.get_by_text("车辆管理").click()
        elif 'page.get_by_text(' in line and '.click()' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)"\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}',
                    value=text,
                    raw_code=line,
                    description=f'点击文本: {text}'
                )
        
        # 匹配 page.get_by_role("link", name="车辆列表").click()
        elif 'page.get_by_role("link"' in line:
            match = re.search(r'page\.get_by_role\("link",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'link={name}',
                    raw_code=line,
                    description=f'点击链接: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="设备号 :").click()
        elif 'page.get_by_role("textbox"' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'textbox={name}',
                    raw_code=line,
                    description=f'点击文本框: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="设备号 :").fill("869497052182449")
        elif 'page.get_by_role("textbox"' in line and '.fill(' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)\.fill\("([^"]+)"\)', line)
            if match:
                name = match.group(1)
                value = match.group(2)
                return ActionInfo(
                    action_type='fill',
                    locator=f'textbox={name}',
                    value=value,
                    raw_code=line,
                    description=f'在文本框"{name}"中输入: {value}'
                )
        
        # 匹配 page.get_by_role("button", name="查 询").click()
        elif 'page.get_by_role("button"' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("button", name="重 置").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("button", name="展开 up").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("checkbox", name="已关联").check()
        elif 'page.get_by_role("checkbox"' in line:
            match = re.search(r'page\.get_by_role\("checkbox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='check',
                    locator=f'checkbox={name}',
                    raw_code=line,
                    description=f'勾选复选框: {name}'
                )
        
        # 匹配 page.get_by_role("button", name="导 出").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("button", name="导出脱敏数据").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("checkbox", name="我确认导出敏感信息数据，并自行承担可能造成的后果").check()
        elif 'page.get_by_role("checkbox"' in line:
            match = re.search(r'page\.get_by_role\("checkbox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='check',
                    locator=f'checkbox={name}',
                    raw_code=line,
                    description=f'勾选复选框: {name}'
                )
        
        # 匹配 page.get_by_role("button", name="导出敏感数据").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("button", name="Close").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("link", name="设备列表").click()
        elif 'page.get_by_role("link"' in line:
            match = re.search(r'page\.get_by_role\("link",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'link={name}',
                    raw_code=line,
                    description=f'点击链接: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="IMEI号 :").click()
        elif 'page.get_by_role("textbox"' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'textbox={name}',
                    raw_code=line,
                    description=f'点击文本框: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="IMEI号 :").fill("869497052182449")
        elif 'page.get_by_role("textbox"' in line and '.fill(' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)\.fill\("([^"]+)"\)', line)
            if match:
                name = match.group(1)
                value = match.group(2)
                return ActionInfo(
                    action_type='fill',
                    locator=f'textbox={name}',
                    value=value,
                    raw_code=line,
                    description=f'在文本框"{name}"中输入: {value}'
                )
        
        # 匹配 page.get_by_role("button", name="查 询").click()
        elif 'page.get_by_role("button"' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("button", name="重 置").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="服务时间 :").click()
        elif 'page.get_by_role("textbox"' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'textbox={name}',
                    raw_code=line,
                    description=f'点击文本框: {name}'
                )
        
        # 匹配 page.get_by_role("button", name="上个月 (翻页上键)").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_text("1", exact=True).nth(1).click()
        elif 'page.get_by_text(' in line and 'exact=True' in line and '.nth(' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)",\s*exact=True\)\.nth\((\d+)\)', line)
            if match:
                text = match.group(1)
                index = match.group(2)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}[exact][{index}]',
                    value=text,
                    raw_code=line,
                    description=f'点击第{index}个精确文本: {text}'
                )
        
        # 匹配 page.get_by_text("28").nth(3).click()
        elif 'page.get_by_text(' in line and '.nth(' in line and '.click()' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)"\)\.nth\((\d+)\)', line)
            if match:
                text = match.group(1)
                index = match.group(2)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}[{index}]',
                    value=text,
                    raw_code=line,
                    description=f'点击第{index}个文本为"{text}"的元素'
                )
        
        # 匹配 page.get_by_role("button", name="入库管理").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("combobox", name="* 4S店名称 :").click()
        elif 'page.get_by_role("combobox"' in line:
            match = re.search(r'page\.get_by_role\("combobox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'combobox={name}',
                    raw_code=line,
                    description=f'点击下拉框: {name}'
                )
        
        # 匹配 page.get_by_text("测试店铺").nth(1).click()
        elif 'page.get_by_text(' in line and '.nth(' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)"\)\.nth\((\d+)\)', line)
            if match:
                text = match.group(1)
                index = match.group(2)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}[{index}]',
                    value=text,
                    raw_code=line,
                    description=f'点击第{index}个文本为"{text}"的元素'
                )
        
        # 匹配 page.get_by_role("textbox", name="设备号 :").click()
        elif 'page.get_by_role("textbox"' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'textbox={name}',
                    raw_code=line,
                    description=f'点击文本框: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="设备号 :").fill("869497052182449 573970116302449")
        elif 'page.get_by_role("textbox"' in line and '.fill(' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)\.fill\("([^"]+)"\)', line)
            if match:
                name = match.group(1)
                value = match.group(2)
                return ActionInfo(
                    action_type='fill',
                    locator=f'textbox={name}',
                    value=value,
                    raw_code=line,
                    description=f'在文本框"{name}"中输入: {value}'
                )
        
        # 匹配 page.get_by_role("button", name="添加入库").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("button", name="Close").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="页").click()
        elif 'page.get_by_role("textbox"' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'textbox={name}',
                    raw_code=line,
                    description=f'点击文本框: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="页").fill("3")
        elif 'page.get_by_role("textbox"' in line and '.fill(' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)\.fill\("([^"]+)"\)', line)
            if match:
                name = match.group(1)
                value = match.group(2)
                return ActionInfo(
                    action_type='fill',
                    locator=f'textbox={name}',
                    value=value,
                    raw_code=line,
                    description=f'在文本框"{name}"中输入: {value}'
                )
        
        # 匹配 page.get_by_role("textbox", name="页").press("Enter")
        elif 'page.get_by_role("textbox"' in line and '.press(' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)\.press\("([^"]+)"\)', line)
            if match:
                name = match.group(1)
                key = match.group(2)
                return ActionInfo(
                    action_type='press',
                    locator=f'textbox={name}',
                    value=key,
                    raw_code=line,
                    description=f'在文本框"{name}"中按下按键: {key}'
                )
        
        # 匹配 page.get_by_role("link", name="信息异常的用户").click()
        elif 'page.get_by_role("link"' in line:
            match = re.search(r'page\.get_by_role\("link",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'link={name}',
                    raw_code=line,
                    description=f'点击链接: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="IMEI号 :").click()
        elif 'page.get_by_role("textbox"' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'textbox={name}',
                    raw_code=line,
                    description=f'点击文本框: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="用户注册的手机 :").click()
        elif 'page.get_by_role("textbox"' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'textbox={name}',
                    raw_code=line,
                    description=f'点击文本框: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="用户注册的手机 :").fill("18108047253")
        elif 'page.get_by_role("textbox"' in line and '.fill(' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)\.fill\("([^"]+)"\)', line)
            if match:
                name = match.group(1)
                value = match.group(2)
                return ActionInfo(
                    action_type='fill',
                    locator=f'textbox={name}',
                    value=value,
                    raw_code=line,
                    description=f'在文本框"{name}"中输入: {value}'
                )
        
        # 匹配 page.get_by_role("link", name="设备授权").click()
        elif 'page.get_by_role("link"' in line:
            match = re.search(r'page\.get_by_role\("link",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'link={name}',
                    raw_code=line,
                    description=f'点击链接: {name}'
                )
        
        # 匹配 page.get_by_role("combobox", name="激活状态 :").click()
        elif 'page.get_by_role("combobox"' in line:
            match = re.search(r'page\.get_by_role\("combobox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'combobox={name}',
                    raw_code=line,
                    description=f'点击下拉框: {name}'
                )
        
        # 匹配 page.get_by_text("激活", exact=True).click()
        elif 'page.get_by_text(' in line and 'exact=True' in line and '.click()' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)",\s*exact=True\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}[exact]',
                    value=text,
                    raw_code=line,
                    description=f'点击精确文本: {text}'
                )
        
        # 匹配 page.locator("#corporation").get_by_text("激活", exact=True).click()
        elif 'page.locator("#' in line and '.get_by_text(' in line and 'exact=True' in line:
            match = re.search(r'page\.locator\("#([^"]+)"\)\.get_by_text\("([^"]+)",\s*exact=True\)', line)
            if match:
                container = match.group(1)
                text = match.group(2)
                return ActionInfo(
                    action_type='click',
                    locator=f'#{container} text={text}[exact]',
                    raw_code=line,
                    description=f'在#{container}中点击精确文本: {text}'
                )
        
        # 匹配 page.get_by_text("未激活").click()
        elif 'page.get_by_text(' in line and '.click()' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)"\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}',
                    value=text,
                    raw_code=line,
                    description=f'点击文本: {text}'
                )
        
        # 匹配 page.get_by_role("combobox", name="是否授权 :").click()
        elif 'page.get_by_role("combobox"' in line:
            match = re.search(r'page\.get_by_role\("combobox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'combobox={name}',
                    raw_code=line,
                    description=f'点击下拉框: {name}'
                )
        
        # 匹配 page.get_by_text("是", exact=True).click()
        elif 'page.get_by_text(' in line and 'exact=True' in line and '.click()' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)",\s*exact=True\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}[exact]',
                    value=text,
                    raw_code=line,
                    description=f'点击精确文本: {text}'
                )
        
        # 匹配 page.locator("#corporation").get_by_text("是", exact=True).click()
        elif 'page.locator("#' in line and '.get_by_text(' in line and 'exact=True' in line:
            match = re.search(r'page\.locator\("#([^"]+)"\)\.get_by_text\("([^"]+)",\s*exact=True\)', line)
            if match:
                container = match.group(1)
                text = match.group(2)
                return ActionInfo(
                    action_type='click',
                    locator=f'#{container} text={text}[exact]',
                    raw_code=line,
                    description=f'在#{container}中点击精确文本: {text}'
                )
        
        # 匹配 page.get_by_text("否", exact=True).click()
        elif 'page.get_by_text(' in line and 'exact=True' in line and '.click()' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)",\s*exact=True\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}[exact]',
                    value=text,
                    raw_code=line,
                    description=f'点击精确文本: {text}'
                )
        
        # 匹配 page.get_by_role("button", name="设备批量授权").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="设备号 :").click()
        elif 'page.get_by_role("textbox"' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'textbox={name}',
                    raw_code=line,
                    description=f'点击文本框: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="设备号 :").fill("869497052182449")
        elif 'page.get_by_role("textbox"' in line and '.fill(' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)\.fill\("([^"]+)"\)', line)
            if match:
                name = match.group(1)
                value = match.group(2)
                return ActionInfo(
                    action_type='fill',
                    locator=f'textbox={name}',
                    value=value,
                    raw_code=line,
                    description=f'在文本框"{name}"中输入: {value}'
                )
        
        # 匹配 page.get_by_role("button", name="添加授权").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("button", name="Close").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("menu").get_by_text("线索管理").click()
        elif 'page.get_by_role("menu"' in line:
            match = re.search(r'page\.get_by_role\("menu"\)\.get_by_text\("([^"]+)"\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'menu={text}',
                    raw_code=line,
                    description=f'点击菜单项: {text}'
                )
        
        # 匹配 page.get_by_text("所有", exact=True).click()
        elif 'page.get_by_text(' in line and 'exact=True' in line and '.click()' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)",\s*exact=True\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}[exact]',
                    value=text,
                    raw_code=line,
                    description=f'点击精确文本: {text}'
                )
        
        # 匹配 page.get_by_role("textbox", name="车主手机 :").click()
        elif 'page.get_by_role("textbox"' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'textbox={name}',
                    raw_code=line,
                    description=f'点击文本框: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="车主手机 :").fill("18108047253")
        elif 'page.get_by_role("textbox"' in line and '.fill(' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)\.fill\("([^"]+)"\)', line)
            if match:
                name = match.group(1)
                value = match.group(2)
                return ActionInfo(
                    action_type='fill',
                    locator=f'textbox={name}',
                    value=value,
                    raw_code=line,
                    description=f'在文本框"{name}"中输入: {value}'
                )
        
        # 匹配 page.locator("i").filter(has_text="未分配").click()
        elif 'page.locator("i")' in line and '.filter(' in line:
            match = re.search(r'\.filter\(has_text="([^"]+)"\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'i[has_text={text}]',
                    raw_code=line,
                    description=f'点击图标: {text}'
                )
        
        # 匹配 page.get_by_text("已删除").click()
        elif 'page.get_by_text(' in line and '.click()' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)"\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}',
                    value=text,
                    raw_code=line,
                    description=f'点击文本: {text}'
                )
        
        # 匹配 page.get_by_text("我的").click()
        elif 'page.get_by_text(' in line and '.click()' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)"\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}',
                    value=text,
                    raw_code=line,
                    description=f'点击文本: {text}'
                )
        
        # 匹配 page.get_by_text("我已关闭").click()
        elif 'page.get_by_text(' in line and '.click()' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)"\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}',
                    value=text,
                    raw_code=line,
                    description=f'点击文本: {text}'
                )
        
        # 匹配 page.get_by_text("所有", exact=True).click()
        elif 'page.get_by_text(' in line and 'exact=True' in line and '.click()' in line:
            match = re.search(r'page\.get_by_text\("([^"]+)",\s*exact=True\)', line)
            if match:
                text = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'text={text}[exact]',
                    value=text,
                    raw_code=line,
                    description=f'点击精确文本: {text}'
                )
        
        # 匹配 page.get_by_role("row", name="事故 387天 01/12 14:14:37 距离：0.").get_by_role("button").click()
        elif 'page.get_by_role("row"' in line:
            match = re.search(r'page\.get_by_role\("row",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'row={name}',
                    raw_code=line,
                    description=f'点击行: {name}'
                )
        
        # 匹配 page.get_by_role("button", name="展开 up").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 匹配 page.get_by_role("textbox", name="设备号 :").click()
        elif 'page.get_by_role("textbox"' in line and '.click()' in line:
            match = re.search(r'page\.get_by_role\("textbox",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'textbox={name}',
                    raw_code=line,
                    description=f'点击文本框: {name}'
                )
        
        # 匹配 page.get_by_role("button", name="close-circle").click()
        elif 'page.get_by_role("button"' in line:
            match = re.search(r'page\.get_by_role\("button",\s*name="([^"]+)"\)', line)
            if match:
                name = match.group(1)
                return ActionInfo(
                    action_type='click',
                    locator=f'button={name}',
                    raw_code=line,
                    description=f'点击按钮: {name}'
                )
        
        # 未匹配的操作，记录原始代码
        return ActionInfo(
            action_type='unknown',
            raw_code=line,
            description=f'未知操作: {line}'
        )


class PageObjectGenerator:
    """Page对象生成器"""
    
    def __init__(self, page_name: str, scenarios: List[ScenarioInfo]):
        self.page_name = page_name
        self.scenarios = scenarios
        self.locators: Dict[str, str] = {}
    
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
        
        for scenario in self.scenarios:
            for action in scenario.actions:
                if action.locator:
                    locator_key = self._generate_locator_key(action.locator, locator_count)
                    if locator_key not in self.locators:
                        self.locators[locator_key] = action.locator
    
    def _generate_locator_key(self, locator: str, count_dict: Dict) -> str:
        """
        生成定位器变量名
        """
        # 简化定位器名称
        if locator.startswith('role='):
            role = locator.split('=')[1]
            key = f'locator_{role}'
        elif locator.startswith('text='):
            text = locator.split('=')[1].split('[')[0]
            key = f'locator_{text}'
        elif locator.startswith('textbox='):
            name = locator.split('=')[1]
            key = f'locator_{name}'
        elif locator.startswith('button='):
            name = locator.split('=')[1]
            key = f'locator_{name}'
        elif locator.startswith('link='):
            name = locator.split('=')[1]
            key = f'locator_{name}'
        elif locator.startswith('combobox='):
            name = locator.split('=')[1]
            key = f'locator_{name}'
        elif locator.startswith('checkbox='):
            name = locator.split('=')[1]
            key = f'locator_{name}'
        elif locator.startswith('radio='):
            name = locator.split('=')[1]
            key = f'locator_{name}'
        elif locator.startswith('tab='):
            name = locator.split('=')[1]
            key = f'locator_{name}'
        elif locator.startswith('#'):
            key = f'locator_{locator[1:]}'
        elif locator.startswith('.'):
            key = f'locator_{locator[1:].replace(".", "_")}'
        else:
            key = 'locator_element'
        
        # 清理名称
        key = re.sub(r'[^a-zA-Z0-9_]', '_', key)
        key = re.sub(r'_+', '_', key).strip('_')
        
        count_dict[key] = count_dict.get(key, 0) + 1
        if count_dict[key] > 1:
            return f'{key}_{count_dict[key]}'
        return key
    
    def _generate_locators(self) -> List[str]:
        """
        生成定位器定义
        """
        lines = ['    # 定位器']
        for locator_name, locator_value in self.locators.items():
            lines.append(f'    {locator_name} = "{locator_value}"')
        return lines
    
    def _generate_methods(self) -> List[str]:
        """
        生成操作方法
        """
        lines = []
        
        for scenario in self.scenarios:
            method_name = self._generate_method_name(scenario.name)
            lines.append(f'    def {method_name}(self):')
            lines.append(f'        """')
            lines.append(f'        {scenario.description}')
            lines.append(f'        """')
            
            for action in scenario.actions:
                method_line = self._generate_action_method(action)
                if method_line:
                    lines.append(f'        {method_line}')
            
            lines.append(f'        logger.info("{method_name}执行完成")')
            lines.append('')
        
        return lines
    
    def _generate_method_name(self, scenario_name: str) -> str:
        """
        生成方法名
        """
        name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '_', scenario_name)
        name = re.sub(r'_+', '_', name).strip('_')
        return f'{name}_flow'
    
    def _generate_action_method(self, action: ActionInfo) -> str:
        """
        生成操作方法代码
        """
        if action.action_type == 'navigate':
            return f'self.visit("{action.value}")'
        elif action.action_type == 'click':
            locator_var = self._find_locator_var(action.locator)
            return f'self.click(self.{locator_var})'
        elif action.action_type == 'fill':
            locator_var = self._find_locator_var(action.locator)
            return f'self.input(self.{locator_var}, "{action.value}")'
        elif action.action_type == 'type':
            locator_var = self._find_locator_var(action.locator)
            return f'self.type(self.{locator_var}, "{action.value}")'
        elif action.action_type == 'check':
            locator_var = self._find_locator_var(action.locator)
            return f'self.check(self.{locator_var})'
        elif action.action_type == 'uncheck':
            locator_var = self._find_locator_var(action.locator)
            return f'self.uncheck(self.{locator_var})'
        elif action.action_type == 'hover':
            locator_var = self._find_locator_var(action.locator)
            return f'self.hover(self.{locator_var})'
        elif action.action_type == 'focus':
            locator_var = self._find_locator_var(action.locator)
            return f'self.focus(self.{locator_var})'
        elif action.action_type == 'clear':
            locator_var = self._find_locator_var(action.locator)
            return f'self.clear(self.{locator_var})'
        elif action.action_type == 'select_option':
            locator_var = self._find_locator_var(action.locator)
            return f'self.select_option(self.{locator_var}, "{action.value}")'
        elif action.action_type == 'upload':
            return f'self.upload_file("{action.locator}", "{action.value}")'
        elif action.action_type == 'press':
            locator_var = self._find_locator_var(action.locator)
            return f'# TODO: 需要手动实现键盘操作: page.press("{locator_var}", "{action.value}")'
        elif action.action_type == 'unknown':
            return f'# TODO: {action.raw_code}'
        return ''
    
    def _find_locator_var(self, locator: str) -> str:
        """
        查找定位器变量名
        """
        for locator_name, locator_value in self.locators.items():
            if locator_value == locator:
                return locator_name
        return 'locator_element'
    
    def _get_page_filename(self) -> str:
        """
        获取Page文件名
        """
        name = re.sub(r'([A-Z])', r'_\1', self.page_name).lower()
        return f'{name}_page.py'


class TestCaseGenerator:
    """测试用例生成器"""
    
    def __init__(self, page_name: str, scenarios: List[ScenarioInfo]):
        self.page_name = page_name
        self.scenarios = scenarios
    
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
        
        for scenario in self.scenarios:
            method_name = self._generate_method_name(scenario.name)
            lines.append(f'    def test_{method_name}(self):')
            lines.append(f'        """')
            lines.append(f'        {scenario.description}')
            lines.append(f'        """')
            lines.append(f'        self.{self.page_name.lower()}_page.{method_name}_flow()')
            lines.append('')
        
        return lines
    
    def _generate_method_name(self, scenario_name: str) -> str:
        """
        生成方法名
        """
        name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '_', scenario_name)
        name = re.sub(r'_+', '_', name).strip('_')
        return name
    
    def _get_test_filename(self) -> str:
        """
        获取测试文件名
        """
        name = re.sub(r'([A-Z])', r'_\1', self.page_name).lower()
        return name
    
    def _get_page_import(self) -> str:
        """
        获取Page导入路径
        """
        name = re.sub(r'([A-Z])', r'_\1', self.page_name).lower()
        return f'{name}/{name}_page'


class RawScriptConverter:
    """原始脚本转换器主类"""
    
    def __init__(self, input_file: str, output_dir: str, page_name: str):
        self.input_file = input_file
        self.output_dir = output_dir
        self.page_name = page_name
        self.parser = None
        self.scenarios = []
    
    def convert(self):
        """
        执行转换
        """
        logger.info(f"开始转换原始录制脚本: {self.input_file}")
        
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
        self.parser = RawScriptParser(self.script_content)
        self.scenarios = self.parser.parse()
        logger.info(f"解析完成，共发现 {len(self.scenarios)} 个测试场景")
    
    def _generate_files(self):
        """
        生成文件
        """
        os.makedirs(self.output_dir, exist_ok=True)
        
        page_generator = PageObjectGenerator(self.page_name, self.scenarios)
        page_code = page_generator.generate()
        page_file = os.path.join(self.output_dir, f'{self._get_page_filename()}')
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(page_code)
        logger.info(f"Page对象已生成: {page_file}")
        
        test_generator = TestCaseGenerator(self.page_name, self.scenarios)
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
        description='Playwright原始录制脚本转换工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python raw_script_converter.py --input clue.md --output ./output --page-name Clue
    
    转换后的文件结构:
        output/
          ├── clue_page.py      # Page对象
          └── test_clue.py      # 测试用例
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='输入的录制脚本文件路径（支持.md格式）'
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
    
    converter = RawScriptConverter(
        input_file=args.input,
        output_dir=args.output,
        page_name=args.page_name
    )
    
    converter.convert()


if __name__ == '__main__':
    main()
