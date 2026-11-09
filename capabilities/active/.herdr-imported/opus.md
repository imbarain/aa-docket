# herdr deep review — opus, 2026-11-09

> Executed along five dimensions (upstream health / functional differentiation / minimal hands-on test / cost surface / recommendation), including a head-to-head comparison with `stablyai/orca`.

## 0. Positioning

`herdr` (`herdrdev/herdr`) is an agent-aware terminal multiplexer written in Rust (`Apache-2.0`). Instead of building a new GUI IDE around coding agents, it replaces traditional multiplexers (`tmux`, `zellij`, `wezterm-mux-server`) with a background server that understands coding agents are running inside its panes. It tracks whether each agent is `working`, `blocked` (awaiting user approval/input), or `idle`, persists sessions across disconnects, resumes agent conversations after server restarts, and exposes a Unix socket API so agents and plugins can drive panes programmatically.

## 1. Upstream health

- Repo created 2026-03-27; ~49.5k stars / ~4.0k forks, Apache-2.0 license, actively maintained with regular releases (`0.9.x` series).
- Pure Rust workspace (`Cargo.toml`, `crates/`), distributed via Homebrew, `mise`, static binaries, and Nix flakes.
- No mandatory cloud account or relay: local Unix socket and standard SSH transport (`herdr --remote <host>`).

## 2. Functional differentiation (herdr vs. tmux / WezTerm mux / Orca)

| Dimension | `tmux` / `zellij` | `herdr` (`herdrdev/herdr`) | `orca` (`stablyai/orca`) |
|---|---|---|---|
| **Core layer** | Generic PTY multiplexer | Agent-aware PTY multiplexer (TUI) | Standalone Electron IDE + Chat/Terminal app |
| **Runtime footprint** | Tiny (C / Rust) | Small (single Rust binary, no Electron) | Heavy (Electron + Node daemon + headless xterm) |
| **Agent UI model** | Raw terminal only | Raw terminal + sidebar agent state (`working`/`blocked`/`idle`) | Dual mode: custom Chat UI wrapper (`claude-agent-sdk`) or terminal |
| **Host independence** | Runs in any terminal over SSH/mosh | Runs in any standard terminal emulator | Requires Orca desktop app (or Orca mobile app paired to Orca server) |
| **Restart recovery** | Layout plugins only (`tmux-resurrect`); processes die | Restores layout + automatically resumes agent sessions via hooks | Restores worktree tabs and chat transcripts inside Orca |
| **Scope beyond mux** | None | Socket API + lightweight plugins | Built-in git worktree manager, diff annotator, browser, Linear/GitHub board |

Key architectural advantages of `herdr`:
1. **Zero wrapper lag**: every new flag, slash command, or interactive TUI prompt shipped by Claude Code or Codex works immediately inside `herdr` because the agent runs in a real terminal pane.
2. **Attention routing**: when running multiple agents concurrently, the bottleneck is knowing which agent is blocked on a permission prompt vs. still working. `herdr` surfaces this state directly in the sidebar and via its socket API.
3. **Display-layer freedom**: because `herdr` is a TUI client talking to a background server, the same running session can be attached from any desktop, web, or mobile SSH terminal client.

## 3. Minimal hands-on test

- Verified `herdr --help`, `herdr server` lifecycle, and `herdr integration status` in an isolated environment, alongside source and documentation review (`herdrdev/herdr`).
- Inspected upstream agent integration mechanism (`herdr integration install <agent>`): lightweight hook registration (`SessionStart` / state reporting) allows closing the client while panes continue running in the background and resuming recorded session IDs after a server restart.
- Reviewed the documented Unix socket API and plugin manifest format (`herdr-plugin.toml`): clean JSON request/event protocol for inspecting and controlling panes programmatically.

## 4. Cost surface

- **Integration hook registration**: `herdr integration install <agent>` writes hook entries into agent configuration files (such as `~/.claude/settings.json` or `~/.codex/hooks.json`). Users who version-control those files should be aware that the installer modifies them in place.
- **Upgrade semantics**: upgrading the binary on disk does not hot-swap a running `herdr server` process (unless using the experimental `--handoff` installer flow); switching server versions normally requires restarting the server and updating integrations when hook versions advance.

## 5. Recommendation

**Adopt (`imported`).** For terminal-centric and remote-host workflows, `herdr` delivers the exact primitives needed for multi-agent concurrency—state visibility, detach/reattach persistence, conversation resume, and a clean socket API—without the bloat or lock-in of an Electron IDE.
