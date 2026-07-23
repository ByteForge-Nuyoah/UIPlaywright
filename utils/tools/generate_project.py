# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : generate_project.py
# @Software: PyCharm
# @Desc    : 项目脚手架 - 按项目名生成多项目登录骨架

"""
按项目名在 projects/<name>/ 下生成登录骨架，包含：
  project_settings.py / data/login_data.yaml / interfaces/<name>_login.yml（项目根，各项目按文件名隔离）
  pages/login_page.py / testcases/conftest.py / testcases/ui/test_login.py / testcases/api/test_login_api.py

用法：
  python utils/tools/generate_project.py <项目名>

生成后还需手动：
  1. 填 pages/login_page.py 的定位器与登录页路径
  2. 填 项目根 interfaces/<name>_login.yml 的 url / payload / 断言
  3. 在 config/env/.env 配置 <NAME>_ADMIN_USER / <NAME>_ADMIN_PASSWORD
  4. 跑通：python run.py -project <项目名> -env test -m login
"""

import os
import re
import sys
import shutil

# 项目根目录（本脚本位于 utils/tools/generate_project.py）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
# 通用项目级 conftest 的来源（已去项目名硬编码，可零改动复用到任意项目）
REFERENCE_CONFTEST = os.path.join(PROJECTS_DIR, "clue", "testcases", "conftest.py")


# ------------------------------------ 模板（用 __NAME__ 等占位符，render() 统一替换）------------------------------------#
PROJECT_SETTINGS_TPL = '''# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : project_settings.py
# @Software: PyCharm
# @Desc    : __NAME__ 项目配置

import os

# ------------------------------------ 测试数据配置 ----------------------------------------------------#
ENV_VARS = {
    "common": {
        "report_title": "UI自动化测试报告-__NAME__",
        "project_name": "__NAME__System",
        "tester": "会飞的🐟",
        "department": "成都研发后台",
        "env": "test",
        # API 登录接口配置（供 testcases/conftest.py 的 api_session_setup 使用）；
        # file 相对项目根 interfaces/ 目录，var_map 把 GLOBAL_VARS 字段映射成接口 payload 变量名
        "login_api": {
            "file": "__NAME___login.yml",
            "key": "__NAME___login",
            # TODO: 按实际登录接口 payload 字段调整 var_map（左=接口字段名，右=GLOBAL_VARS 键）
            "var_map": {
                "username": "admin_user_name",
                "password": "admin_user_password",
            },
            # TODO: 接口需要的固定参数
            "extra_vars": {},
        },
    },
    "test": {
        # TODO: 测试环境前端域名
        "url": "https://__NAME__-dev.example.com",
        # TODO: 测试环境接口域名
        "host": "https://__NAME__api-dev.example.com",
        # 管理员账号（必须通过环境变量或本地 .env 注入，避免代码中保留默认明文账号密码）
        "admin_user_name": os.getenv("__ADMIN_USER_ENV__", ""),
        "admin_user_password": os.getenv("__ADMIN_PASSWORD_ENV__", ""),
    },
    "prod": {
        # TODO: 待补 prod 环境域名
        "url": "https://__NAME__.example.com",
        "host": "https://__NAME__api.example.com",
        "admin_user_name": os.getenv("__ADMIN_USER_ENV__", ""),
        "admin_user_password": os.getenv("__ADMIN_PASSWORD_ENV__", ""),
    },
}
'''

LOGIN_YML_TPL = '''-
   id: __NAME___login
   title: __NAME__ 登录接口
   url: /api/__NAME__/v1/login
   method: POST
   headers:
    Content-Type: application/json; charset=utf-8;
    # Origin 跟随环境变化；后端如对 Origin 做白名单校验也能通过
    Origin: "${url}"
   request_type: json
   payload:
     # TODO: 按实际登录接口 payload 调整字段
     username: "${username}"
     password: "${password}"
   assert_response:
     status_code: 200
     # TODO: 按实际返回补充 code / 字段断言，例如：
     # assertCode:
     #   message: 断言接口返回码为0
     #   expect_value: 0
     #   assert_type: ==
     #   type_jsonpath: $.code
   assert_sql:
   extract:
'''

