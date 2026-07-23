# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @File    : allure_playwright_attach.py
# @Desc    : 将 pytest-playwright 落盘的截图 / 视频 / trace 自动附到 Allure 报告。


from pathlib import Path
from typing import Optional

import pytest


def _get_allure() -> Optional[object]:
    try:
        import allure  # noqa: WPS433 — 延迟导入避免无 allure 环境下报错
        return allure
    except ImportError:
        return None


def _attach_dir(folder: Path, allure_mod) -> None:
    """扫描目录下的 .png/.webm/.zip 附件，挂到 Allure 报告。"""
    if not folder.exists() or not folder.is_dir():
        return
    for f in folder.rglob("*"):
        if not f.is_file():
            continue
        suffix = f.suffix.lower()
        if suffix == ".png":
            allure_mod.attach.file(str(f), name=f.name,
                                   attachment_type=allure_mod.attachment_type.PNG)
        elif suffix == ".webm":
            allure_mod.attach.file(str(f), name=f.name,
                                   attachment_type=allure_mod.attachment_type.WEBM)
        elif suffix == ".zip":
            # trace.zip：Allure 没有 ZIP 媒体类型，用通用附件
            allure_mod.attach.file(str(f), name=f.name, extension="zip")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_teardown(item, nextitem):
    """fixture teardown 跑完后，pytest-playwright 已把媒体文件写盘；
    扫描产物目录把媒体文件挂到 Allure（成功 / 失败都挂）。"""
    yield
    allure_mod = _get_allure()
    if allure_mod is None:
        return

    output_root = Path(item.config.getoption("--output", default="test-results"))
    if not output_root.exists():
        return
    try:
        from slugify import slugify
    except ImportError:
        _attach_dir(output_root, allure_mod)
        return

    candidates = {output_root / slugify(item.nodeid), output_root / slugify(item.name)}
    for c in candidates:
        _attach_dir(c, allure_mod)
