# UI Automation Framework (Playwright + Pytest)

基于 **Playwright + Pytest** 的 UI/API 自动化测试框架。当前示例项目为 `clue`，支持 Page Object、YAML 数据驱动、项目级环境配置、Allure 报告、录制脚本转换、Docker 容器运行和 GitHub Actions。

## 一、核心特性

- **多项目架构**：通过 `projects/<project>` 隔离业务项目，目前默认项目为 `clue`。
- **多环境配置**：项目环境在 `projects/<project>/project_settings.py` 中维护；`clue` 当前支持 `test` / `prod`。
- **POM 设计模式**：页面对象模型（Page Object Model）将页面操作与测试用例分离。
- **框架封装操作**：Page 层优先使用 `BasePage.click()`、`BasePage.input()`、`BasePage.press()` 和封装断言，统一日志与 Allure 步骤。
- **marker 自动注册**：marker 在各项目 `conftest.py` 的 `pytest_configure` 注册（非 `pytest.ini`）；crm 已支持自动扫描 `testcases/test_*.py` 的 `@pytest.mark.xxx`，新增用例无需手改。
- **YAML 数据驱动**：测试数据放在 `projects/<project>/data/*.yaml`，测试代码只表达流程。
- **UI + API 混合测试**：UI 用例在 `testcases`，接口定义在 `interfaces/*.yml`。
- **Allure 报告**：支持生成 `outputs/report/allure_html`、压缩报告 `outputs/report/autotest_report.zip`。
- **录制脚本转换工具**：Playwright codegen 录制统一放 `projects/<project>/files/*.md`，由 `convert_recordings.py` 批量转换为 Page Object + data YAML + testcase 三件套；转换器对 `set_input_files`/`goto`/`exact=True` 等已自动处理，`#el-id-*` 自动 ID 等不稳定定位器会标 TODO 提示手工补全。
- **Docker 运行**：提供 `Dockerfile`、`.dockerignore`，基于官方 Playwright Python 镜像。

## 二、项目结构

```text
uiPlaywright/
├── config/
│   ├── env/
│   │   ├── .env.example          # 环境变量模板
│   │   └── .env                  # 本地敏感配置，需手动创建，不提交
│   ├── settings.py               # 路径 + 运行配置 RunConfig + 通知配置（框架配置唯一入口）
│   └── global_vars.py            # 运行期全局变量
├── interfaces/                   # 接口定义池（项目根，各项目按文件名隔离）
│   ├── clue_login.yml
│   └── crm_login.yml
├── projects/
│   └── clue/
│       ├── project_settings.py   # clue 项目环境配置：test / prod
│       ├── data/
│       │   ├── login_data.yaml
│       │   ├── account_data.yaml
│       │   ├── data_page.yaml
│       │   ├── vehicle_list.yaml
│       │   └── export_record.yaml
│       ├── pages/
│       │   ├── home_page.py
│       │   ├── login_page.py
│       │   ├── account/account_page.py
│       │   ├── data/data_page.py
│       │   ├── vehicle/vehicle_list_page.py
│       │   └── export_record/export_record_page.py
│       └── testcases/
│           ├── conftest.py       # clue 项目级 fixture，默认注入登录态
│           ├── api/              # API 用例
│           │   └── test_login_api.py
│           └── ui/               # UI 用例
│               ├── test_login.py
│               ├── test_create_account.py
│               ├── test_data_page.py
│               ├── test_vehicle_list.py
│               └── test_export_record.py
├── utils/
│   ├── base_utils/
│   │   ├── base_page.py          # UI 页面基础封装
│   │   ├── base_request.py       # API 请求基础封装
│   │   └── request_control.py    # YAML 接口请求流程
│   ├── data_utils/               # 变量替换、数据处理、提取器
│   ├── files_utils/              # YAML / 文件处理
│   ├── report_utils/             # Allure 报告生成与打包
│   ├── notify_utils/             # 邮件、钉钉、企业微信通知
│   └── tools/
│       ├── po_style_converter.py # 录制片段转 Page/data/testcase 三件套（单文件）
│       ├── convert_recordings.py # 扫描 projects/<项目>/files/*.md 批量转 POM 三件套（推荐）
│       ├── recording_to_basepage.py # 录制转函数式 BasePage 脚本
│       ├── script_converter.py
│       └── raw_script_converter.py
├── files/                         # 测试资源附件（如 1.jpeg 等上传文件）；codegen 录制源在 projects/<项目>/files/*.md
├── outputs/                      # 测试产物：日志、报告、trace、压缩包
├── Dockerfile
├── .dockerignore
├── .gitignore
├── pytest.ini                    # pytest 运行参数与告警过滤（marker 在各项目 conftest 注册）
├── requirements.txt
└── run.py                        # 框架统一执行入口
```

