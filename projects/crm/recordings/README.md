# Playwright 录制脚本存放目录

本目录存放各特性的 Playwright codegen 录制（`.py`），一物两用：

1. **直接运行**（`run.py -recording raw`）：录制文件是完整 codegen 测试文件
   （`def test_x(page): ...`），可被 pytest-playwright 直接当用例跑。
2. **转 POM 三件套**（`python utils/tools/convert_recordings.py`）：
   ```
   recordings/<base>.py  ->  pages/<base>_page.py  +  data/<base>.yaml  +  testcases/test_<base>.py
   ```

## 录制文件格式

- **完整 codegen 测试文件**：`from playwright.sync_api import Page` + `def test_<base>(page: Page):`
  + 缩进的 `page.xxx(...)` 动作行。这样 `raw` 模式才能直接收集运行。
- 文件名用 snake_case 特性名，如 `my_account.py` -> 类 `MyAccountPage` / 页 `my_account_page.py` /
  数据 `my_account.yaml` / 用例 `test_my_account.py`。
- `import` / `def` / `expect(...)` 等非动作行转换时自动忽略；`set_input_files` / `page.goto` /
  `get_by_role(..., exact=True)` 等无法逐行映射的动作会以 `# TODO` 标出，需手工补全。

## 命令

```bash
# 扫描所有项目，转 POM 三件套
python utils/tools/convert_recordings.py

# 仅 crm / 仅一个 / 强制覆盖
python utils/tools/convert_recordings.py --project crm
python utils/tools/convert_recordings.py --project crm --file my_account
python utils/tools/convert_recordings.py --project crm --force   # 覆盖已存在（慎用，丢手工修复）

# 直接跑原始录制（不经 POM 转换）
python run.py -project crm -recording raw
python run.py -project crm -recording all    # 同时跑 testcases + recordings
```

## 注意

- **默认跳过已存在**：任一目标文件（page/data/testcase）已存在即跳过，避免覆盖手工修复
  （如 `my_account` 的 `手机号` exact 定位器、头像 `set_input_files` 改挂隐藏 input）。
  确需重生用 `--force`。
- **raw 模式需自包含导航**：录制若未含 `page.goto`，raw 模式直接跑会在首个定位超时；
  完整 raw 回放请在录制开头补导航。`my_account.py` 即为「已在编辑页」片段，仅作格式示例。
- 自动生成的用例标记为 `@pytest.mark.recordings`（已注册）+ `@pytest.mark.<base>`；
  `<base>` marker 由 conftest `pytest_configure` 自动扫描 `test_*.py` 注册，无需手改。
