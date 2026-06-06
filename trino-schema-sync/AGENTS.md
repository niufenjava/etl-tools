# AGENTS.md

## 技术栈

- Python 3.9+（通过调用 MCP-Trino 二进制实现 Kerberos 认证）
- MCP-Trino 二进制（Kerberos 认证，复用 `~/my-projects/MCP-Trino/bin/mcp-trino`）
- PyYAML

## 核心文件

| 文件 | 职责 |
|------|------|
| `sync_trino_schema.py` | CLI 主入口 |
| `src/cli.py` | 命令行参数解析 |
| `src/config.py` | YAML 配置加载 |
| `src/trino_client.py` | 调用 MCP-Trino 执行 SQL |
| `src/schema_discovery.py` | Schema 发现与分层归类 |
| `src/writer.py` | Markdown 原子写 |

## 配置

- 用户级配置：`~/.config/trino-schema-sync/config.yaml`
- 项目配置：`.env`（不提交 git）

### config.yaml 示例

```yaml
output_path: "~/data/trino表结构索引.md"

blacklist:
  - test_cly
  - dw_backup
  - health_check
```

## 运行测试

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

## Kerberos 认证

通过调用 MCP-Trino 二进制实现认证，避免 Python GSSAPI（Heimdal）与阿里云 EMR MIT Kerberos 的兼容性问题。
