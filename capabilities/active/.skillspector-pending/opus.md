# NVIDIA/SkillSpector

## Detailed analysis

- Repo: https://github.com/NVIDIA/SkillSpector
- Positioning: pre-adoption security scanner for AI agent skills — 64 patterns / 16 categories, LangGraph + two-stage (static + LLM) architecture
- Last assessed: 2026-06-22  |  State at the time: Apache-2.0, 9.1k stars, Python 3.12 + YARA
- Niche: same surface as the "pre-adoption static-rule gate" class of tools

## Concerns

1. **High overlap (≥70%) with an existing class of intro-gate tools**: as long as you already have a static-rule gate for pre-adoption of skills, SkillSpector's static stage is a duplicate capability
2. **Adjudication-philosophy tradeoff**: LLM Stage 2 has substantive filtering power over findings (deciding which warnings pass). If your threat model must defend against "the LLM that reads hostile content can itself be injected," then handing veto power to the LLM stage is unacceptable — this is a design-orientation question to be judged against each threat model
3. **Does not cover package-ecosystem malware detection**: SkillSpector has no equivalent for supply-chain surfaces like typosquatting / credential theft / maintainer-takeover; using it to replace a gate that already includes supply-chain detection is a capability-surface downgrade
4. **Integration cost**: Python 3.12 + LangGraph + Docker + multiple LLM providers, heavier than a pure static-rule gate

## Worth borrowing (take for free, no adoption needed)

- Its 64-pattern / 16-category list is a good "rule-surface inventory" reference corpus: surfaces like cross-line taint flow, MCP metadata unicode poisoning, Python AST detection, etc., can be a source of ideas when expanding your own rule set

## Why pending rather than rejected

Overlap on a single item doesn't equal permanent worthlessness. Keep a re-review path open; do a formal re-assessment when any of the following is met:

- When you want to expand your own rule set, revisit its 64-pattern list for any new-surface ideas
- A real malicious-skill sample appears that exploits "cross-line taint flow / MCP metadata / unicode poisoning," requiring a full detection suite

## Assessment log

- 2026-06-22: first assessment
