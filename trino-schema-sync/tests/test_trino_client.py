# coding: utf-8
"""trino_client 模块测试（subprocess 调用 MCP-Trino）。"""

import pytest
from unittest.mock import patch, MagicMock
from src.trino_client import (
    TrinoClient,
    get_env_host,
    get_env_port,
    get_env_user,
    get_env_catalog,
)


def test_get_env_host_default():
    with patch.dict("os.environ", {}, clear=True):
        assert get_env_host() == "trinoaliyunprod01.yummy.tech"


def test_get_env_port_default():
    with patch.dict("os.environ", {}, clear=True):
        assert get_env_port() == 8288


def test_get_env_host_custom():
    with patch.dict("os.environ", {"TRINO_HOST": "custom.trino.com"}):
        assert get_env_host() == "custom.trino.com"


def test_get_env_user_default():
    with patch.dict("os.environ", {}, clear=True):
        assert get_env_user() is None


def test_get_env_catalog_default():
    with patch.dict("os.environ", {}, clear=True):
        assert get_env_catalog() == "hive"


class TestTrinoClient:
    @patch("src.trino_client.subprocess.run")
    def test_query(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"Rows": [{"a": 1, "b": 2}], "Truncated": false, "MaxRows": 10000}',
            stderr="",
        )
        client = TrinoClient()
        result = client.query("SELECT 1")
        assert result == [{"a": 1, "b": 2}]
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[-1] == "SELECT 1"

    @patch("src.trino_client.subprocess.run")
    def test_query_error(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="query failed")
        client = TrinoClient()
        with pytest.raises(RuntimeError, match="MCP-Trino error"):
            client.query("SELECT 1")

    @patch("src.trino_client.subprocess.run")
    def test_get_schemas(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"Rows": [{"schema_name": "cdm_a"}, {"schema_name": "dwd_b"}], "Truncated": false, "MaxRows": 10000}',
            stderr="",
        )
        client = TrinoClient()
        result = client.get_schemas()
        assert result == ["cdm_a", "dwd_b"]

    @patch("src.trino_client.subprocess.run")
    def test_get_columns(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"Rows": [{"table_name": "t1", "column_name": "c1", "data_type": "varchar", "comment": "note"}], "Truncated": false, "MaxRows": 10000}',
            stderr="",
        )
        client = TrinoClient()
        result = client.get_columns("cdm_a")
        assert len(result) == 1
        assert result[0]["column_name"] == "c1"

    @patch("src.trino_client.subprocess.run")
    def test_get_tables(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"Rows": [{"table_name": "dim_shop"}, {"table_name": "dim_user"}], "Truncated": false, "MaxRows": 10000}',
            stderr="",
        )
        client = TrinoClient()
        result = client.get_tables("cdm_a")
        assert result == ["dim_shop", "dim_user"]