## 三、快速开始

### 1. 环境准备

- 推荐 Python：**3.13**（当前 CI/本地验证使用 Python 3.13）
- 浏览器：Chromium / Firefox / WebKit
- 报告：如需本地打开 Allure HTML，需 Java + Allure Commandline

### 2. 安装依赖

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
playwright install chromium
```

如果需要运行全部浏览器：

```bash
playwright install
```

### 3. 配置环境变量

```bash
cp config/env/.env.example config/env/.env
```

## 四、运行测试

框架统一入口为 `run.py`。

### 常用参数

| 参数 | 说明 | 默认值 | 可选值 |
| :--- | :--- | :--- | :--- |
| `-env` | 运行环境 | `test` | `test`, `prod` |
| `-project` | 指定项目 | `clue` | `projects/` 下的目录名 |
| `-mode` | 浏览器模式 | `headed` | `headless`, `headed` |
| `-browser` | 浏览器类型 | `chromium` | `chromium`, `firefox`, `webkit` |
| `-report` | 是否生成并打开 Allure 报告 | `yes` | `yes`, `no` |
| `-m` | pytest marker 筛选 | 无 | `login`, `account`, `data`, `vehicle`, `export`, `api`, `recordings` |
| `-path` | 指定测试文件或目录 | 无 | 任意 pytest 路径 |
| `-video` | 视频录制 | `off` | `on`, `off`, `retain-on-failure` |
| `-screenshot` | 截图策略 | `on` | `on`, `off`, `only-on-failure` |
| `-tracing` | trace 策略 | `retain-on-failure` | `on`, `off`, `retain-on-failure` |
| `-recording` | 录制运行模式 | `converted` | `converted`(跑 testcases), `raw`/`all`(legacy，recordings/ 已弃用) |

### 常用命令

```bash
# 默认运行 clue/test，headed 模式，并生成报告
python run.py -project clue

# 推荐本地快速验证：headless，不生成报告
python run.py -project clue -env test -mode headless -browser chromium -report no

# 可视化调试
python run.py -project clue -env test -mode headed -browser chromium -report no

# 只跑登录 UI 用例
python run.py -project clue -env test -mode headless -report no -m login

# 只跑登录 API 用例
python run.py -project clue -env test -mode headless -report no -m api

# 只跑车辆列表用例
python run.py -project clue -env test -mode headless -report no -m vehicle

# 只跑导出记录用例
python run.py -project clue -env test -mode headless -report no -m export

# 直接跑原始 codegen 录制（不经 POM 转换，需录制含 page.goto 自包含导航）
python run.py -project clue -recording raw -report no

# 同时跑 POM 用例和原始录制
python run.py -project clue -recording all -report no
```

## 五、Allure 报告

### 生成报告

```bash
python run.py -project clue -env test -mode headless -browser chromium -report yes
```

## 六、Docker 运行

项目提供 `Dockerfile` 和 `.dockerignore`，使用官方 Playwright Python 镜像：

```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.57.0-noble
```

### 构建镜像

确保 Docker Desktop / Docker daemon 已启动：

```bash
docker build -t uiplaywright:latest .
```

### 运行容器

```bash
docker run --rm uiplaywright:latest
```

带本地环境变量文件：

```bash
docker run --rm \
  --env-file config/env/.env \
  uiplaywright:latest
```

覆盖默认命令，例如只跑导出记录：

```bash
docker run --rm \
  --env-file config/env/.env \
  uiplaywright:latest \
  python run.py -project clue -env test -mode headless -browser chromium -report no -m export
