# orca deep review — opus, 2026-11-09

> Executed along five dimensions (upstream health / functional differentiation / minimal hands-on test / cost surface / recommendation), contrasted directly against `herdrdev/herdr`.

## 0. Positioning

`orca` (`stablyai/orca`, `orca.dev` / `onorca.dev`) positions itself as an **Agent Development Environment (ADE)**—an all-in-one Electron desktop application (with companion iOS/Android apps and a remote server daemon) designed to run a fleet of coding agents in parallel across isolated Git worktrees. Each agent uses the user's existing CLI subscription (Claude Code, Codex, Gemini CLI, Kimi, etc.) and can be interacted with either through Orca's custom Chat UI or an embedded terminal pane.

## 1. Upstream health

- Repo created 2026-03-17; ~119.6k stars / ~7.6k forks, `MIT` license, backed by Stably AI with very high commit velocity (`v1.4.x`).
- Written in TypeScript (`electron-vite`, React renderer, Zustand state, `node-pty`, `@xterm/headless`, `@anthropic-ai/claude-agent-sdk`).
- Engineering discipline in the repo is strong: extensive `oxlint` rules, `ast-grep` structural gates, Vitest unit suites, and dedicated benchmarks for renderer fanout, terminal stream pacing, and daemon coldstart.

## 2. Functional differentiation (Orca vs. herdr)

Both `orca` and `herdr` address the same root bottleneck of modern agentic coding: **running multiple long-horizon CLI agents concurrently without losing track of context or approvals**. However, they take opposite architectural paths:

1. **Top-down IDE replacement (`orca`) vs. bottom-up multiplexer (`herdr`)**:
   - `orca` replaces your terminal emulator, git client, diff viewer, and local preview browser with a unified Electron workspace. When you start a task in Orca, it creates a dedicated Git worktree, spawns a coordinator or worker agent, renders diffs inline for line-by-line review notes, and lets you click DOM elements in an embedded browser to send selectors back to the agent.
   - `herdr` stays strictly inside the terminal layer: a single Rust binary that multiplexes PTY panes, tracks agent status (`working`/`blocked`/`idle`), and runs inside whatever terminal or editor workbench you already use.
2. **Chat UI abstraction vs. raw PTY fidelity**:
   - `orca` offers a "Chat or Terminal" toggle that projects agent conversations into a graphical chat view and bridges sessions via `@anthropic-ai/claude-agent-sdk` and `@orca/process-host`.
   - `herdr` never parses or re-renders conversation turns into a custom chat UI; the pane *is* the native CLI process.

## 3. Minimal hands-on test

- Inspected the `v1.4.214` source tree, workspace architecture (`package.json`, `electron.vite.config.ts`, `orca.yaml`), and benchmark/diagnostic harnesses.
- Noticeable architectural complexity in the source tree: maintaining parity between Electron main/renderer processes, headless xterm state serialization, WSL/SSH remote relays, and worktree file watchers requires a large surface of custom backpressure and freeze-mitigation machinery (evidenced by dedicated repro suites such as `remote-session-bulk-open-freeze-repro` and `terminal-multiplex-ack-pacing`).

## 4. Cost surface

- **Heavy runtime & Electron lock-in**: requires running an Electron desktop client plus background Node/pty hosts; does not compose with existing lightweight terminal emulators (e.g., Ghostty, Alacritty, WezTerm) or standard `mosh` workflows.
- **Telemetry**: bundles `posthog-node` (documented opt-out in telemetry settings, but enabled by default).
- **High feature overlap**: for developers who already manage worktrees, diffs, and browser automation through unix-style CLI tools and skills, 80% of Orca's bundled UI is redundant weight.

## 5. Recommendation

**Do not adopt (`rejected`) in favor of `herdr`.** `orca` is a well-engineered product for users who want a single GUI application to manage worktrees, chat threads, diffs, and browser previews out of the box. For a composable, terminal-first stack over SSH, `herdr` provides the essential agent multiplexing and state-tracking capabilities with a fraction of the footprint.
