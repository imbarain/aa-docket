---
name: herdr
state: imported
last_assessed: 2026-11-09
github: https://github.com/herdrdev/herdr
---

# herdrdev/herdr — agent-aware terminal multiplexer and persistent session runtime

- [opus](./.herdr-imported/opus.md) — 2026-11-09 · [📁](./.herdr-imported/)

## Decision (imported)

**English**

Adopted as the persistent terminal runtime for CLI coding agents.

1. **Owns terminals without wrapping agents**: `herdr` runs as a single Rust binary (`Apache-2.0`) that manages real PTY panes in a background server while leaving each CLI agent (e.g., Claude Code, Codex, Cursor, OpenCode) completely un-wrapped. Native authentication, hooks, skills, and TUI rendering work without an intermediate translation layer.
2. **Agent state awareness and session restore**: tracks per-pane agent state (`working`, `blocked`, `idle`) in a unified sidebar and restores workspace layouts plus supported agent conversations across server restarts via lifecycle hooks.
3. **Programmatic socket API**: exposes a local socket and CLI so agents and plugins can inspect pane metadata, spawn or split panes, and wait on peer tasks without fragile `tmux send-keys` scraping.
4. **Head-to-head vs. [orca](../archived/orca-rejected.md)**: `herdr` solves multi-agent concurrency at the **multiplexer layer** inside any existing terminal emulator with minimal memory overhead, whereas `stablyai/orca` requires adopting a full standalone Electron IDE.

---

**中文**

采纳作为 CLI 编程 Agent 的持久化终端运行时。

1. **接管终端而不包装 Agent**：`herdr` 是单文件 Rust 二进制（`Apache-2.0`），在后台服务端管理真实 PTY 窗格，对窗格内的 CLI Agent（如 Claude Code、Codex、Cursor、OpenCode）零包装。原生登录态、hooks、skills 与终端渲染直接生效，无中间转译损耗。
2. **Agent 状态感知与会话恢复**：在侧边栏实时聚合各窗格的 `working`、`blocked`（等待人工确认）、`idle` 状态；配合生命周期钩子，服务端重启后可恢复工作区布局并自动续接各 Agent 会话。
3. **可编程 Socket API**：提供本地 Socket 与 CLI 接口，支持插件与 Agent 结构化查询窗格元数据、拆分窗格或等待协作任务完成，无需依赖脆弱的 `tmux send-keys` 盲注。
4. **对照 [orca](../archived/orca-rejected.md)**：`herdr` 在**终端复用层**解决多 Agent 并行与断线保活，可直接跑在任意现有终端中且内存开销极低；而 `stablyai/orca` 要求迁入整套独立的 Electron 桌面 IDE。
