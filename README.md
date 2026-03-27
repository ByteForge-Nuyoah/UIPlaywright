# UI Automation Framework (Playwright + Pytest)

基于 Playwright + Pytest的UI自动化测试框架。支持多项目管理、多环境配置、数据驱动、Allure 可视化报告以及 CI/CD 流水线集成。

## 一、核心特性

- **多项目架构**：一套框架支持多个业务线的自动化测试。
- **环境隔离**：支持 `test` / `live` 等多环境切换，敏感配置通过 `.env` 管理。
- **POM 设计模式**：页面对象模型 (Page Object Model) 实现业务逻辑与测试脚本分离。
- **增强断言体系**：基于 `expect` 封装了 `assert_text_contains`、`assert_element_visible` 等智能等待断言，告别不稳定 `sleep`。
- **数据驱动**：支持 YAML 数据文件分离，实现测试数据与代码解耦。
- **可视化报告**：集成 Allure Report，自动捕获失败截图、日志和详细步骤。
- **CI/CD 就绪**：内置 GitHub Actions、GitLab CI、Gitee Go 配置文件。
- **脚本转换工具**：支持将 Playwright 录制脚本自动转换为 POM 格式。

## 二、项目结构

```text
uiPlaywright/
├── config/                 # 全局配置中心
│   ├── env/                # 环境变量目录
│   │   ├── .env            # 敏感配置 (用户手动创建)
│   │   └── .env.example    # 配置模板
│   ├── settings.py         # 配置加载器
│   └── ...
├── projects/               # 业务项目目录 (多租户支持)
│   └── clue/               # 示例项目：线索管理系统
│       ├── data/                 # 测试数据 (YAML)
│       │   ├── login_data.yaml
│       │   ├── account_data.yaml
│       │   └── data_page.yaml
│       ├── pages/                # 页面对象 (封装页面元素与操作)
│       │   ├── login_page.py
│       │   ├── account/
│       │   │   └── account_page.py
│       │   └── data/
│       │       └── data_page.py
│       ├── testcases/            # 测试用例 (Pytest)
│       │   ├── test_login.py
│       │   ├── test_create_account.py
│       │   └── test_data_page.py
│       ├── interfaces/           # 接口自动化定义 (YAML)
│       │   └── clue_login.yml
│       └── project_settings.py   # 项目特定配置
├── utils/                  # 核心工具库
│   ├── base_utils/         # 基础页面类 (BasePage)
│   │   └── base_page.py
│   ├── data_utils/         # 数据处理工具 (YAML, Random)
│   ├── notify_utils/       # 通知工具 (Email, DingTalk, WeCom)
│   └── tools/              # 实用工具
│       ├── script_converter.py    # 录制脚本转换器 (完整pytest脚本)
│       └── raw_script_converter.py # 原始操作序列转换器
├── outputs/                # 测试产出物
│   ├── logs/               # 运行日志
│   └── report/             # Allure 测试报告
│       ├── allure_html/
│       └── allure_results/
├── run.py                  # 框架统一执行入口
├── requirements.txt        # 项目依赖清单
├── pytest.ini              # Pytest 配置与标记声明
└── .github/                # CI/CD 配置
```

## 三、快速开始

### 1. 环境准备

- **Python**: 推荐 Python 3.9+
- **操作系统**: macOS / Linux / Windows

### 2. 安装依赖

```bash
# 1. 创建并激活虚拟环境 (推荐)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 2. 安装项目依赖
pip install -r requirements.txt

# 3. 安装 Playwright 浏览器驱动
playwright install
```

### 3. 配置文件

复制示例配置文件并按需修改：

```bash
cp config/env/.env.example config/env/.env
```

## 四、运行测试

框架使用 `run.py` 作为统一入口，支持灵活的参数配置。

### 常用参数

