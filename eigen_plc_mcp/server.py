"""
eigen-plc-mcp MCP Server 主入口

基于 MCP 协议，为 AI Agent 提供工业 PLC 代码生成能力。
"""

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server

from . import __version__
from .templates import TemplateLibrary
from .knowledge import KnowledgeBase
from .validator import PLCValidator

# 创建 MCP Server 实例
server = Server("eigen-plc-mcp")

# 初始化核心组件
template_lib = TemplateLibrary()
knowledge_base = KnowledgeBase()
validator = PLCValidator()


@server.list_tools()
async def list_tools() -> list[dict[str, Any]]:
    """列出所有可用的 MCP tools"""
    return [
        {
            "name": "generate_plc_code",
            "description": "根据工艺描述生成 S7-1200 SCL/ST 代码。"
            "输入：工艺段描述、控制逻辑要求。输出：符合 TIA Portal 规范的 SCL 代码。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "process_description": {
                        "type": "string",
                        "description": "工艺段描述，如'菠菜清洗段：启动条件为上游传送带运行+水泵就绪'",
                    },
                    "plc_model": {
                        "type": "string",
                        "description": "PLC型号，默认S7-1200",
                        "default": "S7-1200",
                    },
                    "language": {
                        "type": "string",
                        "description": "编程语言，SCL或LAD",
                        "default": "SCL",
                    },
                    "process_type": {
                        "type": "string",
                        "description": "产线类型，如'菠菜初加工'",
                        "default": "通用",
                    },
                },
                "required": ["process_description"],
            },
        },
        {
            "name": "validate_plc_code",
            "description": "校验 PLC 代码的语法正确性和逻辑合理性。"
            "支持 SCL/ST 代码的基础语法检查和逻辑验证。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "待校验的 PLC SCL 代码",
                    },
                    "plc_model": {
                        "type": "string",
                        "description": "PLC型号",
                        "default": "S7-1200",
                    },
                },
                "required": ["code"],
            },
        },
        {
            "name": "query_process_knowledge",
            "description": "查询产线工艺知识库。"
            "支持菠菜初加工、食品加工等产线的工艺参数、控制策略查询。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "process_type": {
                        "type": "string",
                        "description": "产线类型，如'菠菜初加工'",
                    },
                    "segment": {
                        "type": "string",
                        "description": "工艺段，如'清洗段'、'传送段'、'分拣段'",
                    },
                    "parameter": {
                        "type": "string",
                        "description": "查询的工艺参数，如'温度范围'、'传送带速度'",
                    },
                },
                "required": ["process_type"],
            },
        },
        {
            "name": "list_templates",
            "description": "列出可用的 PLC 代码模板。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "process_type": {
                        "type": "string",
                        "description": "按产线类型筛选模板",
                    },
                    "segment": {
                        "type": "string",
                        "description": "按工艺段筛选模板",
                    },
                },
            },
        },
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[dict[str, Any]]:
    """处理 tool 调用"""

    if name == "generate_plc_code":
        process_desc = arguments["process_description"]
        plc_model = arguments.get("plc_model", "S7-1200")
        language = arguments.get("language", "SCL")
        process_type = arguments.get("process_type", "通用")

        # 从知识库获取工艺参数
        knowledge = knowledge_base.query(process_type, process_desc)

        # 生成代码
        code = template_lib.generate(
            process_description=process_desc,
            knowledge=knowledge,
            plc_model=plc_model,
            language=language,
        )

        return [
            {
                "type": "text",
                "text": json.dumps(
                    {
                        "code": code,
                        "plc_model": plc_model,
                        "language": language,
                        "process_type": process_type,
                        "knowledge_used": knowledge,
                        "warnings": validator.quick_check(code, plc_model),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
            }
        ]

    elif name == "validate_plc_code":
        code = arguments["code"]
        plc_model = arguments.get("plc_model", "S7-1200")

        result = validator.validate(code, plc_model)

        return [
            {
                "type": "text",
                "text": json.dumps(result, ensure_ascii=False, indent=2),
            }
        ]

    elif name == "query_process_knowledge":
        process_type = arguments["process_type"]
        segment = arguments.get("segment")
        parameter = arguments.get("parameter")

        result = knowledge_base.query(process_type, segment, parameter)

        return [
            {
                "type": "text",
                "text": json.dumps(result, ensure_ascii=False, indent=2),
            }
        ]

    elif name == "list_templates":
        process_type = arguments.get("process_type")
        segment = arguments.get("segment")

        templates = template_lib.list_templates(process_type, segment)

        return [
            {
                "type": "text",
                "text": json.dumps(templates, ensure_ascii=False, indent=2),
            }
        ]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """启动 MCP Server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(
                version=__version__,
            ),
        )


def run():
    """入口函数"""
    asyncio.run(main())


if __name__ == "__main__":
    run()
