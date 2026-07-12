# jina-ai（reader + MCP + cli）

## 公司层

- jina-ai 于 2025-10-15 被 Elastic 收购，创始人 Han Xiao 转任 Elastic VP of AI
- 收购公告承诺继续做 embeddings / reranker / Reader / 小模型；OSS 框架（jina-serve）和 JCloud 提都没提
- 9 个月下来的实证：模型 SKU 持续发版（v5-text 2026-02、v5-omni 2026-05、reranker-m0 2025-04），OSS 框架 0 commit
- 当前定位：「Your Search Foundation, Supercharged」——押注 Elastic 搜索生态

## 仓库规模

265 个公开仓库：161 active non-fork（Python 110 / TS 11 / 其他），60 archived，45 forks。

## 活着的 surface（2026 在维护）

**商业模型**（OpenAI 兼容 API at `api.jina.ai/v1/embeddings`）：

| SKU | 上线 | 用途 |
|---|---|---|
| jina-embeddings-v5-omni | 2026-05 | 旗舰多模态（文本+图像+音频+视频统一空间，1.6B / 0.9B） |
| jina-embeddings-v5-text | 2026-02 | 文本旗舰（677M / 239M，task-LoRA、Matryoshka、32K ctx、GGUF/MLX） |
| jina-embeddings-v4 | 旧 | 3.8B 通用多模态，文档检索 |
| jina-clip-v2 | 2024-11 | 轻量 CLIP（865M，89 语言） |
| jina-reranker-m0 | 2025-04 | 首个多模态 reranker（基于 Qwen2-VL-2B） |
| ReaderLM-v2 | 2024-07 | HTML→markdown 小模型 |

**应用层服务**：

| Repo | ★ | 用途 |
|---|---|---|
| `reader` | 11.4k | `r.jina.ai` URL→markdown；`s.jina.ai` 搜索；20+ `X-*` 控制头；OSS 镜像 `ghcr.io/jina-ai/reader:oss` |
| `MCP` | 737 | 21 个 MCP tool；`mcp.jina.ai/v1` streamable-HTTP |
| `cli` | 160 | Unix CLI：`jina read / search / embed / rerank / classify / dedup / screenshot / bibtex / expand / pdf / datetime / primer / grep` |
| `node-DeepResearch` | 5.1k | deepsearch.jina.ai 的引擎 |
| `deepsearch-ui` | 130 | node-DeepResearch 的官方 web UI |

## 与常见备选的对照

同生态里 jina 最常被拿来和 firecrawl、tavily 比——三者在这三类能力上重叠：

| 能力 | jina | firecrawl | tavily |
|---|---|---|---|
| URL → markdown（单页） | `read_url` / `jina read` | `firecrawl scrape` | `tavily extract` |
| 批量 URL → markdown | `parallel_read_url`（≤5）/ 数组 / stdin | `firecrawl crawl`（沿链接） | `tavily extract`（≤20，不沿链接） |
| Web 搜索 | `search_web` / `jina search` | ❌ | `tavily search` |

**三者皆有的就这三类。** 其余都是 jina 独有或单家独有。

**jina 独有（同类工具里没有对照）**：`search_arxiv` / `search_ssrn` / `search_bibtex` / `search_images` / `expand_query` / `extract_pdf` / `classify_text` / `sort_by_relevance` / `deduplicate_strings` / `deduplicate_images` / `embed` / `capture_screenshot_url` / `guess_datetime_url` / `primer` / `jina grep`（语义 grep，Apple Silicon only）。

**jina 没补的（同类工具有）**：
- 整站 URL 发现（firecrawl map 那类）——jina 完全不补
- crawl 的 `--include-paths` / `--exclude-paths` / `--max-depth` 细粒度
- 多源综合 + 引用研究报告（tavily research 那类；jina 的 node-DeepResearch 是同思路但未打包成即用件）

## 死掉的 / 维护模式（值得警示）

- **`jina-ai/serve`（21.9k★，即 jina-serve）**：最后 commit 2025-03-24，Elastic 收购以来 0 commit。issue #6238 由前核心开发公开贴「Looking for a maintained alternative?」。**软弃坑**
- **`clip-as-service`（12.8k★）**：最后 commit 2023-12，概念上被 jina-clip-v2 / v5-omni API 取代
- **`discoart` / `dalle-flow` / `jina-video-chat`**：Stable Diffusion 时代化石
- **Auto-GPT 狂热 2023 留下**：dev-gpt / thinkgpt / agentchain / auto-gpt-web / rungpt / textbook 全部沉默 3 年
- **`jinaai-py` / `jinaai-js` SDK**：覆盖旧五件套（PromptPerfect / SceneXplain / Rationale / JinaChat / BestBanner），**不是当前产品线**，0 release 不要踩

## 待审理由

1. 与常见 scrape / search 工具（firecrawl、tavily 那类）在重合的 3 类能力上没有质变优势
2. 学术 / embed / rerank / classify / dedup 等独有面是利基能力，使用频率不够支撑单装一个 skill
3. jina-ai/serve 软弃坑、jinaai-py/js SDK 是旧五件套——star 数会误导
4. 收购方（Elastic）对 API / 产品线的承诺兑现需持续观察

## 重新评估触发条件

- [ ] RAG 后处理需求具体化（embed + rerank + dedup 真要落地）
- [ ] 常用搜索/提取工具触及配额瓶颈，需要备胎
- [ ] jina MCP 出现能补「整站 URL 发现」空白的新工具
- [ ] jina 出现 deprecation 公告 → 转退役

## 评估记录

- 2026-06-24：首次评估（详细对比见本文件「活着的 surface」与「与常见备选的对照」）