```

> `.dockerignore` 已排除 `.auth/`、`outputs/`、`.env`、`.omc/`、`.claude/`、本地缓存和报告产物，避免把敏感信息和运行产物打进镜像。

## 七、使用增强断言

框架在 `BasePage` 中封装了智能等待断言，Page 类中通过 `self` 调用：

| 断言方法 | 说明 | 示例 |
| :--- | :--- | :--- |
| `assert_text_contains` | 验证元素文本包含指定内容 | `self.assert_text_contains("#msg", "登录成功")` |
| `assert_text_equals` | 验证元素文本完全等于指定内容 | `self.assert_text_equals("#status", "Active")` |
| `assert_element_visible` | 验证元素可见 | `self.assert_element_visible("#submit-btn")` |
| `assert_element_hidden` | 验证元素隐藏 | `self.assert_element_hidden(".loading-spinner")` |
| `assert_url_contains` | 验证当前 URL 包含指定内容 | `self.assert_url_contains("/welcome")` |
| `assert_title_contains` | 验证页面标题包含指定内容 | `self.assert_title_contains("首页")` |

示例：

```python
class LoginPage(BasePage):
    def login_success_check(self, username):
        self.assert_url_contains("/welcome")
        self.assert_element_visible("#welcome-msg")
        self.assert_text_contains("#user-name", username)
        return self
