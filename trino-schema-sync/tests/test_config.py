# coding: utf-8
"""配置加载测试。"""

import pytest
from pathlib import Path
from src.config import (
    load_config,
    DEFAULT_OUTPUT_PATH_FIELD,
    DEFAULT_OUTPUT_PATH_SCHEMA,
    DEFAULT_OUTPUT_PATH_TABLE,
)


def test_load_config_with_all_paths(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "output_path_field: /tmp/fields.md\n"
        "output_path_schema: /tmp/schemas.md\n"
        "output_path_table: /tmp/tables.md\n"
        "blacklist:\n  - foo\n  - bar"
    )
    config = load_config(config_file)
    assert config.output_path_field == "/tmp/fields.md"
    assert config.output_path_schema == "/tmp/schemas.md"
    assert config.output_path_table == "/tmp/tables.md"
    assert config.blacklist == ["foo", "bar"]


def test_load_config_defaults(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    config_dir = tmp_path / ".config" / "trino-schema-sync"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text("blacklist:\n  - foo")
    config = load_config(config_file)
    assert config.output_path_field == DEFAULT_OUTPUT_PATH_FIELD
    assert config.output_path_schema == DEFAULT_OUTPUT_PATH_SCHEMA
    assert config.output_path_table == DEFAULT_OUTPUT_PATH_TABLE


def test_load_config_file_not_found():
    config = load_config(Path("/nonexistent/config.yaml"))
    assert config.blacklist == []
    assert config.output_path_field == DEFAULT_OUTPUT_PATH_FIELD
    assert config.output_path_schema == DEFAULT_OUTPUT_PATH_SCHEMA
    assert config.output_path_table == DEFAULT_OUTPUT_PATH_TABLE
