# jina-ai (reader + MCP + cli)

## Company layer

- jina-ai was acquired by Elastic on 2025-10-15; founder Han Xiao became Elastic VP of AI
- The acquisition announcement promised to keep doing embeddings / reranker / Reader / small models; the OSS framework (jina-serve) and JCloud went unmentioned
- Nine months of evidence: model SKUs keep shipping (v5-text 2026-02, v5-omni 2026-05, reranker-m0 2025-04), the OSS framework at 0 commits
- Current positioning: "Your Search Foundation, Supercharged" — betting on the Elastic search ecosystem

## Repo scale

265 public repos: 161 active non-fork (Python 110 / TS 11 / other), 60 archived, 45 forks.

## Living surface (maintained in 2026)

**Commercial models** (OpenAI-compatible API at `api.jina.ai/v1/embeddings`):

| SKU | Launched | Use |
|---|---|---|
| jina-embeddings-v5-omni | 2026-05 | Flagship multimodal (text+image+audio+video in a unified space, 1.6B / 0.9B) |
| jina-embeddings-v5-text | 2026-02 | Text flagship (677M / 239M, task-LoRA, Matryoshka, 32K ctx, GGUF/MLX) |
| jina-embeddings-v4 | old | 3.8B general-purpose multimodal, document retrieval |
| jina-clip-v2 | 2024-11 | Lightweight CLIP (865M, 89 languages) |
| jina-reranker-m0 | 2025-04 | First multimodal reranker (based on Qwen2-VL-2B) |
| ReaderLM-v2 | 2024-07 | HTML→markdown small model |

**Application-layer services**:

| Repo | ★ | Use |
|---|---|---|
| `reader` | 11.4k | `r.jina.ai` URL→markdown; `s.jina.ai` search; 20+ `X-*` control headers; OSS mirror `ghcr.io/jina-ai/reader:oss` |
| `MCP` | 737 | 21 MCP tools; `mcp.jina.ai/v1` streamable-HTTP |
| `cli` | 160 | Unix CLI: `jina read / search / embed / rerank / classify / dedup / screenshot / bibtex / expand / pdf / datetime / primer / grep` |
| `node-DeepResearch` | 5.1k | The engine behind deepsearch.jina.ai |
| `deepsearch-ui` | 130 | Official web UI for node-DeepResearch |

## Comparison against common alternatives

Within the same ecosystem, jina is most often compared with firecrawl and tavily — the three overlap on these three capability classes:

| Capability | jina | firecrawl | tavily |
|---|---|---|---|
| URL → markdown (single page) | `read_url` / `jina read` | `firecrawl scrape` | `tavily extract` |
| Batch URL → markdown | `parallel_read_url` (≤5) / array / stdin | `firecrawl crawl` (follows links) | `tavily extract` (≤20, no link-following) |
| Web search | `search_web` / `jina search` | ❌ | `tavily search` |

**These three classes are all the three share.** Everything else is jina-only or one-vendor-only.

**jina-only (no counterpart among peer tools)**: `search_arxiv` / `search_ssrn` / `search_bibtex` / `search_images` / `expand_query` / `extract_pdf` / `classify_text` / `sort_by_relevance` / `deduplicate_strings` / `deduplicate_images` / `embed` / `capture_screenshot_url` / `guess_datetime_url` / `primer` / `jina grep` (semantic grep, Apple Silicon only).

**What jina does not fill (peer tools have it)**:
- Whole-site URL discovery (the firecrawl-map class) — jina does not fill this at all
- Fine-grained crawl controls: `--include-paths` / `--exclude-paths` / `--max-depth`
- Multi-source synthesis + cited research reports (the tavily-research class; jina's node-DeepResearch is the same idea but not packaged as a ready-to-use component)

## Dead / maintenance-mode (worth flagging)

- **`jina-ai/serve` (21.9k★, i.e. jina-serve)**: last commit 2025-03-24, 0 commits since the Elastic acquisition. Issue #6238 has a former core developer publicly posting "Looking for a maintained alternative?" **Soft-abandoned.**
- **`clip-as-service` (12.8k★)**: last commit 2023-12, conceptually superseded by the jina-clip-v2 / v5-omni API
- **`discoart` / `dalle-flow` / `jina-video-chat`**: Stable Diffusion-era fossils
- **Leftovers from the 2023 Auto-GPT mania**: dev-gpt / thinkgpt / agentchain / auto-gpt-web / rungpt / textbook — all silent for 3 years
- **`jinaai-py` / `jinaai-js` SDKs**: cover the old five-piece set (PromptPerfect / SceneXplain / Rationale / JinaChat / BestBanner), **not the current product line**, 0 releases — don't step on it

## Reasons pending

1. No qualitative advantage over common scrape / search tools (the firecrawl, tavily class) on the 3 overlapping capability classes
2. The unique surfaces — academic / embed / rerank / classify / dedup, etc. — are niche capabilities used too infrequently to justify installing a dedicated skill
3. jina-ai/serve is soft-abandoned, jinaai-py/js SDKs are the old five-piece set — star counts mislead
4. The acquirer's (Elastic's) delivery on API / product-line commitments needs ongoing observation

## Re-assessment triggers

- [ ] RAG post-processing needs become concrete (embed + rerank + dedup actually land)
- [ ] Commonly used search/extraction tools hit a quota bottleneck and a backup is needed
- [ ] A new jina MCP tool appears that fills the "whole-site URL discovery" gap
- [ ] jina issues a deprecation notice → move to end-of-life

## Assessment log

- 2026-06-24: first assessment (detailed comparison in this file's "Living surface" and "Comparison against common alternatives")