```

## 八、数据驱动与变量引用

数据文件放在：

```text
projects/<project>/data/*.yaml
```

示例：

```yaml
login_cases:
  - title: "网页登录，正确用户名和密码登录成功"
    login: "${admin_user_name}"
    password: "${admin_user_password}"
    run: true
```

测试用例读取：

```python
data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "login_data.yaml")
cases = YamlHandle(data_path).read_yaml

@pytest.mark.parametrize("case", cases["login_cases"], ids=lambda x: x["title"])
def test_login_user(self, case):
    ...
```

> `run: false` 的 case 会在收集阶段被框架跳过。

## 九、当前示例用例

### 登录 UI

- Page：`projects/clue/pages/login_page.py`
- Data：`projects/clue/data/login_data.yaml`
- Test：`projects/clue/testcases/test_login.py`
- Marker：`login`

### 登录 API

- Interface：`interfaces/clue_login.txt`
- Test：`projects/clue/testcases/test_login_api.py`
- Marker：`api`

运行：

```bash
python run.py -m api -report no
```

## 十、录制脚本转换工具

### 推荐流程：`files/*.md` + `convert_recordings.py`（批量，推荐）

Playwright codegen 录制片段保存为 `projects/<project>/files/<base>.md`（可含 `# 标题`、
`def test_xxx` 包裹，转换器自动剥离非 `page.` 行）。运行 `convert_recordings.py` 批量转 POM 三件套，
已存在目标默认跳过以防覆盖手工修复，`--force` 强制重生。

```bash
# 扫描 files/*.md 转 POM 三件套（已存在默认跳过，--force 强转）
python utils/tools/convert_recordings.py
python utils/tools/convert_recordings.py --project crm
python utils/tools/convert_recordings.py --project crm --file createAccount
python utils/tools/convert_recordings.py --project crm --force
```

命名约定：`files/my_account.md` -> `MyAccountPage` / `pages/my_account_page.py` /
`data/my_account.yaml` / `testcases/test_my_account.py`（`<base>` 即文件名去扩展名，
想要 `my_account_page.py` 就把录制命名为 `my_account.md`）。

### 单文件转换：`po_style_converter.py`

该工具可以把 Playwright codegen 片段转换为：

```text
Page Object + data YAML + testcase
```

输入示例：

```python
# 导出页面
page.get_by_role("link", name="to-top 导出记录").click()
page.get_by_role("button", name="查 询").click()
page.get_by_role("textbox", name="页").fill("5")
page.get_by_role("textbox", name="页").press("Enter")
```

生成三件套：

```bash
python utils/tools/po_style_converter.py \
  --input projects/clue/files/clue.md \
  --class-name ExportRecordPage \
  --file-name export_page.py \
  --suite-dir projects/clue \
  --page-subdir pages/export \
  --page-import export.export_record_page
```

生成结果：

```text
projects/clue/pages/export/export_page.py
projects/clue/data/export_record.yaml
projects/clue/testcases/test_export_record.py
```

只生成 Page Object：

```bash
python utils/tools/po_style_converter.py \
  --input projects/clue/files/clue.md \
  --class-name ExportRecordPage \
  --file-name export_page.py \
  --output projects/clue/pages/export/export_page.py
```

### 转换后的注意事项

转换结果是初稿，复杂控件通常需要实际运行后微调：

1. **菜单图标 + 文本**：如 `to-top 导出记录` 可能需要改为 `导出记录`。
2. **日期选择器**：建议限定在当前可见的 `.ant-picker-dropdown` 内。
3. **Popover/Modal**：导出、确认弹窗类操作需要确认真实 DOM。
4. **仍需手工补全的动作**：转换器已自动处理 `set_input_files`（-> `upload_file`）、
   `page.goto`（静默跳过，导航归用例 setup）、`get_by_role(..., exact=True)`、相邻试错 fill
   合并取末值、退键 `press` 丢弃、连续重复 `click` 去重。但 `get_by_label().get_by_text()` 等
   链式定位、`#el-id-*` 自动 ID 会留 `# TODO`，且 el-select 下拉、头像上传等需按真实 DOM 校验
   （如头像实际是点 `figure.avatar` 挂隐藏 `input[type=file]`）；正因如此 `convert_recordings.py`
   默认跳过已存在目标以保护手工修复，`--force` 才覆盖。
5. **marker**：在项目 `conftest.py` 的 `pytest_configure` 注册（非 `pytest.ini`）；crm 已支持
   自动扫描 `test_*.py` 的 `@pytest.mark.xxx`，新增用例无需手改。
6. **补断言**：录制脚本多为操作步骤，建议在关键业务节点补充断言。

### 其他转换工具

- `utils/tools/recording_to_basepage.py`：录制转函数式 BasePage 脚本（非 POM）。
- `utils/tools/script_converter.py`：完整 pytest 脚本转换。
- `utils/tools/raw_script_converter.py`：原始操作序列转换。

后续新录制优先用 `files/*.md` + `convert_recordings.py`。

## 十一、多环境配置与使用

每个项目通过 `project_settings.py` 定义环境：

```python
ENV_VARS = {
    "common": {
        "报告标题": "UI自动化测试报告-Clue",
        "项目名称": "clueSystem",
        "tester": "会飞的🐟",
        "department": "成都研发后台",
        "env": "test",
    },
    "test": {
        "url": "https://clue-dev.spreadwin.cn",
        "host": "https://clueapi-dev.spreadwin.cn",
        "admin_user_name": os.getenv("CLUE_ADMIN_USER", ""),
        "admin_user_password": os.getenv("CLUE_ADMIN_PASSWORD", ""),
        "login_type": "PASSWD",
        "uuid": "",
        "sms_state": "LOGIN",
    },
    "prod": {
        "url": "https://clue.spreadwin.cn",
        "host": "https://clueapi.spreadwin.cn",
        "admin_user_name": os.getenv("CLUE_ADMIN_USER", ""),
        "admin_user_password": os.getenv("CLUE_ADMIN_PASSWORD", ""),
    },
}
```

运行时：

```bash
python run.py -project clue -env test
python run.py -project clue -env prod
```

YAML 中可通过 `${var}` 引用配置：

```yaml
payload:
  user_name: "${user_name}"
  password: "${password}"
```

## 十二、新增一个 UI 用例的建议流程

1. 在 `projects/clue/pages/<module>/` 新增 Page Object。
2. 在 `projects/clue/data/` 新增 YAML 数据文件。
3. 在 `projects/clue/testcases/` 新增 `test_<module>.py`。
4. marker 在项目 `conftest.py` 注册（crm 自动扫描 `test_*.py` 无需手改；clue 需手动加到 `pytest_configure`）。
5. 运行单模块验证：

```bash
python run.py -project clue -env test -mode headless -browser chromium -report no -m <marker>
```

## 十三、定位器规范

Page Object 中的元素定位器按以下优先级选择，保证稳定与可维护：

1. `get_by_role` / `get_by_label`（语义化，最稳定，优先使用）
2. `data-testid`（团队可控的测试标识）
3. `id=`（稳定，需前端配合）
4. `text=`（文本定位，适合按钮/链接）
5. `xpath=`（最后手段，**禁止使用绝对路径**如 `/html/body/...`，DOM 层级变化即失效）

示例：

```python
# 推荐：语义化或稳定结构定位
locator_btn_confirm = "xpath=//div[contains(@class,'ant-modal-footer')]//button[contains(@class,'ant-btn-primary')]"
# 禁止：绝对路径，DOM 层级微调即失效
locator_btn_confirm = "xpath=/html/body/div[2]/div/div[2]/div/div[1]/div/div[3]/div/div/button[2]"
```