# herdr 深评 — opus, 2026-11-09

> 按五维（上游健康 / 功能差异化 / 最小实测 / 成本面 / 建议）执行，含与 `stablyai/orca` 的横向对比。

## 0. 定位

`herdr`（`herdrdev/herdr`）是用 Rust 编写的面向编程 Agent 的终端多路复用器（`Apache-2.0`）。它没有在 Agent 外面再套一层重型图形 IDE，而是直接在 `tmux` / `zellij` / `wezterm-mux-server` 所在的终端复用层做升级：后台服务端持有真实 PTY 窗格，自动识别窗格内运行的 Agent 处于 `working`（执行中）、`blocked`（卡在权限审批或等待输入）还是 `idle`（空闲）状态，支持断线保活、服务端重启后自动续接 Agent 会话，并提供本地 Socket API 供插件与 Agent 编程操控。

## 1. 上游健康度

- 仓库创建于 2026-03-27，约 49.5k stars / 4.0k forks，`Apache-2.0` 许可，版本迭代活跃（`0.9.x` 系列）。
- 纯 Rust 实现（`Cargo.toml`、`crates/`），支持 Homebrew、`mise`、静态二进制与 Nix 安装。
- 无强制云账号或中继依赖：纯本地 Unix Socket 与标准 SSH 传输（`herdr --remote <host>`）。

## 2. 功能差异化（herdr vs. tmux / WezTerm mux / Orca）

| 维度 | `tmux` / `zellij` | `herdr` (`herdrdev/herdr`) | `orca` (`stablyai/orca`) |
|---|---|---|---|
| **所处层级** | 通用终端多路复用器 | 原生感知 Agent 的终端多路复用器（TUI） | 独立的全栈 Electron IDE 桌面应用 |
| **运行时体积** | 极小（C / Rust） | 小（单文件 Rust 二进制，无 Electron） | 重（Electron + Node 守护进程 + headless xterm） |
| **Agent 交互形态** | 纯原生命令行 | 纯原生命令行 + 侧边栏状态聚合（`working`/`blocked`/`idle`） | 双模式：自建 Chat UI 包装层（`claude-agent-sdk`）或终端 |
| **宿主终端自由度** | 任意终端通过 SSH/mosh 接入 | 任意标准终端模拟器均可接入 | 必须使用 Orca 桌面客户端（或配对专用 Orca 服务端） |
| **重启恢复能力** | 仅靠插件恢复布局，进程丢失 | 恢复布局 + 通过生命周期钩子自动 `resume` 续接对话 | 在 Orca 内部恢复 worktree 标签页与聊天记录 |
| **边界与附加功能** | 无 | Socket API + 轻量插件机制 | 内置 Git worktree 管理、Diff 批注、内嵌浏览器、Linear/GitHub 看板 |

`herdr` 的三个核心架构优势：
1. **零包装滞后**：Claude Code 或 Codex 发布的任何新参数、斜杠命令或交互式 TUI 界面，在 `herdr` 里当天就能原样使用，不存在第三方 Web/GUI 壳的适配延迟。
2. **注意力路由**：同时并行跑多个 Agent 时，真正的瓶颈是“一眼看出谁卡在审批弹窗等拍板、谁还在后台干活”。`herdr` 在侧边栏和 Socket API 中把这一状态做成了核心原语。
3. **显示层完全解耦**：由于 `herdr` 只是挂在后台服务上的 TUI，同一个常驻工作区可以从桌面终端、网页终端或移动端 SSH 客户端随时接入。

## 3. 最小实测

- 在隔离环境中验证 `herdr --help`、`herdr server` 生命周期与 `herdr integration status`，并结合上游源码与文档（`herdrdev/herdr`）审读。
- 核查上游 Agent 集成机制（`herdr integration install <agent>`）：通过轻量钩子注册（`SessionStart` 与状态上报），关闭客户端后窗格可在后台继续运行，服务端重启后可按记录的会话 ID 自动续接对话。
- 审读本地 Unix Socket API 与插件清单规范（`herdr-plugin.toml`）：采用结构化 JSON 请求与事件订阅协议，便于外部脚本或 Agent 编程控制窗格。

## 4. 成本面

- **钩子配置写入**：`herdr integration install <agent>` 会向对应 Agent 的配置文件（如 `~/.claude/settings.json`、`~/.codex/hooks.json`）写入钩子项。若对这些配置文件做版本管理，需注意安装器会就地修改它们。
- **版本升级重启**：升级磁盘上的二进制文件不会自动热替换正在运行的 `herdr server`（除非使用实验性的 `--handoff` 流程）；常规升级需重启服务端并在钩子协议版本演进时更新 integration。

## 5. 建议

**采纳（`imported`）。** 对于以终端和远程服务器为核心的工作流，`herdr` 用最小的运行时开销精准补齐了多 Agent 并行最缺的“状态感知、断线保活、重启续接、Socket 编排”四块拼图，且不绑定任何特定 GUI 外壳。
