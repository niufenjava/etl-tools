"""配置加载：YAML 配置文件 + 默认值。"""

from dataclasses import dataclass
from pathlib import Path
import yaml

DEFAULT_OUTPUT_PATH_FIELD = "~/data/trino表结构字段索引.md"
DEFAULT_OUTPUT_PATH_SCHEMA = "~/data/trino库索引.md"
DEFAULT_OUTPUT_PATH_TABLE = "~/data/trino表索引.md"


@dataclass(frozen=True)
class Config:
    output_path_field: str
    output_path_schema: str
    output_path_table: str
    blacklist: list[str]


def load_config(config_file: Path | None = None) -> Config:
    if config_file is None:
        config_file = Path.home() / ".config" / "trino-schema-sync" / "config.yaml"

    if not config_file.exists():
        return Config(
            output_path_field=DEFAULT_OUTPUT_PATH_FIELD,
            output_path_schema=DEFAULT_OUTPUT_PATH_SCHEMA,
            output_path_table=DEFAULT_OUTPUT_PATH_TABLE,
            blacklist=[],
        )

    with open(config_file, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return Config(
        output_path_field=data.get("output_path_field", DEFAULT_OUTPUT_PATH_FIELD),
        output_path_schema=data.get("output_path_schema", DEFAULT_OUTPUT_PATH_SCHEMA),
        output_path_table=data.get("output_path_table", DEFAULT_OUTPUT_PATH_TABLE),
        blacklist=data.get("blacklist", []),
    )
