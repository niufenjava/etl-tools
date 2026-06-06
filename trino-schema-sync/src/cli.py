"""命令行参数解析。"""

import argparse

VALID_LAYERS = ["cdm", "dwd", "ads", "bi", "ods"]
VALID_MODES = ["field-index", "schema-index", "table-index"]


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Trino 表结构同步工具")
    parser.add_argument(
        "--mode",
        choices=VALID_MODES + ["all"],
        default="all",
        help="同步模式：field-index=字段索引, schema-index=库索引, table-index=表索引, all=全部",
    )
    parser.add_argument(
        "--layer",
        choices=VALID_LAYERS,
        help=f"按分层同步，可选: {', '.join(VALID_LAYERS)}",
    )
    parser.add_argument(
        "--schema",
        help="指定 schema",
    )
    args = parser.parse_args(argv)

    if args.schema:
        args.mode = "schema"

    return args