LOGIN_PAGE_TPL = '''# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : login_page.py
# @Software: PyCharm
# @Desc    : __NAME__ 登录页

import allure
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from utils.base_utils.base_page import BasePage


class LoginPage(BasePage):
    """
    __NAME__ 登录页。
    """
    # TODO: 打开登录页，用开发者工具确认以下定位器
    locator_page_username = "id=username"                       # TODO: 用户名输入框定位器
    locator_page_password = "id=password"                       # TODO: 密码输入框定位器
    locator_page_login_btn = "xpath=//button[@type='submit']"   # TODO: 登录按钮定位器

    @allure.step("访问 __NAME__ 登录页面")
    def navigate(self, timeout: int = 30):
        """
        访问登录页面
        # TODO: 确认登录页路径，可能是 /login 或根路径重定向到登录页
        """
        self.page.goto("/login", timeout=timeout)
        self.wait_for_load_state()
        return self

    @allure.step("网页登录：输入用户名：{login}")
    def input_username_on_page(self, login):
        self.input(locator=self.locator_page_username, text=login)
        return self

    @allure.step("网页登录：输入密码：{password}")
    def input_password_on_page(self, password):
        self.input(locator=self.locator_page_password, text=password)
        return self

    @allure.step("网页登录：点击【登录】按钮，提交登录表单")
    def submit_login_on_page(self):
        self.click(locator=self.locator_page_login_btn)
        return self

    # --------------------- 流程 -------------------------------------
    @allure.step("网页登录：输入用户名：{login}，输入密码：{password}，点击【登录】按钮，提交登录表单")
    def login_on_page_flow(self, login, password):
        """
        完整登录操作 --> 输入用户名 + 密码 -> 提交表单。
        成功则 URL 离开登录页；失败仍停留。

        :return: self（暂未建 home_page，调用方直接用 self.page 继续操作）
        """
        (self
         .input_username_on_page(login)
         .input_password_on_page(password)
         .submit_login_on_page())
        try:
            self.page.wait_for_url(lambda url: "/login" not in url, timeout=5000)
        except PlaywrightTimeoutError:
            pass
        return self
'''

TEST_LOGIN_TPL = '''# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_login.py
# @Software: PyCharm
# @Desc    : __NAME__ 登录功能测试用例

import os

import pytest
from loguru import logger
from playwright.sync_api import Page

from pages.login_page import LoginPage
from utils.files_utils.yaml_handle import YamlHandle


@pytest.mark.login
# 登录用例本身要验证 UI 登录流程，必须使用未登录的全新上下文，
# 通过 marker 覆盖项目级 conftest 注入的 storage_state。
@pytest.mark.browser_context_args(storage_state=None)
class TestLogin:
    """__NAME__ 登录"""
    # 动态获取 yaml 数据文件路径
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "login_data.yaml")
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        logger.info("\\n\\n---------------Start: 开始测试-------------")
        self.login_page = LoginPage(page)
        self.login_page.navigate()
        yield
        # 清除登录 cookies，避免影响其他登录用例
        page.context.clear_cookies()

    @pytest.mark.parametrize("case", cases["user_with_phone_page"], ids=lambda x: x["title"])
    def test_login_user(self, case):
        """
        网页登录：输入用户名密码并提交。
        TODO: 定位器（login_page.py）与登录后跳转路径填好后，按实际情况补充成功/失败断言
              （可参照 projects/clue/testcases/test_login.py 的写法）
        """
        login = case.get("login")
        password = case.get("password")
        self.login_page.login_on_page_flow(login=login, password=password)
        # TODO: 成功用例断言跳转到首页；失败用例断言仍停留在登录页
        assert self.login_page.page is not None
'''

TEST_LOGIN_API_TPL = '''# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_login_api.py
# @Software: PyCharm
# @Desc    : __NAME__ 登录接口用例

import os
import pytest
from playwright.sync_api import Playwright
from config.global_vars import GLOBAL_VARS
from config.config_path import BASE_DIR
from utils.base_utils.request_control import RequestControl

INTERFACE_DIR = os.path.join(BASE_DIR, "interfaces")


@pytest.mark.api
class TestLoginApi:
    """__NAME__ 登录接口"""

    def test_login_api(self, playwright: Playwright):
        """
        验证 __NAME___login.yml 可被 RequestControl 正常加载执行，
        并确认 headers.Origin 中的 ${url} 已按当前环境替换。
        """
        api_request_context = playwright.request.new_context(base_url=GLOBAL_VARS["host"])
        try:
            result = RequestControl(api_request_context=api_request_context).api_request_flow(
                api_file_path=os.path.join(INTERFACE_DIR, "__NAME___login.yml"),
                key="__NAME___login",
                global_var={
                    "url": GLOBAL_VARS["url"],
                    "username": GLOBAL_VARS["admin_user_name"],
                    "password": GLOBAL_VARS["admin_user_password"],
                },
            )
            assert result["headers"]["Origin"] == GLOBAL_VARS["url"]
        finally:
            api_request_context.dispose()
'''

