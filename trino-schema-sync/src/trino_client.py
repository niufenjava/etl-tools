"""Trino 连接与查询：调用 MCP-Trino 二进制，解析 JSON 输出。

复用 MCP-Trino 的 Kerberos 认证能力，避免 Python GSSAPI 兼容性问题。
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


def _load_env_from_file(env_path: Path) -> None:
    """从 .env 文件加载环境变量到 os.environ。"""
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


# 尝试从项目根目录加载 .env 文件
_project_root = Path(__file__).parent.parent
_load_env_from_file(_project_root / ".env")

__all__ = [
    "TrinoClient",
    "get_env_host",
    "get_env_port",
    "get_env_user",
    "get_env_catalog",
]

DEFAULT_HOST = "trinoaliyunprod01.yummy.tech"
DEFAULT_PORT = 8288


def get_env_host() -> str:
    return os.environ.get("TRINO_HOST", DEFAULT_HOST)


def get_env_port() -> int:
    return int(os.environ.get("TRINO_PORT", str(DEFAULT_PORT)))


def get_env_user() -> str | None:
    return os.environ.get("TRINO_USER")


def get_env_catalog() -> str:
    return os.environ.get("TRINO_CATALOG", "hive")


def get_env_mcp_trino_path() -> Path:
    """MCP-Trino 二进制路径，默认从 ~/my-projects/MCP-Trino/bin/mcp-trino"""
    return Path(os.environ.get("MCP_TRINO_PATH", str(Path.home() / "my-projects/MCP-Trino/bin/mcp-trino")))


class TrinoClient:
    """Trino 数据库客户端，通过调用 MCP-Trino 二进制实现。

    复用 MCP-Trino 的 Kerberos 认证，避免 Python GSSAPI 兼容性问题。
    """

    def __init__(self):
        self.host = get_env_host()
        self.port = get_env_port()
        self.user = get_env_user()
        self.catalog = get_env_catalog()
        self._trino_path = get_env_mcp_trino_path()

    def _run(self, sql: str) -> list[dict]:
        """执行 SQL，返回 JSON 解析后的行列表。"""
        env = os.environ.copy()
        env["TRINO_HOST"] = self.host
        env["TRINO_PORT"] = str(self.port)
        if self.user:
            env["TRINO_USER"] = self.user
        env["TRINO_CATALOG"] = self.catalog
        if "TRINO_KERBEROS_KEYTAB_PATH" in os.environ:
            env["TRINO_KERBEROS_KEYTAB_PATH"] = os.environ["TRINO_KERBEROS_KEYTAB_PATH"]
        if "TRINO_KERBEROS_CONFIG_PATH" in os.environ:
            env["TRINO_KERBEROS_CONFIG_PATH"] = os.environ["TRINO_KERBEROS_CONFIG_PATH"]
        if "TRINO_KERBEROS_PRINCIPAL" in os.environ:
            env["TRINO_KERBEROS_PRINCIPAL"] = os.environ["TRINO_KERBEROS_PRINCIPAL"]

        result = subprocess.run(
            [str(self._trino_path), "--format", "json", "query", sql],
            capture_output=True,
            text=True,
            env=env,
        )
        if result.returncode != 0:
            raise RuntimeError(f"MCP-Trino error: {result.stderr.strip()}")
        data = json.loads(result.stdout)
        return data.get("Rows", [])

    def query(self, sql: str) -> list[dict]:
        return self._run(sql)

    def get_schemas(self) -> list[str]:
        rows = self.query(f"SELECT schema_name FROM {self.catalog}.information_schema.schemata")
        return [r["schema_name"] for r in rows]

    def get_columns(self, schema: str) -> list[dict]:
        sql = (
            f"SELECT table_name, column_name, data_type, comment "
            f"FROM {self.catalog}.information_schema.columns "
            f"WHERE table_schema = '{schema}'"
        )
        return self.query(sql)

    def get_tables(self, schema: str) -> list[str]:
        sql = f"SELECT table_name FROM {self.catalog}.information_schema.tables WHERE table_schema = '{schema}'"
        rows = self.query(sql)
        return [r["table_name"] for r in rows]