| 参数 | 说明 | 默认值 | 可选值 |
| :--- | :--- | :--- | :--- |
| `-env` | 运行环境 | `test` | `test`, `live` |
| `-project` | 指定运行项目 | `clue` | `projects/` 下的目录名 |
| `-mode` | 浏览器运行模式 | `headless` | `headless` (无头), `headed` (可视化) |
| `-browser` | 浏览器类型 | `chromium` | `chromium`, `firefox`, `webkit` |
| `-report` | 是否生成报告 | `no` | `yes`, `no` |

### 运行示例

```bash
# 1. 默认运行 (无头模式, test环境, clue项目)
python run.py

# 2. 可视化调试模式 (开启浏览器界面)
python run.py -mode headed

# 3. 指定生产环境运行
python run.py -env live

# 4. 生成并自动打开 Allure 报告
python run.py -report yes

# 5. 组合命令 (指定 Firefox 浏览器 + 可视化 + 生成报告)
python run.py -browser firefox -mode headed -report yes
```

### 按标记运行示例

```bash
# 仅运行登录相关用例
python run.py -project clue -env test -mode headless -report no -m login

# 仅运行账号相关用例
python run.py -project clue -env test -mode headless -report no -m account
```
### 多项目切换注意事项

框架通过 `-project` 参数实现多项目隔离运行，使用时需注意以下几点：
1.  **目录规范**：项目必须位于 `projects/` 目录下，且文件夹名称与 `-project` 参数完全一致。
2.  **配置隔离**：
    *   每个项目必须包含独立的 `project_settings.py`。
    *   该文件定义的 `ENV_VARS` 会覆盖全局配置，确保 `test`/`live` 环境地址与当前项目匹配。
3.  **导包路径**：
    *   运行时框架会将 `projects/<project_name>` 加入系统路径。
    *   **代码中请直接 import**，例如 `from pages.login_page import LoginPage`，**不要**带上 `projects.xxx` 前缀，以便代码复用和重构。
4.  **默认项目**：若未指定 `-project` 参数，默认运行 `clue` 项目（可在 `run.py` 修改默认值）。

## 五、使用增强断言

框架在 `BasePage` 中封装了智能等待断言，直接在 Page 类中使用 `self` 调用：

| 断言方法 | 说明 | 示例 |
| :--- | :--- | :--- |
| `assert_text_contains` | 验证元素文本包含指定内容 | `self.assert_text_contains("#msg", "登录成功")` |
| `assert_text_equals` | 验证元素文本完全等于指定内容 | `self.assert_text_equals("#status", "Active")` |
| `assert_element_visible` | 验证元素可见 | `self.assert_element_visible("#submit-btn")` |
| `assert_element_hidden` | 验证元素隐藏 | `self.assert_element_hidden(".loading-spinner")` |
| `assert_url_contains` | 验证当前 URL 包含指定内容 | `self.assert_url_contains("/dashboard")` |
| `assert_title_contains` | 验证页面标题包含指定内容 | `self.assert_title_contains("首页")` |

**代码示例 (Page 层):**
```python
class LoginPage(BasePage):
    def login_success_check(self, username):
        # 验证 URL 跳转
        self.assert_url_contains("/welcome")
        # 验证欢迎消息可见
        self.assert_element_visible("#welcome-msg")
        # 验证用户名显示正确
        self.assert_text_contains("#user-name", username)
```

## 六、数据驱动与变量引用

框架支持 YAML 数据驱动，并内置了变量引用机制 (`${var}`)，可动态读取环境变量或配置。

**数据文件示例 (`projects/clue/data/login_data.yaml`):**

```yaml
login_cases:
  - title: "网页登录，正确用户名和密码登录成功"
    login: "${admin_user_name}"
    password: "${admin_user_password}"
    run: true
  - title: "网页登录，错误用户名登录失败"
    login: "nonexistent_user"
    password: "${admin_user_password}"
    run: true
  - title: "网页登录，错误密码登录失败"
    login: "${admin_user_name}"
    password: "incorrect_password"
    run: true
```

## 七、核心依赖说明

项目基于以下核心库构建 (详见 `requirements.txt`):

