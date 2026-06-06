# coding: utf-8
"""命令行参数测试。"""

import pytest
from src.cli import parse_args


def test_parse_args_default_mode():
    args = parse_args([])
    assert args.mode == "all"
    assert args.layer is None
    assert args.schema is None


def test_parse_args_mode_field_index():
    args = parse_args(["--mode", "field-index"])
    assert args.mode == "field-index"


def test_parse_args_mode_schema_index():
    args = parse_args(["--mode", "schema-index"])
    assert args.mode == "schema-index"


def test_parse_args_mode_table_index():
    args = parse_args(["--mode", "table-index"])
    assert args.mode == "table-index"


def test_parse_args_mode_all():
    args = parse_args(["--mode", "all"])
    assert args.mode == "all"


def test_parse_args_layer():
    args = parse_args(["--layer", "cdm"])
    assert args.mode == "all"
    assert args.layer == "cdm"


def test_parse_args_schema():
    args = parse_args(["--schema", "cdm_abite"])
    assert args.mode == "schema"
    assert args.schema == "cdm_abite"


def test_parse_args_mode_with_layer():
    args = parse_args(["--mode", "field-index", "--layer", "cdm"])
    assert args.mode == "field-index"
    assert args.layer == "cdm"


def test_parse_args_invalid_mode():
    with pytest.raises(SystemExit):
        parse_args(["--mode", "invalid"])


def test_parse_args_invalid_layer():
    with pytest.raises(SystemExit):
        parse_args(["--layer", "invalid"])
