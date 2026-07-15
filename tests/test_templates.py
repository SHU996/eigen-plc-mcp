"""
TemplateLibrary 单元测试
"""

import pytest
from eigen_plc_mcp.templates import TemplateLibrary


@pytest.fixture
def template_lib():
    return TemplateLibrary()


def test_list_all_templates(template_lib):
    """列出所有模板"""
    templates = template_lib.list_templates()
    assert len(templates) >= 3
    assert any(t["process_type"] == "菠菜初加工" for t in templates)


def test_list_by_process_type(template_lib):
    """按产线类型筛选模板"""
    templates = template_lib.list_templates(process_type="菠菜初加工")
    assert len(templates) == 3


def test_list_by_segment(template_lib):
    """按工艺段筛选模板"""
    templates = template_lib.list_templates(segment="清洗段")
    assert len(templates) == 1
    assert templates[0]["name"] == "spinach_washing_segment"


def test_generate_washing_code(template_lib):
    """生成清洗段代码"""
    knowledge = {"conveyor_speed": 50}
    code = template_lib.generate(
        process_description="菠菜清洗段控制逻辑",
        knowledge=knowledge,
        plc_model="S7-1200",
    )
    assert "FB_WashingSegment" in code
    assert "S7-1200" in code
    assert "WaterPumpStart" in code


def test_generate_conveyor_code(template_lib):
    """生成传送段代码"""
    code = template_lib.generate(
        process_description="传送段控制逻辑",
        plc_model="S7-1200",
    )
    assert "FB_ConveyorSegment" in code


def test_generate_sorting_code(template_lib):
    """生成分拣段代码"""
    code = template_lib.generate(
        process_description="菠菜分拣控制",
        plc_model="S7-1200",
    )
    assert "FB_SortingSegment" in code


def test_generate_basic_framework_when_no_match(template_lib):
    """无匹配模板时生成基础框架"""
    code = template_lib.generate(
        process_description="未知产线控制逻辑",
        plc_model="S7-1200",
    )
    assert "FB_CustomSegment" in code
