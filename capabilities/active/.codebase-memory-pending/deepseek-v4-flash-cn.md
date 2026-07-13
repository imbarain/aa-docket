# codebase-memory-mcp (casualjim) — 高性能代码智能 MCP

评估日期：2026-06-28
GitHub: https://github.com/casualjim/codebase-memory-mcp
语言：C（静态编译，单文件二进制）
协议：MIT

## 项目定位

高性能代码智能 MCP 服务器。将代码库索引为持久化知识图谱，AI agent 不需要逐个文件 grep 即可查询代码结构和关系。

## 技术架构

- **解析引擎**：Tree-sitter AST，**158 种语言**（全部编译进二进制）
- **类型解析**：Hybrid LSP（内置轻量 C 实现，无外部 LSP server）— Python/TS/JS/JSX/TSX/PHP/C#/Go/C/C++/Java/Kotlin/Rust 共 10 种语言有类型感知解析
- **存储**：SQLite 图存储 + 内置 openCypher 解析器/规划器/执行器
- **同步**：git polling 自动增量同步
- **嵌入模型**：Nomic 本地嵌入模型（编译进二进制，无需 API key 或 Ollama）
- **部署形态**：单文件静态二进制（无 Docker、无 Python/Node/JVM 运行时）

## 架构分层

| 层 | 职能 |
|----|------|
| `src/main.c` | 入口 — MCP stdio server + CLI + 安装/更新 |
| `src/mcp/` | JSON-RPC 2.0 MCP 实现，14 个工具 |
| `src/pipeline/` | 多 pass 索引（结构→定义→调用→HTTP→配置→测试） |
| `src/store/` | SQLite 图存储 + 遍历/搜索/Louvain 聚类 |
| `src/cypher/` | 自研 openCypher 解析器/规划器/执行器 |
| `src/discover/` | 文件发现（`.gitignore`/`.cbmignore`） |
| `src/watcher/` | git polling 后台自动同步 |
| `internal/cbm/` | vendored 158 种 Tree-sitter 语法 |

## MCP 工具清单（14 个）

索引类：`index_repository`（含自动同步）、`list_projects`、`delete_project`、`index_status`
查询类：`search_graph`（label/name/file 过滤）、`trace_call_path`（BFS 遍历 callers/callees，depth 1-5）
分析类：`detect_changes`（git diff → 影响符号 + blast radius + 风险评级）
搜索类：`search_code`（grep 式搜索）、`get_code_snippet`（按 qualified name 读取源代码）
架构类：`get_architecture`（语言/包/路由/热点/聚类/ADR）、`get_graph_schema`
ADR 管理：`manage_adr`（架构决策记录 CRUD）
Cypher 查询：`query_graph`（只读 openCypher：MATCH/WHERE/RETURN/聚合/EXISTS 子查询）
其他：`ingest_traces`（导入运行时 trace 验证 `HTTP_CALLS` 边）

## 性能数据

| 指标 | 数值 |
|------|------|
| Cypher 查询 | < 1ms |
| 名称搜索（regex） | < 10ms |
| 调用链追踪（depth=5） | < 10ms |
| 死代码检测（全图扫描） | ~150ms |
| Django 全量索引 | ~6s（49K nodes） |
| Linux kernel（28M LOC, 75K files） | ~3 分钟（4.81M nodes, 7.72M edges） |
| 二进制体积 | 单文件，约数十 MB（含所有语法 + 嵌入模型） |
| 内存 | RAM-first + LZ4 压缩，索引完成后释放回 OS |

## 独特能力（相对同类 CGC 之外的增量）

1. **Detect changes 带 blast radius** — 很适配「bounded 修改」的提交风格：做改动前先查波及范围
2. **ADR 管理** — 架构决策持久化，匹配跨 session 知识传承（复杂 skill 的业务规则、设计决策不因换 session 丢失）
3. **Claude Code 专用 hook** — PreToolUse 拦截 Grep/Glob，命中已索引符号时用 `search_graph` 结果增强上下文，但不阻塞 Read 操作（"gating Read breaks read-before-edit invariant"）

## 上下文负担估算

工具定义约 4-6K tokens/turn（14 个 MCP tool schemas，但参数比 CGC 更精简）。
Hook 的 `additionalContext` 注入是增量的且按需触发。

## 评估维度

### 优点

1. **零依赖单文件二进制** → 对「用户级安装、不碰系统环境」友好（丢 `~/.local/bin/` 即可）
2. **158 种语言** → 覆盖 Python/JS/TS/Shell 等常见栈
3. **Hybrid LSP** → 10 种主流语言有真正的类型解析，不只是文本匹配
4. **子毫秒级查询** → 日常使用无感
5. **git polling 自动同步** → 不需要手动 reindex
6. **ADR 管理** → 能解决跨 session 知识丢失
7. **Claude Code hook 设计优雅** → 不阻塞读，只在有意义时注入
8. **团队共享** → 图快照文件（`.codebase-memory/graph.db.zst`）可分享，避免重复索引

### 顾虑

1. **首次索引耗时**：一个 ~14K 文件的中型仓，首次全量索引可能要 1-2 分钟
2. **上下文固定开销**：即使不用任何 graph 工具，每次对话多 4-6K tokens
3. **Windows SmartScreen** 警告（未签名二进制）— Linux 无此问题
4. **相对较新**：社区规模不如 CGC（星标少），但代码质量看起来更高（C 语言、单二进制、实测基准透明）
5. **Hook 潜在的偶发干扰**：Grep 被注入额外数据可能改变 agent 的搜索行为，不是 100% 透明

### 当前结论

**推荐优先试水。** 比 CGC 更轻：
- 无环境维护成本（单二进制 vs Python 依赖链）
- 性能足够好（< 1ms 查询）
- ADR 功能解决跨 session 知识丢失的实际痛点
- Hook 设计不阻塞工作流

建议先在一个代表性 repo 做一周试用，评估实际上下文负担 vs 收益。

## 相关链接

- GitHub: https://github.com/casualjim/codebase-memory-mcp
- 安装：从 Releases 下载对应平台静态二进制，放 `~/.local/bin/`
- MCP 配置：添加到 MCP 客户端的 `mcpServers` 块
