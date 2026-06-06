#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据文件比较工具：比较两个文件的 ID 集合差异"""

import argparse
from pathlib import Path


def load_ids(path: Path) -> set[str]:
    """从文件加载所有非空行，返回集合"""
    ids = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                ids.add(s)
    return ids


def main():
    parser = argparse.ArgumentParser(
        description="比较两个文件的 ID 集合差异",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 data_compare.py file1.txt file2.txt
  python3 data_compare.py /path/to/v1.txt /path/to/v2.txt
""",
    )
    parser.add_argument("v1", help="V1 文件路径")
    parser.add_argument("v2", help="V2 文件路径")
    args = parser.parse_args()

    v1_path = Path(args.v1)
    v2_path = Path(args.v2)

    if not v1_path.exists():
        print(f"错误: V1 文件不存在: {v1_path}")
        return 1
    if not v2_path.exists():
        print(f"错误: V2 文件不存在: {v2_path}")
        return 1

    v1_ids = load_ids(v1_path)
    v2_ids = load_ids(v2_path)

    only_in_v1 = sorted(v1_ids - v2_ids)
    only_in_v2 = sorted(v2_ids - v1_ids)

    print(f"V1 总数: {len(v1_ids)}")
    print(f"V2 总数: {len(v2_ids)}")
    print()

    print(f"只在 V1 中存在的 (V1 - V2): {len(only_in_v1)}")
    for i in only_in_v1:
        print(i)
    print()

    print(f"只在 V2 中存在的 (V2 - V1): {len(only_in_v2)}")
    for i in only_in_v2:
        print(i)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
