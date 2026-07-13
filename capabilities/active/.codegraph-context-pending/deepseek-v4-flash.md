# CodeGraphContext (CGC) — code knowledge-graph MCP

Assessment date: 2026-06-28
GitHub: https://github.com/CodeGraphContext/CodeGraphContext
Stars: ~3.8k
Language: Python
License: MIT

## Project positioning

Indexes local code into a graph database and exposes it to AI assistants via MCP. Also provides a CLI for standalone use.

## Technical architecture

- **Parsing engine**: Tree-sitter AST parsing, supports 23 languages
- **Graph database**: FalkorDB Lite (default on Unix) / KuzuDB (cross-platform) / LadybugDB / Neo4j / Nornic
- **MCP protocol**: JSON-RPC 2.0 over stdio
- **Optional enhancement**: SCIP indexing (C/C++/C# require `compile_commands.json`)

## MCP tool inventory (14 tools + 4 resources + 6 prompts)

Indexing: `index_project`, `list_projects`, `delete_project`
Query: `search_code`, `trace_calls`, `find_callers`, `find_callees`, `impact_analysis`
Analysis: `dead_code_detection`, `complexity_analysis`, `get_architecture`
Visualization: interactive HTML graph (force-directed layout)

## Differences from LSP

| Capability | LSP | CGC |
|------|-----|-----|
| Go to definition | ✅ | ❌ redundant |
| Find references | ✅ | ❌ redundant |
| Call chain | ❌ | ✅ BFS multi-level call chain |
| Impact analysis | ❌ | ✅ scope affected by changing X |
| Dead code | ❌ | ✅ |
| Architecture overview | ❌ | ✅ package/module/hotspot map |

## Context-burden estimate

Tool definitions ~5-8K tokens/turn (14 MCP tool schemas).
Result returns depend on query complexity; a call chain can add an extra 1-3K tokens.

## Assessment dimensions

### Pros
1. The most mature open-source implementation (3.8k ★, active community)
2. Dual CLI + MCP mode
3. GraphRAG (Louvain community detection + global/local search)
4. Zero-config start (SQLite embedded)
5. Indexing speed: 100K lines < 30s, incremental < 2s

### Concerns
1. **Python-ecosystem dependency**: tree-sitter + graph-DB SDK → need to maintain a Python environment
2. **Known bugs**: the repo contains `CGC_E2E_BUG_REPORT.md` and `CGC_GRAPH_INCONSISTENCIES.md`, indicating acknowledged problems
3. **Python 3.13 compatibility**: Tree-sitter is marked "not installed" on 3.13
4. **C/C++ SCIP indexing**: requires a complete build system + `compile_commands.json`, high barrier, silently degrades on failure
5. **23-language coverage** but many languages are shallow text parsing (not Hybrid LSP type inference)
6. **Multiple DB backends** add configuration complexity; embedded DBs may be insufficient at large scale (Neo4j recommended for "Enterprise")
7. Tool schemas are on the heavy side → context overhead at the upper bound (~8K tokens)

### Current conclusion

Functionally it does fill LSP's gaps, but for a workflow dominated by bounded modifications (one logical change per commit):
- impact analysis is used infrequently
- a medium-scale codebase (~hundreds of thousands of lines) hasn't yet reached the point where a graph is indispensable
- the Python dependency chain and known bugs add maintenance burden
- decision: **watch and wait, no rush to adopt**. Re-assess if a scenario with frequent cross-module refactoring comes up later.

## Related links

- GitHub: https://github.com/CodeGraphContext/CodeGraphContext
- PyPI: https://pypi.org/project/codegraphcontext/
