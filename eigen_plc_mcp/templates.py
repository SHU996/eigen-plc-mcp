"""
PLC 代码模板库

提供 S7-1200 各工艺段的标准 SCL 代码模板。
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class PLCTemplate:
    """PLC 代码模板"""
    name: str
    process_type: str
    segment: str
    description: str
    code_template: str
    variables: list[dict[str, str]]


# ============================================================
# 菠菜初加工产线 — SCL 模板
# ============================================================

WASHING_SEGMENT = PLCTemplate(
    name="spinach_washing_segment",
    process_type="菠菜初加工",
    segment="清洗段",
    description="菠菜清洗段控制逻辑：水泵启停 + 传送带速度控制 + 急停保护",
    code_template="""// 菠菜初加工产线 — 清洗段控制逻辑
// PLC: {plc_model} | 编程语言: SCL
// 工艺段: 清洗段

FUNCTION_BLOCK "FB_WashingSegment"
{var_block}

BEGIN
    // 启动条件判断
    IF "StartSignal" AND "UpstreamConveyorRunning" AND "WaterPumpReady" AND NOT "EmergencyStop" THEN
        "WashingEnable" := TRUE;
    END_IF;

    // 停止条件判断
    IF "EmergencyStop" OR NOT "UpstreamConveyorRunning" THEN
        "WashingEnable" := FALSE;
    END_IF;

    // 水泵控制
    IF "WashingEnable" THEN
        "WaterPumpStart" := TRUE;
        // 传送带速度控制（变频器）
        "ConveyorSpeed" := {conveyor_speed};
    ELSE
        "WaterPumpStart" := FALSE;
        "ConveyorSpeed" := 0;
    END_IF;

    // 运行状态反馈
    "SegmentRunning" := "WashingEnable" AND "WaterPumpRunningFB";
END_FUNCTION_BLOCK""",
    variables=[
        {"name": "StartSignal", "type": "BOOL", "comment": "启动信号"},
        {"name": "UpstreamConveyorRunning", "type": "BOOL", "comment": "上游传送带运行状态"},
        {"name": "WaterPumpReady", "type": "BOOL", "comment": "水泵就绪信号"},
        {"name": "EmergencyStop", "type": "BOOL", "comment": "急停按钮"},
        {"name": "WashingEnable", "type": "BOOL", "comment": "清洗段使能"},
        {"name": "WaterPumpStart", "type": "BOOL", "comment": "水泵启动命令"},
        {"name": "WaterPumpRunningFB", "type": "BOOL", "comment": "水泵运行反馈"},
        {"name": "ConveyorSpeed", "type": "INT", "comment": "传送带速度设定值"},
        {"name": "SegmentRunning", "type": "BOOL", "comment": "段运行状态"},
    ],
)

CONVEYOR_SEGMENT = PLCTemplate(
    name="spinach_conveyor_segment",
    process_type="菠菜初加工",
    segment="传送段",
    description="菠菜传送段控制逻辑：传送带启停 + 速度调节 + 物料检测",
    code_template="""// 菠菜初加工产线 — 传送段控制逻辑
// PLC: {plc_model} | 编程语言: SCL
// 工艺段: 传送段

FUNCTION_BLOCK "FB_ConveyorSegment"
{var_block}

BEGIN
    // 启动条件
    IF "StartSignal" AND "DownstreamReady" AND NOT "EmergencyStop" THEN
        "ConveyorEnable" := TRUE;
    END_IF;

    // 急停或下游不就绪时停止
    IF "EmergencyStop" OR NOT "DownstreamReady" THEN
        "ConveyorEnable" := FALSE;
    END_IF;

    // 传送带运行控制
    IF "ConveyorEnable" THEN
        "ConveyorStart" := TRUE;
        "ConveyorSpeedSet" := {conveyor_speed};
    ELSE
        "ConveyorStart" := FALSE;
        "ConveyorSpeedSet" := 0;
    END_IF;

    // 物料计数
    IF "MaterialDetected" AND NOT "LastMaterialDetected" THEN
        "MaterialCounter" := "MaterialCounter" + 1;
    END_IF;
    "LastMaterialDetected" := "MaterialDetected";
END_FUNCTION_BLOCK""",
    variables=[
        {"name": "StartSignal", "type": "BOOL", "comment": "启动信号"},
        {"name": "DownstreamReady", "type": "BOOL", "comment": "下游段就绪"},
        {"name": "EmergencyStop", "type": "BOOL", "comment": "急停按钮"},
        {"name": "ConveyorEnable", "type": "BOOL", "comment": "传送段使能"},
        {"name": "ConveyorStart", "type": "BOOL", "comment": "传送带启动"},
        {"name": "ConveyorSpeedSet", "type": "INT", "comment": "传送带速度"},
        {"name": "MaterialDetected", "type": "BOOL", "comment": "物料检测传感器"},
        {"name": "LastMaterialDetected", "type": "BOOL", "comment": "上次物料检测状态"},
        {"name": "MaterialCounter", "type": "DINT", "comment": "物料计数器"},
    ],
)

SORTING_SEGMENT = PLCTemplate(
    name="spinach_sorting_segment",
    process_type="菠菜初加工",
    segment="分拣段",
    description="菠菜分拣段控制逻辑：视觉检测 + 分拣执行 + 品质分类",
    code_template="""// 菠菜初加工产线 — 分拣段控制逻辑
// PLC: {plc_model} | 编程语言: SCL
// 工艺段: 分拣段

FUNCTION_BLOCK "FB_SortingSegment"
{var_block}

