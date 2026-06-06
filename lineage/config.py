"""配置管理：输出路径、邮件配置"""

from pathlib import Path

HOME = Path.home()

ETL_SQL_DIR = HOME / "code/etl-dw/src/main/resources/etl-sql/"
OUTPUT_DIR = HOME / "data/"

ETL_GRAPH_FILE = OUTPUT_DIR / "etl依赖图.json"
ETL_INDEX_FILE = OUTPUT_DIR / "etl表血缘索引.md"

IGNORE_DIRS = {
    "es2ods",
    "es_yummy",
    "landing2ods",
    "ods",
}

IGNORE_PATTERNS = [
    "ads-smartagent/expand",
    "ads_yummy/ads_yummy_sensors_data",
]

IGNORE_DAVINCI = {"teacat"}

MAIL_CONFIG = {
    "enabled": False,
    "smtp_host": "smtp.example.com",
    "smtp_port": 587,
    "from_addr": "etl-lineage@example.com",
    "to_addrs": ["bee@example.com"],
}
