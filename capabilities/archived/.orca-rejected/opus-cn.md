# orca 深评 — opus, 2026-11-09

> 按五维（上游健康 / 功能差异化 / 最小实测 / 成本面 / 建议）执行，并与 `herdrdev/herdr` 做直接对照。

## 0. 定位

`orca`（`stablyai/orca`，`orca.dev` / `onorca.dev`）定位为 **Agent Development Environment (ADE，Agent 开发环境)**——一款基于 Electron 的全功能桌面客户端（配套 iOS/Android 移动端与远程服务端守护进程），主打在隔离的 Git worktree 中并行调度多支编程 Agent 舰队。它直接复用用户本机已订阅登录的 CLI（Claude Code、Codex、Gemini CLI、Kimi 等），支持在图形化 Chat UI 与内嵌终端之间无缝切换同一段对话。

## 1. 上游健康度

- 仓库创建于 2026-03-17，约 119.6k stars / 7.6k forks，`MIT` 许可，由 Stably AI 团队高频维护（`v1.4.x`）。
- 基于 TypeScript 构建（`electron-vite`、React 渲染进程、Zustand 状态管理、`node-pty`、`@xterm/headless`、`@anthropic-ai/claude-agent-sdk`）。
- 仓库自身的工程门禁非常扎实：配备严密的 `oxlint` 规则、`ast-grep` 结构化扫描、Vitest 测试集，以及针对渲染器状态扇出、终端流控背压与守护进程冷启动的专项基准测试。

## 2. 功能差异化（Orca vs. herdr）

`orca` 和 `herdr` 解决的是同一个时代痛点：**当单个编程 Agent 任务耗时数十分钟、需要同时并行跑多个 Agent 时，如何管理会话、感知谁卡在审批、以及如何跨设备续接**。但两者的架构路线截然相反：

1. **自顶向下的全栈 IDE 替代（`orca`）vs. 自底向上的终端复用底座（`herdr`）**：
   - `orca` 试图用一个 Electron 客户端同时替代你的终端模拟器、Git 客户端、Diff 审查器、本地调试浏览器与任务看板。在 Orca 中发起任务会自动创建 Git worktree，支持对 AI 改动逐行写批注打回修改，还能在内嵌浏览器中点选 DOM 元素把样式和选择器直接塞进 Agent 对话框。
   - `herdr` 则严格守在终端复用层：只是一个单文件 Rust 程序，负责管理后台 PTY 窗格、聚合并高亮各窗格 Agent 的忙闲/阻塞状态，直接跑在你已有的任何终端或编辑器工作台中。
2. **Chat UI 抽象包装 vs. 原生 PTY 保真**：
   - `orca` 提供“Chat 或 Terminal”双视图，通过 `@anthropic-ai/claude-agent-sdk` 与 `@orca/process-host` 将命令行对话映射为图形气泡，并内置 Coordinator → Worker 任务拆解。
   - `herdr` 不解析也不重绘对话内容，窗格里永远是 100% 原生的 CLI 进程。

## 3. 最小实测

- 审读 `v1.4.214` 源码树、工作区配置（`package.json`、`electron.vite.config.ts`、`orca.yaml`）及性能基准测试集。
- 从源码树可清晰看到全栈 GUI 路线的复杂度代价：为了在 Electron 主进程/渲染进程、`@xterm/headless` 状态序列化、远程 SSH/WSL 中继以及多 worktree 文件监听之间维持流畅度，项目不得不维护大量专门针对主线程卡顿、终端流控确认（ack pacing）和批量打开远程会话假死的修复与压测套件（如 `remote-session-bulk-open-freeze-repro`）。

## 4. 成本面

- **重型运行时与客户端绑定**：必须运行独立的 Electron 桌面端及配套 Node 宿主进程，无法嵌入 Ghostty、Alacritty、WezTerm 等轻量原生终端，也不兼容标准 `mosh` 极简工作流。
- **遥测默认开启**：内置 `posthog-node`（文档提供关闭选项，但默认开启）。
- **功能高度冗余**：对于已经通过独立 CLI/Skill 管理 worktree、代码审查和浏览器自动化的工作流，Orca 捆绑的 80% 图形组件属于重复建设。

## 5. 建议

**不予引入（`rejected`），选用 `herdr`。** 如果用户希望装一个开箱即用的图形客户端来一揽子托管 worktree、聊天窗口、Diff 批注和网页预览，`orca` 是目前完成度极高的开源方案；但对于追求轻量、可组合、跨 SSH 多端接入的终端工作流，`herdr` 以极小的体积和零包装损耗提供了核心所需的全部多 Agent 复用能力。