| 库名称 | 用途 |
| :--- | :--- |
| `playwright` | 核心 UI 自动化引擎 |
| `pytest` | 测试运行器与断言框架 |
| `pytest-playwright` | Pytest 的 Playwright 插件 |
| `allure-pytest` | 生成 Allure 测试报告 |
| `pydantic` | 数据校验与设置管理 |
| `loguru` | 高性能日志记录 |
| `PyYAML` | YAML 数据文件解析 |
| `Faker` | 生成伪造测试数据 |

## 八、Playwright 使用手册（Python 同步 API）

### 选择器与 Locator

- `page.locator("css 或 xpath")`、`page.get_by_text("文本")`、`page.get_by_role("button", name="提交")`
- `nth(index)` 获取第 N 个匹配元素；`first`/`last` 获取首/末元素

```python
locator = page.locator(".btn.primary")
locator.first.click()
page.get_by_text("登录").click()
page.get_by_role("button", name="提交").click()
```

### 等待与断言

- 智能等待：`expect(locator).to_be_visible()` / `to_have_text()` / `to_contain_text()`
- URL/Title：`expect(page).to_have_url()` / `to_have_title()`

```python
from playwright.sync_api import expect
expect(page.locator("#status")).to_contain_text("成功", timeout=5000)
expect(page).to_have_url(re.compile("/welcome"))
expect(page).to_have_title(re.compile("首页"))
```

### 导航与上下文

- `page.goto(url, timeout=...)` 跳转；`page.reload()`
- `context = browser.new_context()`；`page = context.new_page()`
- `storage_state` 保存/加载登录态

```python
page.goto("https://example.com/login", timeout=30000)
context.storage_state(path="auth.json")
context = browser.new_context(storage_state="auth.json")
page = context.new_page()
```

### 基本交互

- 点击/输入：`page.click(selector)`、`page.fill(selector, text)`、`page.type(selector, text)`
- 选择器：`page.select_option("select#role", value="admin")`
- 悬浮/聚焦：`page.hover(selector)`、`page.focus(selector)`

```python
page.fill("#user_name", "xiaojing")
page.fill("#password", "qwer123")
page.click("xpath=//*[@id='root']/div/div/form/button")
page.select_option("select#role", value="admin")
```

### 文件上传与下载

```python
page.set_input_files("#upload", "path/to/file.png")
with page.expect_download() as download_info:
    page.click("text=导出")
download = download_info.value
download.save_as("outputs/export.xlsx")
```

### 弹窗与对话框

```python
def on_dialog(dialog):
    if dialog.type == "alert":
        dialog.accept()
page.once("dialog", on_dialog)
page.click("text=触发弹窗")
```

### 截图/视频/Tracing

```python
page.screenshot(path="outputs/snap.png", full_page=True)
context.tracing.start(screenshots=True, snapshots=True)
# 执行测试...
context.tracing.stop(path="outputs/trace.zip")
```

### 网络与请求拦截

```python
def handle_route(route):
    if "config" in route.request.url:
        route.fulfill(status=200, body='{"feature_flag":true}')
    else:
        route.continue_()
page.route("**/*", handle_route)
```

### 多窗口与多页面

```python
with context.expect_page() as new_page_info:
    page.click("text=在新窗口打开")
new_page = new_page_info.value
new_page.wait_for_load_state("networkidle")
```

### 权限与地理位置

```python
context = browser.new_context(
    geolocation={"longitude": 12.4924, "latitude": 41.8902},
    permissions=["geolocation"]
)
page = context.new_page()
```

### 设备与视口

```python
context = browser.new_context(viewport={"width": 1920, "height": 1080})
# 或 headed 模式下让视口跟随窗口
context = browser.new_context(viewport=None)
```

### 键盘/鼠标

```python
page.keyboard.type("Hello, World!")
page.keyboard.press("Enter")
page.mouse.move(100, 200)
page.mouse.click(120, 220)
```

### 超时与重试

- 全局默认 30s；单操作可覆盖 timeout
- 期望重试内置于 expect 智能等待

```python
page.click("#slow-btn", timeout=15000)
expect(page.locator("#done")).to_be_visible(timeout=10000)
```

### 并行与标记

