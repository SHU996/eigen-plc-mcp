"""
PLCValidator 单元测试
"""

import pytest
from eigen_plc_mcp.validator import PLCValidator


@pytest.fixture
def validator():
    return PLCValidator()


def test_validate_valid_code(validator):
    """校验有效代码"""
    code = """
FUNCTION_BLOCK "FB_Test"
VAR_INPUT
    StartSignal : BOOL;
END_VAR
VAR_OUTPUT
    Running : BOOL;
END_VAR
BEGIN
    IF "StartSignal" THEN
        "Running" := TRUE;
    ELSE
        "Running" := FALSE;
    END_IF;
END_FUNCTION_BLOCK
"""
    result = validator.validate(code)
    assert result["status"] == "PASS"


def test_validate_missing_end_if(validator):
    """检测缺失的 END_IF"""
    code = """
FUNCTION_BLOCK "FB_Test"
VAR_INPUT
    StartSignal : BOOL;
END_VAR
BEGIN
    IF "StartSignal" THEN
        "Running" := TRUE;
END_FUNCTION_BLOCK
"""
    result = validator.validate(code)
    assert result["status"] == "FAIL"
    assert any("IF语句未闭合" in e for e in result["syntax_errors"])


def test_validate_missing_emergency_stop(validator):
    """检测缺少急停逻辑"""
    code = """
FUNCTION_BLOCK "FB_Test"
VAR_INPUT
    StartSignal : BOOL;
END_VAR
BEGIN
    IF "StartSignal" THEN
        "Running" := TRUE;
    END_IF;
END_FUNCTION_BLOCK
"""
    result = validator.validate(code)
    assert any("急停" in w for w in result["logic_warnings"])


def test_quick_check(validator):
    """快速校验"""
    code = """IF "Start" THEN "Run" := TRUE; END_IF;"""
    warnings = validator.quick_check(code)
    assert isinstance(warnings, list)


def test_structure_check(validator):
    """结构检查"""
    code = """
FUNCTION_BLOCK "FB_Test"
VAR_INPUT EmergencyStop : BOOL; END_VAR
BEGIN
    IF NOT "EmergencyStop" THEN
        "Running" := TRUE;
    END_IF;
END_FUNCTION_BLOCK
"""
    result = validator.validate(code)
    structure = result["structure_check"]
    assert structure["has_function_block"] is True
    assert structure["has_emergency_stop"] is True
