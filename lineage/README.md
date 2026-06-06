# ETL 表血缘分析工具

解析 `etl-sql/` 下所有 ETL 文件，提取表级血缘关系。

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
python etl_lineage.py --all
```

## 输出

- `~/data/etl依赖图.json` - 血缘数据
- `~/data/etl表血缘索引.md` - 检索索引
