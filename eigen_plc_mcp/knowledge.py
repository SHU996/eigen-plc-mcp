"""
产线工艺知识库

包含菠菜初加工产线等典型工艺的参数和控制策略。
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ProcessKnowledge:
    """工艺知识条目"""
    process_type: str
    segment: str
    parameters: dict[str, Any]
    control_strategy: str
    notes: str


# ============================================================
# 菠菜初加工产线知识库
# ============================================================

SPINACH_WASHING = ProcessKnowledge(
    process_type="菠菜初加工",
    segment="清洗段",
    parameters={
        "conveyor_speed": 50,        # 传送带速度 (Hz 变频器设定)
        "water_pressure": 0.3,       # 水压 (MPa)
        "water_temperature": 15,     # 水温 (°C)
        "washing_time": 30,          # 清洗时间 (s)
        "pump_power": 2.2,           # 水泵功率 (kW)
    },
    control_strategy="顺序启动：先启水泵 → 检测水压就绪 → 启传送带 → 检测物料到达",
    notes="清洗段需考虑水压联锁保护，水压低于0.15MPa时自动停泵报警",
)

SPINACH_CONVEYOR = ProcessKnowledge(
    process_type="菠菜初加工",
    segment="传送段",
    parameters={
        "conveyor_speed": 40,        # 传送带速度 (Hz)
        "conveyor_length": 5.0,      # 传送带长度 (m)
        "max_load": 50,              # 最大负载 (kg)
        "sensor_spacing": 0.5,       # 传感器间距 (m)
    },
    control_strategy="变频调速：根据下游段状态动态调整速度，下游堵料时减速",
    notes="传送段需设置物料计数器，用于产量统计和异常检测",
)

SPINACH_SORTING = ProcessKnowledge(
    process_type="菠菜初加工",
    segment="分拣段",
    parameters={
        "grading_speed": 30,         # 分拣速度 (件/min)
        "vision_delay": 200,         # 视觉系统响应延迟 (ms)
        "grade_a_ratio": 0.6,        # A级占比
        "grade_b_ratio": 0.3,        # B级占比
        "reject_ratio": 0.1,         # 废料占比
    },
    control_strategy="视觉引导分拣：视觉系统判定品质等级 → PLC执行气缸分拣动作",
    notes="分拣段需要与视觉系统通信，通常使用PROFINET或Modbus TCP",
)

# 知识库集合
KNOWLEDGE_ENTRIES = [SPINACH_WASHING, SPINACH_CONVEYOR, SPINACH_SORTING]


class KnowledgeBase:
    """产线工艺知识库"""

    def __init__(self):
        self.entries: list[ProcessKnowledge] = KNOWLEDGE_ENTRIES

    def query(
        self,
        process_type: str,
        segment: str | None = None,
        parameter: str | None = None,
    ) -> dict[str, Any]:
        """查询工艺知识"""

        # 查找匹配条目
        matches = []
        for entry in self.entries:
            if entry.process_type != process_type:
                continue
            if segment and entry.segment != segment:
                continue
            matches.append(entry)

        if not matches:
            return {
                "found": False,
                "message": f"未找到'{process_type}'相关知识，当前仅支持：菠菜初加工",
                "available_types": [e.process_type for e in self.entries],
            }

        # 提取参数
        result = {
            "found": True,
            "process_type": process_type,
            "segments": [],
        }

        for match in matches:
            segment_data = {
                "segment": match.segment,
                "parameters": match.parameters,
                "control_strategy": match.control_strategy,
                "notes": match.notes,
            }

            # 如果指定了具体参数，只返回该参数
            if parameter:
                if parameter in match.parameters:
                    segment_data["parameters"] = {
                        parameter: match.parameters[parameter]
                    }

            result["segments"].append(segment_data)

        return result
