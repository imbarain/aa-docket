---
name: orca
state: rejected
last_assessed: 2026-11-09
github: https://github.com/stablyai/orca
---

# stablyai/orca — Electron Agent Development Environment (ADE) for parallel worktrees

- [opus](./.orca-rejected/opus.md) — 2026-11-09 · [📁](./.orca-rejected/)

## Reason (rejected)

**English**

Not adopted; the multi-agent multiplexing requirement is covered at a lower cost by **[herdr](../active/herdr-imported.md)**.

1. **Monolithic Electron IDE vs. composable terminal runtime**: `orca` (`stablyai/orca`, MIT) bundles an Electron desktop GUI, a custom Chat UI wrapper, automated Git worktree creation, an embedded browser with DOM picker, diff annotation, mobile emulator integration, and Linear/GitHub task boards into a single heavy application. Adopting it requires moving the entire daily editing and terminal workflow inside Orca's GUI.
2. **Scope overlap with modular CLI stacks**: worktree isolation, diff inspection, browser automation, and session persistence can already be composed from standard, single-purpose tools (`git worktree`, standard code editors, browser automation CLIs, and `herdr`).
3. **Wrapper maintenance and runtime overhead**: Orca's native chat mode translates CLI agent streams through SDK/process-host bridges (`@anthropic-ai/claude-agent-sdk`, `node-pty`, headless `xterm`), adding memory overhead and a compatibility surface whenever upstream CLIs introduce new interactive features.

**Re-assessment conditions (any one)**:
1. A workflow emerges that requires non-terminal users to review line-level agent diffs and manage GitHub/Linear tasks inside a single standalone desktop GUI;
2. Orca extracts its remote process-host / worktree daemon as a lightweight headless CLI usable from standard terminal emulators without the Electron shell.

---

**中文**

不予引入；多 Agent 并行与状态管理需求已由更轻量的 **[herdr](../active/herdr-imported.md)** 覆盖。

1. **全栈重型 Electron IDE 与可组合终端工具链冲突**：`orca`（`stablyai/orca`，MIT）把桌面 GUI、自建 Chat UI 包装层、Git worktree 自动管理、带 DOM 取色器的内嵌浏览器、行级 Diff 批注、模拟器控制以及 Linear/GitHub 任务看板全部打包进一个庞大的 Electron 应用。引入它意味着必须把日常终端和编辑器工作流整体搬进 Orca 客户端。
2. **与模块化工具链重叠度高**：分支隔离（`git worktree`）、代码审阅（标准编辑器）、浏览器自动化以及多 Agent 会话保活（`herdr`）均可通过单一职责的通用工具组合完成，无需再叠一层全家桶。
3. **包装层滞后与资源开销**：Orca 的 Chat UI 模式通过 SDK 与进程桥接（`@anthropic-ai/claude-agent-sdk`、`node-pty`、`@xterm/headless`）转译 Agent 输出，既增加了常驻内存开销，又在上游 CLI 更新交互特性时多出一层适配滞后。

**重评条件（满足任一）**：
1. 出现需要在单一独立桌面 GUI 内完成“看板派单 → 自动建 worktree → 行级 Diff 批注打回”的纯图形化工作流需求；
2. Orca 将其远程进程宿主与 worktree 调度核心拆分为脱离 Electron 外壳、可在标准终端内独立使用的轻量 CLI。
