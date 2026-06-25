# -*- coding: utf-8 -*-
# @File    : allure_fixture_filter.py
# @Desc    : 隐藏 Allure 报告 Set up / Tear down 区域的内部 fixture 噪声，
#            只保留对业务有意义的 fixture（如 browser / page / storage_state_path / setup_teardown_for_each 等）。
#
# 实现方式：对 allure_commons.reporter.AllureReporter 的 start/stop_before_fixture
# 与 start/stop_after_fixture 打猴补丁，命中黑名单的 fixture 不进 Allure 容器。

# 黑名单：这些 fixture 是 pytest / pytest-base-url / faker / pytest-playwright 内部
# 流转用，对业务理解无帮助，反而让 Set up 区域显得很乱。
HIDDEN_FIXTURES = frozenset({
    # pytest 内部
    "pytestconfig", "base_url",
    # pytest-base-url
    "_verify_url",
    # faker 的 pytest 插件
    "_session_faker",
    # pytest-playwright（本地副本 plugins/pytest_playwright.py）的内部 fixture
    "delete_output_dir",
    "_pw_artifacts_folder",
    "_artifacts_recorder",
    "playwright",
    "launch_browser",
    "browser_type",
    "device",
    "browser_type_launch_args",
    "browser_context_args",
    "new_context",
})

# 白名单（参考用，不在逻辑里使用）：
#   browser / context / page / storage_state_path / setup_teardown_for_each


def _make_start_wrapper(original):
    """包装 start_before/after_fixture：命中黑名单则跳过原方法。"""
    # 用闭包共享一组 uuid，确保配套的 stop_* 也能跳过
    hidden_uuids = set()

    def wrapper(self, parent_uuid, uuid, fixture):
        if getattr(fixture, "name", None) in HIDDEN_FIXTURES:
            hidden_uuids.add(uuid)
            return
        return original(self, parent_uuid, uuid, fixture)

    wrapper._hidden_uuids = hidden_uuids
    return wrapper


def _make_stop_wrapper(original, hidden_uuids):
    """包装 stop_before/after_fixture：命中黑名单（uuid 在隐藏集合中）则跳过原方法。"""
    def wrapper(self, uuid, **kwargs):
        if uuid in hidden_uuids:
            hidden_uuids.discard(uuid)
            return
        return original(self, uuid, **kwargs)
    return wrapper


def pytest_configure(config):
    """pytest 启动时打补丁。重复执行无副作用。"""
    try:
        from allure_commons.reporter import AllureReporter
    except ImportError:
        return  # 未安装 allure，直接跳过

    if getattr(AllureReporter, "_fixture_filter_applied", False):
        return

    # ---- before fixture (Set up 区域) ----
    start_before = _make_start_wrapper(AllureReporter.start_before_fixture)
    AllureReporter.start_before_fixture = start_before
    AllureReporter.stop_before_fixture = _make_stop_wrapper(
        AllureReporter.stop_before_fixture, start_before._hidden_uuids,
    )

    # ---- after fixture (Tear down 区域) ----
    start_after = _make_start_wrapper(AllureReporter.start_after_fixture)
    AllureReporter.start_after_fixture = start_after
    AllureReporter.stop_after_fixture = _make_stop_wrapper(
        AllureReporter.stop_after_fixture, start_after._hidden_uuids,
    )

    AllureReporter._fixture_filter_applied = True