- 使用 `pytest -n` 并行（需安装 pytest-xdist）
- 通过 `-m` 选择性运行：`login`、`account`、`projects`

```bash
pytest -n auto
python run.py -m login
```

### 请求 API（APIRequestContext）

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    request = p.request.new_context(base_url="https://api.example.com")
    resp = request.post("/login", data={"user":"xiaojing","pwd":"qwer123"})
    assert resp.ok
```

### 与本框架的结合

- 推荐通过 BasePage 封装统一日志与断言（见 [utils/base_utils/base_page.py](file:///Users/nidaye/DevolFiles/PythonProject/uiPlaywright/utils/base_utils/base_page.py)）
- Page 层只写业务操作；Case 层只表达测试意图；数据从 YAML 注入

## 九、录制脚本转换工具

框架提供了脚本转换工具，可以将 Playwright 录制的脚本自动转换为 POM 格式。

### 1. 录制脚本生成

使用 Playwright 自带录制工具生成 Python 脚本：

```bash
# 打开录制器并保存为 Python 脚本
playwright codegen https://clue-dev.spreadwin.cn/welcome \
  --target python \
  -b chromium \
  -o recorded_script.py

# 仅打开录制器（交互结束后手动保存）
playwright codegen -b chromium https://clue-dev.spreadwin.cn/
```

### 2. 脚本转换工具

框架提供两种转换工具：

#### 方式一：转换完整的 pytest 脚本

适用于 Playwright codegen 生成的完整 pytest 测试文件。

```bash
# 基本用法
python utils/tools/script_converter.py --input recorded_script.py --output ./output --page-name Example

# 参数说明
--input   : 录制的 pytest 脚本路径
--output  : 输出目录
--page-name: 生成的 Page 对象名称
```
### 3. 转换后的代码结构

转换工具会生成以下文件：

```
output/
├── _example_page.py      # Page 对象（使用 BasePage 封装方法）
└── test__example.py      # 测试用例
```

**生成的 Page 对象示例：**

```python
from utils.base_utils.base_page import BasePage
from playwright.sync_api import Page
from loguru import logger

class ExamplePage(BasePage):
    """Example页面"""

    # 定位器
    locator_textbox = "role=textbox"
    locator_button = "role=button"

    def login_flow(self):
        """执行登录流程"""
        self.visit("https://example.com/login")
        self.click(self.locator_textbox)
        self.input(self.locator_textbox, "admin")
        self.click(self.locator_button)
        logger.info("登录流程执行完成")
```

### 4. 转换后的优化建议

转换后的代码需要手动优化：

1. **优化定位器**：将自动生成的定位器改为更稳定的语义化选择器
2. **添加断言**：在关键步骤后添加断言验证
3. **参数化数据**：将硬编码的数据提取到 YAML 文件
4. **方法拆分**：将长方法拆分为多个小方法，提高可维护性

### 5. 使用框架封装方法的优势

转换工具生成的代码使用框架封装的 `base_page` 方法：

- **统一的日志记录**：所有操作自动记录日志，方便调试
- **统一的异常处理**：捕获操作失败的情况，提供清晰的错误信息
- **集成 Allure 报告**：自动添加 Allure 步骤装饰器，测试报告更清晰直观
- **代码一致性**：所有测试代码使用统一的方法，便于维护和扩展

## 十、多环境配置与使用

### 环境配置入口

每个项目的 `project_settings.py` 定义 `ENV_VARS`，包含 `common` 与具体环境键（如 `test`、`live`）。

**示例：[project_settings.py](file:///Users/nidaye/DevolFiles/PythonProject/uiPlaywright/projects/clue/project_settings.py)**

```python
ENV_VARS = {
    "common": {
        "项目名称": "clueSystem",
        "报告标题": "UI自动化测试报告-Clue",
        "env": "test"
    },
    "test": {
        "url": "https://clue-dev.spreadwin.cn",
        "host": "https://clueapi-dev.spreadwin.cn",
        "admin_user_name": "xiaojing",
        "admin_user_password": "qwer123",
        "login_type": "PASSWD",
        "uuid": "",
        "sms_state": "LOGIN"
    },
    "live": {
        "url": "https://your-prod-frontend",
        "host": "https://your-prod-api",
        "admin_user_name": "",
        "admin_user_password": ""
    }
}
```

### 运行时环境选择

使用 `-env` 指定环境，框架会将 `ENV_VARS["common"]` 与 `ENV_VARS[env]` 合并写入 `GLOBAL_VARS`。

```bash
python run.py -project clue -env test -mode headless -report no
```

### 数据文件变量引用

YAML 中通过 `${var}` 引用环境变量或配置，运行时由 `GLOBAL_VARS` 解析。

```yaml
login_cases:
  - title: "网页登录，正确用户名和密码登录成功"
    login: "${admin_user_name}"
    password: "${admin_user_password}"
    run: true
