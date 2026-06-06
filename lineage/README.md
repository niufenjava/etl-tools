# ETL 表血缘分析工具

解析 `etl-sql/` 下所有 ETL 文件，提取表级血缘关系。

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
# 自动检测：有上次运行记录则增量，否则全量
python3 etl_tools.py lineage

# 强制全量
python3 etl_tools.py lineage --all

# 强制增量（必须已有运行记录）
python3 etl_tools.py lineage --incremental
```

## 输出

- `~/data/etl-tools/etl依赖图.json` - 血缘数据
- `~/data/etl-tools/etl表血缘索引.md` - 检索索引
- `~/data/etl-tools/lineage_last_run.json` - 上次运行时间
