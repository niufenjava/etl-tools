# Trino 表结构同步工具

从 Trino 同步表结构信息（字段名、类型、注释）到 Markdown 文件。

## 使用方法

```bash
# 全量同步
python sync_trino_schema.py --all

# 按分层同步
python sync_trino_schema.py --layer cdm
python sync_trino_schema.py --layer dwd
python sync_trino_schema.py --layer ads
python sync_trino_schema.py --layer bi
python sync_trino_schema.py --layer ods

# 指定 schema
python sync_trino_schema.py --schema cdm_abite
```

## 环境配置

在项目根目录创建 `.env` 文件：

```bash
TRINO_HOST=trinoaliyunprod01.yummy.tech
TRINO_USER=haijun.zhang
TRINO_KERBEROS_KEYTAB_PATH=/path/to/haijun.zhang.keytab
TRINO_KERBEROS_CONFIG_PATH=/etc/krb5-prod-ali-trino.conf
```

## 依赖

- Python 3.9+
- MCP-Trino 二进制（自动从 `~/my-projects/MCP-Trino/bin/mcp-trino` 调用）
- PyYAML
