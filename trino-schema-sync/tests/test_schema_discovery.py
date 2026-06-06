"""schema_discovery 模块的测试。"""

import pytest
from src.schema_discovery import LAYER_RULES, classify_schema, filter_schemas

def test_classify_cdm():
    assert classify_schema("cdm_abite") == "cdm"

def test_classify_dwd():
    assert classify_schema("dwd_order") == "dwd"

def test_classify_ads():
    assert classify_schema("ads_user_stats") == "ads"

def test_classify_bi_dashboard():
    assert classify_schema("ads_dashboard_sales") == "bi"

def test_classify_ods():
    assert classify_schema("ods_order") == "ods"
    assert classify_schema("landing_events") == "ods"

def test_classify_unknown():
    assert classify_schema("unknown_schema") == "other"

def test_filter_schemas_blacklist():
    schemas = ["cdm_a", "test_cly", "dw_backup", "ods_b"]
    result = filter_schemas(schemas, layer=None, blacklist=["test_cly", "dw_backup"])
    assert result == ["cdm_a", "ods_b"]

def test_filter_schemas_by_layer():
    schemas = ["cdm_a", "dwd_b", "ads_c", "ods_d", "other_e"]
    result = filter_schemas(schemas, layer="cdm", blacklist=[])
    assert result == ["cdm_a"]
