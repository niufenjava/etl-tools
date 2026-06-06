"""Markdown 文件写入，原子写。

先写入 .tmp 文件，再 rename 到目标路径，避免写入中断导致文件损坏。
"""

from pathlib import Path


def format_table_header(schema: str, table: str) -> str:
    """将 schema 和 table 格式化为二级标题。"""
    return f"## {schema}.{table}"


def format_column_line(
    schema: str, table: str, column: str, data_type: str, comment: str
) -> str:
    """将列信息格式化为可读行，格式为：schema.table.column data_type — comment。"""
    return f"{schema}.{table}.{column} {data_type} — {comment}"


def format_schema_index_line(schema: str) -> str:
    """将 schema 格式化为索引行。"""
    return schema


def format_table_index_line(schema: str, table: str) -> str:
    """将表格式化为索引行。"""
    return f"{schema}.{table}"


def format_layer_header(layer: str) -> str:
    """将分层名称格式化为二级标题。"""
    return f"## {layer}"


def write_markdown(content: str, output_path: Path) -> None:
    """原子写入 Markdown 文件。

    先写入 .tmp 后缀临时文件，再 rename 到目标路径，
    确保写入过程中崩溃不会污染目标文件。
    """
    output_path = Path(output_path).expanduser()
    tmp_path = Path(str(output_path) + ".tmp")
    tmp_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.rename(output_path)
