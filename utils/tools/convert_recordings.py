# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc    : 录制文件转换成 POM 三件套

"""
用法：
    python utils/tools/convert_recordings.py                       # 扫描所有项目
    python utils/tools/convert_recordings.py --project crm          # 仅 crm
    python utils/tools/convert_recordings.py --project crm --force  # 强制覆盖已存在
    python utils/tools/convert_recordings.py --project crm --file my_account  # 仅转一个

录制源：projects/<项目>/files/*.md（Playwright codegen 录制片段）。
新增 .md 后运行本命令即可生成 page/data/testcase 三件套；已存在目标默认跳过，--force 强制重生。
"""

import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.tools.po_style_converter import PoStyleConverter
PROJECTS_DIR = Path(__file__).resolve().parents[2] / "projects"


def snake_to_pascal(name: str) -> str:
    """
    """
    return "".join(part[:1].upper() + part[1:] for part in name.split("_") if part)


def normalize_base(stem: str) -> str:
    """录制文件名去扩展名后规整：去掉误带的 _page 后缀，避免类名出现 ...PagePage。"""
    base = stem
    if base.endswith("_page"):
        base = base[: -len("_page")]
    return base


def convert_one(recording_path: Path, project_dir: Path, force: bool = False):
    """
    转换单个录制文件为 POM 三件套。
    :return: (status, message) status in {"gen", "skip"}
    """
    base = normalize_base(recording_path.stem)
    class_name = snake_to_pascal(base)  # MyAccount（PoStyleConverter 会自动补 "Page"）
    # file_name 由 class_name 派生（snake_case），保证类名/文件名/用例引用三者一致
    conv = PoStyleConverter(class_name=class_name)

    page_dir = project_dir / "pages"
    data_dir = project_dir / "data"
    testcase_dir = project_dir / "testcases" / "ui"
    # 全部用转换器派生的文件名，保证「写入路径」与「用例内部引用路径」一致
    page_path = page_dir / conv.file_name
    data_path = data_dir / conv.data_file_name()
    testcase_path = testcase_dir / conv.test_file_name()

    targets = [page_path, data_path, testcase_path]
    if any(p.exists() for p in targets) and not force:
        return "skip", f"{base}: 目标已存在，跳过（--force 强转）"

    for d in (page_dir, data_dir, testcase_dir):
        d.mkdir(parents=True, exist_ok=True)

    script = recording_path.read_text(encoding="utf-8")
    page_path.write_text(conv.convert(script), encoding="utf-8")
    data_path.write_text(conv.generate_data_yaml(script), encoding="utf-8")
    testcase_path.write_text(conv.generate_testcase(), encoding="utf-8")
    return "gen", f"{base}: 生成 {page_path.name} / {data_path.name} / {testcase_path.name}"


def discover_projects() -> list:
    """所有含 files/ 录制源目录的项目。"""
    if not PROJECTS_DIR.is_dir():
        return []
    return sorted([d for d in PROJECTS_DIR.iterdir() if d.is_dir() and (d / "files").is_dir()])


def list_recordings(project_dir: Path, file_filter: str = None) -> list:
    """项目下待转换的录制文件（.md；排除下划线开头）。"""
    files_dir = project_dir / "files"
    if not files_dir.is_dir():
        return []
    files = [f for f in sorted(files_dir.glob("*.md")) if not f.name.startswith("_")]
    if file_filter:
        files = [f for f in files if normalize_base(f.stem) == file_filter or f.stem == file_filter]
    return files


def main():
    parser = argparse.ArgumentParser(
        description="扫描项目 files/ 目录，批量把 Playwright 录制(.md)转为 POM 三件套"
    )
    parser.add_argument("--project", "-p", help="项目名（projects/<name>）；不传则扫描所有项目")
    parser.add_argument("--file", "-f", help="仅转换指定录制（文件名不含扩展名），如 my_account")
    parser.add_argument("--force", action="store_true", help="目标已存在时强制重生覆盖")
    args = parser.parse_args()

    if args.project:
        project_dir = PROJECTS_DIR / args.project
        if not project_dir.is_dir():
            print(f"项目不存在：{project_dir}")
            return
        project_dirs = [project_dir]
    else:
        project_dirs = discover_projects()
        if not project_dirs:
            print(f"未发现含 files/ 目录的项目（请在 projects/<name>/files/ 放入 .md 录制）")
            return

    total_gen = total_skip = 0
    for project_dir in project_dirs:
        recordings = list_recordings(project_dir, args.file)
        print(f"\n[{project_dir.name}] 录制 {len(recordings)} 个")
        if not recordings:
            print("  无录制文件（将 codegen 录制保存为 .md 放入 files/ 后重试）")
            continue
        for rec in recordings:
            status, msg = convert_one(rec, project_dir, force=args.force)
            print(f"  {'✅' if status == 'gen' else '⏭️'} {msg}")
            if status == "gen":
                total_gen += 1
            else:
                total_skip += 1

    print(f"\n完成：生成 {total_gen}，跳过 {total_skip}")
    if total_gen:
        print("提示：自动转换对 set_input_files / goto / exact 定位器等会留 # TODO，请手工补全；"
              "已存在目标默认跳过以防覆盖手工修复，--force 可强制重生。")


if __name__ == "__main__":
    main()