BEGIN
    // 分拣使能条件
    IF "StartSignal" AND "VisionSystemReady" AND NOT "EmergencyStop" THEN
        "SortingEnable" := TRUE;
    END_IF;

    IF "EmergencyStop" THEN
        "SortingEnable" := FALSE;
    END_IF;

    // 视觉检测结果处理
    IF "VisionResultValid" THEN
        CASE "QualityGrade" OF
            0:  // A级 - 传送至精品出口
                "ActuatorA" := TRUE;
                "ActuatorB" := FALSE;
            1:  // B级 - 传送至普通出口
                "ActuatorA" := FALSE;
                "ActuatorB" := TRUE;
            2:  // C级 - 传送至废料出口
                "RejectActuator" := TRUE;
        END_CASE;
    END_IF;

    // 分拣计数统计
    IF "SortingComplete" THEN
        "SortedCounter" := "SortedCounter" + 1;
    END_IF;
END_FUNCTION_BLOCK""",
    variables=[
        {"name": "StartSignal", "type": "BOOL", "comment": "启动信号"},
        {"name": "VisionSystemReady", "type": "BOOL", "comment": "视觉系统就绪"},
        {"name": "EmergencyStop", "type": "BOOL", "comment": "急停按钮"},
        {"name": "SortingEnable", "type": "BOOL", "comment": "分拣段使能"},
        {"name": "VisionResultValid", "type": "BOOL", "comment": "视觉结果有效"},
        {"name": "QualityGrade", "type": "INT", "comment": "品质等级"},
        {"name": "ActuatorA", "type": "BOOL", "comment": "A级分拣执行器"},
        {"name": "ActuatorB", "type": "BOOL", "comment": "B级分拣执行器"},
        {"name": "RejectActuator", "type": "BOOL", "comment": "废料执行器"},
        {"name": "SortedCounter", "type": "DINT", "comment": "分拣计数"},
    ],
)

# 所有模板集合
ALL_TEMPLATES = [WASHING_SEGMENT, CONVEYOR_SEGMENT, SORTING_SEGMENT]


class TemplateLibrary:
    """PLC 代码模板库管理"""

    def __init__(self):
        self.templates: list[PLCTemplate] = ALL_TEMPLATES

    def generate(
        self,
        process_description: str,
        knowledge: dict[str, Any] | None = None,
        plc_model: str = "S7-1200",
        language: str = "SCL",
    ) -> str:
        """根据工艺描述生成 PLC 代码"""

        # 查找匹配模板
        template = self._find_matching_template(process_description)

        if template is None:
            # 无匹配模板，生成基础框架代码
            return self._generate_basic_framework(process_description, plc_model)

        # 使用知识库参数填充模板
        params = knowledge or {}
        conveyor_speed = params.get("conveyor_speed", 50)
        var_block = self._format_var_block(template.variables)

        code = template.code_template.format(
            plc_model=plc_model,
            conveyor_speed=conveyor_speed,
            var_block=var_block,
        )

        return code

    def list_templates(
        self,
        process_type: str | None = None,
        segment: str | None = None,
    ) -> list[dict[str, Any]]:
        """列出可用模板"""
        results = []
        for t in self.templates:
            if process_type and t.process_type != process_type:
                continue
            if segment and t.segment != segment:
                continue
            results.append(
                {
                    "name": t.name,
                    "process_type": t.process_type,
                    "segment": t.segment,
                    "description": t.description,
                    "variables_count": len(t.variables),
                }
            )
        return results

    def _find_matching_template(self, description: str) -> PLCTemplate | None:
        """根据描述查找匹配模板"""
        keywords_map = {
            WASHING_SEGMENT: ["清洗", "wash", "水", "pump", "水泵"],
            CONVEYOR_SEGMENT: ["传送", "conveyor", "输送", "transport"],
            SORTING_SEGMENT: ["分拣", "sort", "分类", "grade", "品质"],
        }

        for template, keywords in keywords_map.items():
            if any(kw in description.lower() for kw in keywords):
                return template

        return None

    def _generate_basic_framework(self, description: str, plc_model: str) -> str:
        """生成基础框架代码（无匹配模板时）"""
        return f"""// 自动生成的 PLC 控制逻辑框架
// PLC: {plc_model} | 编程语言: SCL
// 工艺描述: {description}

FUNCTION_BLOCK "FB_CustomSegment"
VAR_INPUT
    StartSignal : BOOL;     // 启动信号
    EmergencyStop : BOOL;   // 急停按钮
END_VAR

VAR_OUTPUT
    SegmentRunning : BOOL;  // 运行状态
END_VAR

BEGIN
    // TODO: 根据具体工艺需求补充控制逻辑
    IF "StartSignal" AND NOT "EmergencyStop" THEN
        "SegmentRunning" := TRUE;
    ELSE
        "SegmentRunning" := FALSE;
    END_IF;
END_FUNCTION_BLOCK"""

    def _format_var_block(self, variables: list[dict[str, str]]) -> str:
        """格式化变量声明块"""
        lines = []
        lines.append("VAR_INPUT")
        for v in variables:
            if "Signal" in v["name"] or "Stop" in v["name"] or "Ready" in v["name"] or "Detected" in v["name"]:
                lines.append(f'    {v["name"]} : {v["type"]};   // {v["comment"]}')
        lines.append("END_VAR")
        lines.append("")
        lines.append("VAR_OUTPUT")
        for v in variables:
            if "Enable" in v["name"] or "Start" in v["name"] or "Running" in v["name"] or "Counter" in v["name"]:
                lines.append(f'    {v["name"]} : {v["type"]};   // {v["comment"]}')
        lines.append("END_VAR")

        return "\n".join(lines)
