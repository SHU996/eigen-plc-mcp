# eigen-plc-mcp

开源工业PLC代码生成MCP Server

## 开发设置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 启动 MCP Server
python -m eigen_plc_mcp
```

## MCP 配置

在 Claude Code / Cursor / WorkBuddy 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "eigen-plc-mcp": {
      "command": "python",
      "args": ["-m", "eigen_plc_mcp"],
      "env": {
        "PLC_BRAND": "siemens",
        "PLC_MODEL": "S7-1200"
      }
    }
  }
}
```