LOGIN_DATA_TPL = '''# 场景：__NAME__ 登录
user_with_phone_page:
  - title: "网页登录，正确用户名和密码登录成功"
    login: "${admin_user_name}"
    password: "${admin_user_password}"
    run: true

  # - title: "网页登录，错误密码登录失败"
  #   login: "${admin_user_name}"
  #   password: "wrong_password"
  #   run: true
'''

INIT_TPL = '''# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : __init__.py
# @Software: PyCharm
# @Desc: __NAME__ 包
'''


def render(tpl, name):
    """替换模板占位符。用 replace 而非 format，避免模板里的 {}/`${}` 被误解析。"""
    return (tpl
            .replace("__NAME__", name)
            .replace("__ADMIN_USER_ENV__", f"{name.upper()}_ADMIN_USER")
            .replace("__ADMIN_PASSWORD_ENV__", f"{name.upper()}_ADMIN_PASSWORD"))


def print_next_steps(name):
    env_user = f"{name.upper()}_ADMIN_USER"
    env_pwd = f"{name.upper()}_ADMIN_PASSWORD"
    print(f"""
项目 {name} 骨架已生成：projects/{name}/

接下来手动完成：
  1. projects/{name}/pages/login_page.py      填定位器 + 登录页路径（TODO 处）
  2. interfaces/{name}_login.yml  填 url / payload / 断言（TODO 处）
  3. config/env/.env                           追加 {env_user}=xxx  {env_pwd}=xxx
  4. （可选）pytest.ini                         为业务用例补充 markers
  5. 跑通登录骨架：
       python run.py -project {name} -env test -m login
""")


def main():
    if len(sys.argv) != 2:
        print("用法: python utils/tools/generate_project.py <项目名>")
        sys.exit(1)

    name = sys.argv[1].strip()
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", name):
        print(f"项目名非法: {name!r}（需以字母开头，仅含字母/数字/下划线）")
        sys.exit(1)

    project_dir = os.path.join(PROJECTS_DIR, name)
    if os.path.exists(project_dir):
        print(f"项目已存在: {project_dir}（如需重新生成请先删除）")
        sys.exit(1)
    if not os.path.exists(REFERENCE_CONFTEST):
        print(f"参考 conftest 不存在: {REFERENCE_CONFTEST}（脚手架依赖 clue 的通用 conftest）")
        sys.exit(1)

    # 1. 建目录（interfaces 在项目根，不在项目目录下；testcases 下分 api/ui 子目录）
    for sub in ["data", "pages", "testcases", "testcases/api", "testcases/ui"]:
        os.makedirs(os.path.join(project_dir, sub), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "interfaces"), exist_ok=True)

    # 2. 拷贝通用项目级 conftest（已去硬编码，零改动复用）
    shutil.copyfile(REFERENCE_CONFTEST, os.path.join(project_dir, "testcases", "conftest.py"))
    print(f"生成: projects/{name}/testcases/conftest.py  (拷贝自 clue)")

    # 3. 渲染模板文件（写到项目目录）
    writes = [
        ("project_settings.py", render(PROJECT_SETTINGS_TPL, name)),
        ("pages/login_page.py", render(LOGIN_PAGE_TPL, name)),
        ("testcases/ui/test_login.py", render(TEST_LOGIN_TPL, name)),
        ("testcases/api/test_login_api.py", render(TEST_LOGIN_API_TPL, name)),
        ("data/login_data.yaml", render(LOGIN_DATA_TPL, name)),
        ("pages/__init__.py", render(INIT_TPL, name)),
        ("testcases/__init__.py", render(INIT_TPL, name)),
        ("testcases/api/__init__.py", render(INIT_TPL, name)),
        ("testcases/ui/__init__.py", render(INIT_TPL, name)),
    ]
    for rel, content in writes:
        path = os.path.join(project_dir, rel)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"生成: projects/{name}/{rel}")

    # 4. 接口定义写到项目根 interfaces/<name>_login.yml（各项目按文件名隔离）
    interface_path = os.path.join(BASE_DIR, "interfaces", f"{name}_login.yml")
    with open(interface_path, "w", encoding="utf-8") as f:
        f.write(render(LOGIN_YML_TPL, name))
    print(f"生成: interfaces/{name}_login.yml")

    print_next_steps(name)


if __name__ == "__main__":
    main()
