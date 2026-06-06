#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""etl-tools: 数仓开发工具集"""

import argparse
import subprocess
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser(
        description="etl-tools: 数仓开发工具集",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
可用工具:
  lineage           ETL 表血缘分析工具
  trino-schema-sync Trino 表结构同步工具

示例:
  python etl_tools.py lineage --all
  python etl_tools.py trino-schema-sync --all
  python etl_tools.py trino-schema-sync --layer cdm
""",
    )
    parser.add_argument(
        "tool",
        choices=["lineage", "trino-schema-sync"],
        help="工具名称",
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="传递给工具的参数",
    )

    parsed = parser.parse_args()
    tool = parsed.tool
    tool_args = parsed.args

    if tool == "lineage":
        script = TOOLS_DIR / "lineage" / "etl_lineage.py"
        sys.exit(subprocess.call([sys.executable, str(script)] + tool_args))

    elif tool == "trino-schema-sync":
        script = TOOLS_DIR / "trino-schema-sync" / "sync_trino_schema.py"
        sys.exit(subprocess.call([sys.executable, str(script)] + tool_args))


if __name__ == "__main__":
    main()
