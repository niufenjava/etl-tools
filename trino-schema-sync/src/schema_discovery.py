"""Schema 发现与分层归类。"""

from typing import Literal

LAYER_RULES: dict[str, list[str]] = {
    "cdm": ["cdm_"],
    "dwd": ["dwd_"],
    "bi": ["ads_cotti_", "ads_dashboard", "ads_dj_", "ads_manage_"],
    "ads": ["ads_"],
    "ods": ["ods_", "landing_"],
}

Layer = Literal["cdm", "dwd", "ads", "bi", "ods"]

def classify_schema(schema_name: str) -> str:
    for layer, prefixes in LAYER_RULES.items():
        for prefix in prefixes:
            if schema_name.startswith(prefix) or schema_name.startswith(prefix.replace("_", "")):
                # When the prefix has trailing underscore (e.g. "landing_"), strip it so that
                # "landing_events" matches via startswith("landing") — handles cases where
                # schema names don't follow the expected underscore pattern.
                return layer
    return "other"

def filter_schemas(schemas: list[str], layer: Layer | None, blacklist: list[str]) -> list[str]:
    result = []
    for schema in schemas:
        if schema in blacklist:
            continue
        if layer is not None and classify_schema(schema) != layer:
            continue
        result.append(schema)
    return result
