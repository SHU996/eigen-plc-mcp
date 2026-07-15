"""
PLC 代码校验器

对生成的 SCL/ST 代码进行语法和逻辑基础校验。
"""

import re
from typing import Any


class PLCValidator:
    """PLC 代码校验器"""

    # SCL 关键字
    SCL_KEYWORDS = [
        "FUNCTION_BLOCK", "END_FUNCTION_BLOCK",
        "FUNCTION", "END_FUNCTION",
        "VAR_INPUT", "END_VAR",
        "VAR_OUTPUT", "END_VAR",
        "VAR", "END_VAR",
        "BEGIN", "END_BEGIN",
        "IF", "THEN", "ELSE", "END_IF",
        "CASE", "OF", "END_CASE",
        "FOR", "TO", "DO", "END_FOR",
        "WHILE", "DO", "END_WHILE",
        "REPEAT", "UNTIL", "END_REPEAT",
        "TRUE", "FALSE",
        "AND", "OR", "NOT",
    ]

    # 常见语法错误模式
    ERROR_PATTERNS = [
        (r'IF\s+\w+\s+THEN\s*$', "IF语句缺少条件后的THEN关键字"),
        (r'END_IF\s*;\s*END_IF', "多余的END_IF"),
        (r':=\s*:=', "重复赋值运算符"),
        (r'"\w+"\s*:=\s*"\w+"\s*:=', "连续赋值语法错误"),
    ]

    def validate(self, code: str, plc_model: str = "S7-1200") -> dict[str, Any]:
        """完整校验 PLC 代码"""

        syntax_errors = self._check_syntax(code)
        logic_warnings = self._check_logic(code)
        structure_check = self._check_structure(code)

        overall_status = "PASS" if not syntax_errors else "FAIL"

        return {
            "status": overall_status,
            "plc_model": plc_model,
            "syntax_errors": syntax_errors,
            "logic_warnings": logic_warnings,
            "structure_check": structure_check,
            "total_errors": len(syntax_errors),
            "total_warnings": len(logic_warnings),
        }

    def quick_check(self, code: str, plc_model: str = "S7-1200") -> list[str]:
        """快速校验，返回警告列表"""

        syntax_errors = self._check_syntax(code)
        logic_warnings = self._check_logic(code)

        warnings = []
        for err in syntax_errors:
            warnings.append(f"[ERROR] {err}")
        for warn in logic_warnings:
            warnings.append(f"[WARN] {warn}")

        return warnings

    def _check_syntax(self, code: str) -> list[str]:
        """语法检查"""

        errors = []

        # 检查常见错误模式
        for pattern, message in self.ERROR_PATTERNS:
            if re.search(pattern, code):
                errors.append(message)

        # 检查 FUNCTION_BLOCK 闭合
        fb_open = len(re.findall(r'FUNCTION_BLOCK', code))
        fb_close = len(re.findall(r'END_FUNCTION_BLOCK', code))
        if fb_open != fb_close:
            errors.append(f"FUNCTION_BLOCK未闭合：打开{fb_open}次，关闭{fb_close}次")

        # 检查 IF 闭合
        if_open = len(re.findall(r'\bIF\b', code))
        if_close = len(re.findall(r'\bEND_IF\b', code))
        if if_open != if_close:
            errors.append(f"IF语句未闭合：IF {if_open}次，END_IF {if_close}次")

        # 检查 VAR 闭合
        var_open = len(re.findall(r'VAR_INPUT|VAR_OUTPUT|VAR\b', code))
        var_close = len(re.findall(r'END_VAR', code))
        if var_open != var_close:
            errors.append(f"变量声明块未闭合：VAR {var_open}次，END_VAR {var_close}次")

        return errors

    def _check_logic(self, code: str) -> list[str]:
        """逻辑检查（基础级别）"""

        warnings = []

        # 检查急停逻辑
        if "FUNCTION_BLOCK" in code and "EmergencyStop" not in code:
            warnings.append("未检测到急停(EmergencyStop)逻辑，工业场景必须包含急停保护")

        # 检查反馈信号
        if "Start" in code and not re.search(r'Running.*FB|Feedback', code):
            warnings.append("启停控制缺少运行反馈信号，建议添加设备运行状态反馈")

        # 检查变量声明完整性
        var_names = re.findall(r'"(\w+)"', code)
        declared_vars = re.findall(r'(\w+)\s*:\s*(BOOL|INT|DINT|REAL)', code)
        undeclared = set(var_names) - set(declared_vars)
        if undeclared:
            warnings.append(f"以下变量在代码中使用但可能未声明：{', '.join(list(undeclared)[:5])}")

        return warnings

    def _check_structure(self, code: str) -> dict[str, Any]:
        """结构检查"""

        return {
            "has_function_block": bool(re.search(r'FUNCTION_BLOCK', code)),
            "has_variables": bool(re.search(r'VAR_INPUT|VAR_OUTPUT', code)),
            "has_control_logic": bool(re.search(r'IF.*THEN', code)),
            "has_emergency_stop": "EmergencyStop" in code,
            "line_count": len(code.strip().split("\n")),
            "estimated_complexity": "简单" if len(code) < 500 else "中等" if len(code) < 1000 else "复杂",
        }
