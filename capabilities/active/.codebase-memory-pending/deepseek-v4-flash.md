# codebase-memory-mcp (casualjim) — high-performance code-intelligence MCP

Assessment date: 2026-06-28
GitHub: https://github.com/casualjim/codebase-memory-mcp
Language: C (statically compiled, single-file binary)
License: MIT

## Project positioning

A high-performance code-intelligence MCP server. Indexes a codebase into a persistent knowledge graph so an AI agent can query code structure and relationships without grepping file by file.

## Technical architecture

- **Parsing engine**: Tree-sitter AST, **158 languages** (all compiled into the binary)
- **Type resolution**: Hybrid LSP (a built-in lightweight C implementation, no external LSP server) — 10 languages have type-aware resolution: Python/TS/JS/JSX/TSX/PHP/C#/Go/C/C++/Java/Kotlin/Rust
- **Storage**: SQLite graph store + built-in openCypher parser/planner/executor
- **Sync**: automatic incremental sync via git polling
- **Embedding model**: Nomic local embedding model (compiled into the binary, no API key or Ollama needed)
- **Deployment form**: single static binary (no Docker, no Python/Node/JVM runtime)

## Architecture layering

| Layer | Responsibility |
|----|------|
| `src/main.c` | Entry — MCP stdio server + CLI + install/update |
| `src/mcp/` | JSON-RPC 2.0 MCP implementation, 14 tools |
| `src/pipeline/` | Multi-pass indexing (structure→definitions→calls→HTTP→config→tests) |
| `src/store/` | SQLite graph store + traversal/search/Louvain clustering |
| `src/cypher/` | In-house openCypher parser/planner/executor |
| `src/discover/` | File discovery (`.gitignore`/`.cbmignore`) |
| `src/watcher/` | git-polling background auto-sync |
| `internal/cbm/` | vendored 158 Tree-sitter grammars |

## MCP tool inventory (14 tools)

Indexing: `index_repository` (incl. auto-sync), `list_projects`, `delete_project`, `index_status`
Query: `search_graph` (label/name/file filters), `trace_call_path` (BFS traversal of callers/callees, depth 1-5)
Analysis: `detect_changes` (git diff → affected symbols + blast radius + risk rating)
Search: `search_code` (grep-style search), `get_code_snippet` (read source by qualified name)
Architecture: `get_architecture` (languages/packages/routes/hotspots/clusters/ADR), `get_graph_schema`
ADR management: `manage_adr` (architecture-decision-record CRUD)
Cypher query: `query_graph` (read-only openCypher: MATCH/WHERE/RETURN/aggregation/EXISTS subqueries)
Other: `ingest_traces` (import runtime traces to validate `HTTP_CALLS` edges)

## Performance data

| Metric | Value |
|------|------|
| Cypher query | < 1ms |
| Name search (regex) | < 10ms |
| Call-chain trace (depth=5) | < 10ms |
| Dead-code detection (full-graph scan) | ~150ms |
| Django full index | ~6s (49K nodes) |
| Linux kernel (28M LOC, 75K files) | ~3 min (4.81M nodes, 7.72M edges) |
| Binary size | single file, ~tens of MB (incl. all grammars + embedding model) |
| Memory | RAM-first + LZ4 compression, released back to the OS after indexing completes |

## Unique capabilities (increment beyond a peer like CGC)

1. **Detect changes with blast radius** — fits a "bounded modification" commit style well: check the affected scope before making a change
2. **ADR management** — persists architecture decisions, matches cross-session knowledge transfer (a complex skill's business rules and design decisions are not lost when the session changes)
3. **Claude Code-specific hook** — PreToolUse intercepts Grep/Glob and, on a hit against an indexed symbol, enriches context with `search_graph` results, but does not block Read operations ("gating Read breaks read-before-edit invariant")

## Context-burden estimate

Tool definitions ~4-6K tokens/turn (14 MCP tool schemas, but parameters are leaner than CGC's).
The hook's `additionalContext` injection is incremental and triggered on demand.

## Assessment dimensions

### Pros

1. **Zero-dependency single-file binary** → friendly to "user-level install, don't touch the system environment" (just drop it in `~/.local/bin/`)
2. **158 languages** → covers common stacks like Python/JS/TS/Shell
3. **Hybrid LSP** → 10 mainstream languages get real type resolution, not just text matching
4. **Sub-millisecond queries** → imperceptible in daily use
5. **git-polling auto-sync** → no manual reindex needed
6. **ADR management** → solves cross-session knowledge loss
7. **Elegant Claude Code hook design** → does not block reads, injects only when meaningful
8. **Team sharing** → the graph snapshot file (`.codebase-memory/graph.db.zst`) can be shared, avoiding duplicate indexing

### Concerns

1. **First-time indexing cost**: for a medium-sized repo of ~14K files, the first full index may take 1-2 minutes
2. **Fixed context overhead**: even if you use no graph tool at all, every conversation carries an extra 4-6K tokens
3. **Windows SmartScreen** warning (unsigned binary) — Linux has no such issue
4. **Relatively new**: smaller community than CGC (fewer stars), but the code quality looks higher (C, single binary, transparent measured benchmarks)
5. **Potential occasional hook interference**: Grep being injected with extra data may change the agent's search behavior; not 100% transparent

### Current conclusion

**Recommend trying it first.** Lighter than CGC:
- No environment-maintenance cost (single binary vs. a Python dependency chain)
- Performance is good enough (< 1ms queries)
- The ADR feature solves the real pain of cross-session knowledge loss
- The hook design does not block the workflow

Suggest a one-week trial on a representative repo first, to assess actual context burden vs. benefit.

## Related links

- GitHub: https://github.com/casualjim/codebase-memory-mcp
- Install: download the static binary for your platform from Releases, put it in `~/.local/bin/`
- MCP config: add to the `mcpServers` block of the MCP client
