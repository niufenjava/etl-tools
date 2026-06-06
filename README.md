# etl-tools

数仓开发工具集。

## 工具列表

### lineage

ETL 表血缘分析工具。解析 `etl-sql/` 下所有 ETL 文件，提取表级血缘关系。

```bash
python etl_tools.py lineage --all
```

详细说明见 [lineage/README.md](lineage/README.md)

### trino-schema-sync

Trino 表结构同步工具。从 Trino 同步表结构信息（字段名、类型、注释）到 Markdown 文件。

```bash
python etl_tools.py trino-schema-sync --all
python etl_tools.py trino-schema-sync --layer cdm
python etl_tools.py trino-schema-sync --schema cdm_abite
```

详细说明见 [trino-schema-sync/README.md](trino-schema-sync/README.md)

### data-compare

数据文件比较工具。比较两个文件的 ID 集合差异，输出只在其中一个文件存在的 ID。

```bash
python etl_tools.py data-compare file1.txt file2.txt
```

详细说明见 [data-compare/data_compare.py](data-compare/data_compare.py)
