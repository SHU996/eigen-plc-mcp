"""
KnowledgeBase 单元测试
"""

import pytest
from eigen_plc_mcp.knowledge import KnowledgeBase


@pytest.fixture
def kb():
    return KnowledgeBase()


def test_query_spinach(kb):
    """查询菠菜初加工知识"""
    result = kb.query("菠菜初加工")
    assert result["found"] is True
    assert len(result["segments"]) >= 3


def test_query_washing_segment(kb):
    """查询清洗段知识"""
    result = kb.query("菠菜初加工", segment="清洗段")
    assert result["found"] is True
    assert len(result["segments"]) == 1
    assert result["segments"][0]["segment"] == "清洗段"


def test_query_specific_parameter(kb):
    """查询特定参数"""
    result = kb.query("菠菜初加工", segment="清洗段", parameter="conveyor_speed")
    assert result["found"] is True
    assert "conveyor_speed" in result["segments"][0]["parameters"]


def test_query_unknown_type(kb):
    """查询未知产线类型"""
    result = kb.query("未知产线")
    assert result["found"] is False


def test_available_types(kb):
    """返回可用产线类型"""
    result = kb.query("未知产线")
    assert "菠菜初加工" in result["available_types"]
