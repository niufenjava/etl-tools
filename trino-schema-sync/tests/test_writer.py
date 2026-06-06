"""Markdown 文件写入的测试。"""

import pytest
from pathlib import Path
from src.writer import write_markdown, format_table_header, format_column_line


def test_format_column_line():
    """格式化列信息为可读行。"""
    result = format_column_line("cdm_a", "dim_shop", "shop_id", "varchar", "门店ID")
    assert result == "cdm_a.dim_shop.shop_id varchar — 门店ID"


def test_format_table_header():
    """格式化表头为二级标题。"""
    result = format_table_header("cdm_a", "dim_shop")
    assert result == "## cdm_a.dim_shop"


def test_write_markdown_atomic(tmp_path):
    """原子写入：先写 .tmp，再 rename，完成后无残留。"""
    output_path = tmp_path / "test.md"
    content = "## cdm_a.dim_shop\ncdm_a.dim_shop.shop_id varchar — 门店ID\n"
    write_markdown(content, output_path)
    assert output_path.exists()
    assert output_path.read_text() == content
    assert not (tmp_path / "test.md.tmp").exists()
