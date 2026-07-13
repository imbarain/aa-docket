# CodeGraphContext (CGC) — 代码知识图谱 MCP

评估日期：2026-06-28
GitHub: https://github.com/CodeGraphContext/CodeGraphContext
星标：~3.8k
语言：Python
协议：MIT

## 项目定位

将本地代码索引为图数据库，通过 MCP 暴露给 AI 助手。同时提供 CLI 独立使用。

## 技术架构

- **解析引擎**：Tree-sitter AST 解析，支持 23 种语言
- **图数据库**：FalkorDB Lite（默认 Unix）/ KuzuDB（跨平台）/ LadybugDB / Neo4j / Nornic
- **MCP 协议**：JSON-RPC 2.0 over stdio
- **可选增强**：SCIP 索引（C/C++/C# 需 `compile_commands.json`）

## MCP 工具清单（14 tools + 4 resources + 6 prompts）

索引类：`index_project`、`list_projects`、`delete_project`
查询类：`search_code`、`trace_calls`、`find_callers`、`find_callees`、`impact_analysis`
分析类：`dead_code_detection`、`complexity_analysis`、`get_architecture`
可视化：交互式 HTML 图（force-directed layout）

## 与 LSP 的差异点

| 能力 | LSP | CGC |
|------|-----|-----|
| 跳转定义 | ✅ | ❌ 冗余 |
| 查找引用 | ✅ | ❌ 冗余 |
| 调用链 | ❌ | ✅ BFS 多级调用链 |
| 影响分析 | ❌ | ✅ 改 X 波及范围 |
| 死代码 | ❌ | ✅ |
| 架构总览 | ❌ | ✅ 包/模块/热点图 |

## 上下文负担估算

工具定义约 5-8K tokens/turn（14 个 MCP tool schemas）。
结果返回视查询复杂度，调用链可额外带 1-3K tokens。

## 评估维度

### 优点
1. 最成熟的开源实现（3.8k ★，活跃社区）
2. CLI + MCP 双模式
3. GraphRAG（Louvain 社区检测 + 全局/局部搜索）
4. 零配置起步（SQLite embedded）
5. 索引速度 100K 行 < 30s，增量 < 2s

### 顾虑
1. **Python 生态依赖**：tree-sitter + 图 DB SDK → 需维护 Python 环境
2. **已知 bug**：repo 内有 `CGC_E2E_BUG_REPORT.md`、`CGC_GRAPH_INCONSISTENCIES.md`，说明有已承认的问题
3. **Python 3.13 兼容**：Tree-sitter 在 3.13 标记为 "not installed"
4. **C/C++ SCIP 索引**：需要完整构建系统 + `compile_commands.json`，门槛高，失败则静默降级
5. **23 语言覆盖**但很多语言是浅层文本解析（非 Hybrid LSP 类型推导）
6. **多 DB 后端**增加配置复杂度，嵌入式 DB 在大规模场景可能不够（推荐 Neo4j 用于 "Enterprise"）
7. 工具 schema 偏重 → 上下文开销在上界（~8K tokens）

### 当前结论

功能上确实补了 LSP 的空白，但对以 bounded 修改（一 commit 一逻辑）为主的工作流：
- impact analysis 使用频率低
- 中等量级代码库（~数十万行）还没到非图不可
- Python 依赖链和已知 bug 增加维护负担
- 决策：**观望，不急于引入**。如果之后遇到频繁跨模块重构的场景再重新评估。

## 相关链接

- GitHub: https://github.com/CodeGraphContext/CodeGraphContext
- PyPI: https://pypi.org/project/codegraphcontext/
