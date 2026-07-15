# eigen-plc-mcp

> 开源工业PLC代码生成MCP Server —— 开源版西门子 Eigen Engineering Agent

基于 MCP（Model Context Protocol）协议，为工业自动化场景提供智能 PLC 代码生成、调试与验证能力。

## 为什么做这个项目？

2026年7月，西门子在 WAIC（世界人工智能大会）发布 **Eigen Engineering Agent** —— 全球首款可独立编写 PLC 代码的工业 AI 智能体。但它：

- ❌ 仅支持西门子自家 PLC（S7-1200/S7-1500）
- ❌ 闭源、昂贵、不可定制
- ❌ 无法与第三方 AI Agent 工具链集成

**eigen-plc-mcp** 要做的事：

- ✅ 开源、免费、可定制
- ✅ 基于标准 MCP 协议，可与任何 AI Agent 集成
- ✅ 支持 S7-1200（TIA Portal）为起点，逐步扩展
- ✅ 将 PLC 编程经验沉淀为可复用的知识库

## 核心能力

| 能力 | 说明 | 状态 |
|------|------|------|
| PLC 代码生成 | 根据工艺描述自动生成 SCL/ST 代码 | 🔜 MVP |
| PLC 代码校验 | 语法检查 + 逻辑验证 | 🔜 MVP |
| 工艺知识库 | 菠菜/食品加工产线工艺参数 | 🔜 MVP |
| TIA Portal 集成 | 通过 MCP 调用 TIA Portal API | 📋 Roadmap |
| 多品牌支持 | 三菱、欧姆龙、AB 等 | 📋 Roadmap |
| HMI 界面生成 | 自动生成 HMI 画面 | 📋 Roadmap |

## 快速开始

### 安装

```bash
pip install eigen-plc-mcp
```

### 配置 MCP Client

在 Claude Code / Cursor / WorkBuddy 等工具的 MCP 配置中添加：

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

### 使用示例

在 AI Agent 对话中：

```
请为菠菜初加工产线编写 S7-1200 的清洗段控制逻辑：
- 启动条件：上游传送带运行信号 + 水泵就绪
- 停止条件：急停按钮 + 传送带停止
- 输出：水泵启停 + 传送带速度控制
```

MCP Server 将自动生成符合 TIA Portal 规范的 SCL 代码。

## 技术架构

```
┌─────────────────────────────────┐
│         AI Agent (LLM)          │
│    Claude / GPT / Qwen / ...   │
└────────────┬────────────────────┘
             │ MCP Protocol
┌────────────▼────────────────────┐
│      eigen-plc-mcp Server       │
│  ┌──────────┐  ┌──────────────┐ │
│  │Code Gen  │  │ Knowledge    │ │
│  │Engine    │  │ Base         │ │
│  └──────────┘  └──────────────┘ │
│  ┌──────────┐  ┌──────────────┐ │
│  │Validator │  │ Template     │ │
│  │          │  │ Library      │ │
│  └──────────┘  └──────────────┘ │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│    TIA Portal / PLC Simulator   │
└─────────────────────────────────┘
```

## 项目背景

本项目灵感来自以下背景：

- **西门子 Eigen Engineering Agent**（WAIC 2026 中国首发）
- **S7-1200 PLC 菠菜初加工产线控制系统**（毕业论文题目）
- **MCP 协议生态**（AI Agent 与工业系统的标准桥梁）
- **制造业 AI 落地痛点**（PLC 编程门槛高、经验难复用）

## Roadmap

### Phase 1 — MVP（预计30小时）

- [ ] MCP Server 基础框架搭建
- [ ] S7-1200 SCL 代码模板库（清洗段、传送段、分拣段）
- [ ] 菠菜初加工产线知识库
- [ ] 代码生成 tool（工艺描述 → SCL 代码）
- [ ] 代码校验 tool（语法 + 逻辑基础检查）
- [ ] README + 文档

### Phase 2 — 增强

- [ ] TIA Portal Python API 集成
- [ ] 更多产线工艺模板（食品、饮料、包装）
- [ ] PLC 代码仿真验证
- [ ] 多品牌 PLC 适配层

### Phase 3 — 产品化

- [ ] Web UI（工艺配置 → 代码生成 → 下载）
- [ ] SaaS 部署选项
- [ ] 企业版（私有部署 + 定制知识库）

## 贡献指南

欢迎贡献！特别是：

- 🏭 工业自动化领域的 PLC 编程经验
- 🔧 MCP 协议的开发与优化
- 📝 产线工艺知识库的补充
- 🧪 测试用例与边界场景

## 许可证

MIT License

## 致谢

- 西门子 Eigen Engineering Agent —— 激发了这个开源替代的灵感
- MCP 协议 —— Anthropic 开源的 AI 工具链标准
- S7-1200 社区 —— 无数的 PLC 编程经验分享

---

**如果制造业的 AI 落地是未来，那开源就是通往未来的路。**