```

### 接口环境注入

接口定义文件可引用 `${}` 变量，运行前会注入当前环境的 host、账号等。

**示例：[clue_login.yml](file:///Users/nidaye/DevolFiles/PythonProject/uiPlaywright/projects/clue/interfaces/clue_login.yml)**

### 多项目 × 多环境组合

```bash
# 指定项目与环境
python run.py -project projectA -env test

# 结合标记筛选
python run.py -project projectA -env live -m account
```

### 新增环境步骤（如 `staging`）

1. 在项目的 `project_settings.py` 中添加 `staging` 键，填入前端 `url` 与接口 `host` 等
2. 如有环境专属账号或参数，一并添加到该键下
3. 运行时传入 `-env staging` 即可

## 十一、环境变量与通知 (Secrets)

若需启用邮件、钉钉或企业微信通知，请在 CI/CD 平台配置以下 **Secrets / Variables**：

- `EMAIL_USER` / `EMAIL_PASSWORD` / `EMAIL_HOST` / `EMAIL_TO`
- `DINGTALK_WEBHOOK`
- `WECHAT_WEBHOOK`

## 十二、最佳实践

### 1. Page 对象设计原则

- **单一职责**：每个 Page 类只负责一个页面
- **封装细节**：将元素定位和操作细节封装在 Page 类中
- **语义化方法**：方法名应表达业务含义，如 `login()`、`create_order()`

### 2. 测试用例编写原则

- **独立性**：每个测试用例应独立运行，不依赖其他用例
- **可重复性**：测试结果应稳定可重复
- **清晰性**：用例名称和步骤应清晰明了

### 3. 数据管理原则

- **数据分离**：测试数据与代码分离，存储在 YAML 文件中
- **变量引用**：使用 `${var}` 引用环境配置，避免硬编码
- **数据有效性**：确保测试数据的有效性和时效性

### 4. 断言策略

- **关键路径断言**：在关键业务步骤后添加断言
- **智能等待**：使用框架封装的断言方法，自动等待元素状态
- **明确断言**：断言应明确验证业务结果，而非技术细节

## 十三、常见问题

### 1. 元素定位失败

**原因**：页面加载慢、元素动态变化、定位器不稳定

**解决方案**：
- 使用语义化选择器：`get_by_role()`、`get_by_text()`
- 增加等待时间：`wait_for_selector()`
- 使用更稳定的属性：`data-testid`、`aria-label`

### 2. 测试用例不稳定

**原因**：网络波动、数据依赖、环境问题

**解决方案**：
- 使用智能等待而非固定 `sleep()`
- 确保测试数据独立且可重复
- 在 CI/CD 中配置重试机制

### 3. 报告生成失败

**原因**：Allure 未安装、路径问题

**解决方案**：
- 确保 Allure 已正确安装并配置环境变量
- 检查报告输出路径是否有写入权限

## 十四、贡献指南

欢迎提交 Issue 和 Pull Request 来改进框架！

### 开发环境设置

```bash
# 克隆项目
git clone <repository-url>

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright
playwright install
```

### 代码规范

- 遵循 PEP 8 编码规范
- 添加必要的注释和文档字符串
- 编写单元测试确保代码质量

## 十五、许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。
