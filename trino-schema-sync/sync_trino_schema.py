#!/usr/bin/env python3
# coding: utf-8
"""Trino 表结构同步工具主入口。"""

import logging
import sys
from collections import defaultdict
from pathlib import Path

from src.cli import parse_args
from src.config import load_config
from src.trino_client import TrinoClient
from src.schema_discovery import LAYER_RULES, filter_schemas, classify_schema
from src.writer import (
    write_markdown,
    format_table_header,
    format_column_line,
    format_schema_index_line,
    format_table_index_line,
    format_layer_header,
)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)
logger = logging.getLogger(__name__)


def build_field_index(client: TrinoClient, schemas: list[str], output_path: Path) -> None:
    """将 schema 列表同步为字段索引 Markdown。"""
    all_lines: list[str] = []
    total_tables = 0
    total_columns = 0
    failed_schemas: list[str] = []

    for schema in schemas:
        try:
            columns = client.get_columns(schema)
            if not columns:
                continue

            tables: dict[str, list[dict]] = defaultdict(list)
            for col in columns:
                tables[col["table_name"]].append(col)

            for table_name, cols in tables.items():
                all_lines.append(format_table_header(schema, table_name))
                for col in sorted(cols, key=lambda x: x["column_name"]):
                    line = format_column_line(
                        schema,
                        table_name,
                        col["column_name"],
                        col["data_type"],
                        col.get("comment") or "",
                    )
                    all_lines.append(line)
                all_lines.append("")
                total_tables += 1
                total_columns += len(cols)

            logger.info(f"Syncing {schema}... {len(tables)} tables")

        except Exception as e:
            logger.error(f"Failed to sync {schema}: {e}")
            failed_schemas.append(schema)

    content = "\n".join(all_lines).strip() + "\n"
    write_markdown(content, output_path)

    done_msg = f"Done: {len(schemas)} schemas, {total_tables} tables, {total_columns} columns"
    if failed_schemas:
        done_msg += f"\nFailed schemas: {failed_schemas} (skipped)"
    logger.info(done_msg)


def build_schema_index(client: TrinoClient, schemas: list[str], output_path: Path) -> None:
    """将 schema 列表同步为库索引 Markdown，按分层分组。"""
    by_layer: dict[str, list[str]] = defaultdict(list)
    for schema in schemas:
        layer = classify_schema(schema)
        if layer not in by_layer:
            by_layer[layer] = []
        by_layer[layer].append(schema)

    layer_order = ["cdm", "dwd", "ads", "bi", "ods"]
    all_lines: list[str] = []
    total_schemas = 0

    for layer in layer_order:
        if layer not in by_layer:
            continue
        all_lines.append(format_layer_header(layer))
        for schema in sorted(by_layer[layer]):
            all_lines.append(format_schema_index_line(schema))
            total_schemas += 1
        all_lines.append("")

    content = "\n".join(all_lines).strip() + "\n"
    write_markdown(content, output_path)
    logger.info(f"Done: {total_schemas} schemas")


def build_table_index(client: TrinoClient, schemas: list[str], output_path: Path) -> None:
    """将 schema 列表同步为表索引 Markdown，按 schema 分组。"""
    all_lines: list[str] = []
    total_tables = 0
    failed_schemas: list[str] = []

    for schema in schemas:
        try:
            tables = client.get_tables(schema)
            if not tables:
                continue
            all_lines.append(format_table_header(schema, ""))
            for table in sorted(tables):
                all_lines.append(format_table_index_line(schema, table))
                total_tables += 1
            logger.info(f"Syncing {schema}... {len(tables)} tables")
        except Exception as e:
            logger.error(f"Failed to sync {schema}: {e}")
            failed_schemas.append(schema)

    content = "\n".join(all_lines).strip() + "\n"
    write_markdown(content, output_path)

    done_msg = f"Done: {len(schemas)} schemas, {total_tables} tables"
    if failed_schemas:
        done_msg += f"\nFailed schemas: {failed_schemas} (skipped)"
    logger.info(done_msg)


def main() -> None:
    """主入口：解析参数、加载配置、同步并输出 Markdown。"""
    args = parse_args()
    config = load_config()

    client = TrinoClient()

    if args.mode == "schema":
        schemas = [args.schema]
    else:
        all_schemas = client.get_schemas()
        layer = getattr(args, 'layer', None)
        schemas = filter_schemas(all_schemas, layer=layer, blacklist=config.blacklist)

    mode = args.mode

    output_paths = {
        "field-index": Path(config.output_path_field).expanduser().resolve(),
        "schema-index": Path(config.output_path_schema).expanduser().resolve(),
        "table-index": Path(config.output_path_table).expanduser().resolve(),
    }

    for p in output_paths.values():
        p.parent.mkdir(parents=True, exist_ok=True)

    if mode == "all":
        build_schema_index(client, schemas, output_paths["schema-index"])
        build_table_index(client, schemas, output_paths["table-index"])
        build_field_index(client, schemas, output_paths["field-index"])
    elif mode == "schema-index":
        build_schema_index(client, schemas, output_paths["schema-index"])
    elif mode == "table-index":
        build_table_index(client, schemas, output_paths["table-index"])
    else:
        build_field_index(client, schemas, output_paths["field-index"])


if __name__ == "__main__":
    main()
