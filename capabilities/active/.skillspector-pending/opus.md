# NVIDIA/SkillSpector

## 详细分析

- 仓库: https://github.com/NVIDIA/SkillSpector
- 定位: AI agent skill 引入前安全扫描器 — 64 patterns / 16 categories，LangGraph + 双阶段（静态 + LLM）架构
- 末次评估: 2026-06-22  |  当时状态: Apache-2.0, 9.1k stars, Python 3.12 + YARA
- 生态位: 与「引入前静态规则闸」一类工具同面

## 顾虑

1. **与一类既有 intro-gate 工具高度重叠（≥70%）**：只要已经有一套 skill 引入前的静态规则闸，SkillSpector 的静态阶段就是重复能力
2. **裁决哲学取舍**：LLM Stage 2 对 finding 有实质过滤权（决定哪些告警放行）。若威胁模型里「读敌意内容的 LLM 自身可被注入」是必须防的，那把否决权交给 LLM 阶段就不可接受——这是设计取向问题，需按各自威胁模型判断
3. **不覆盖包生态恶意检测**：typosquat / 凭证窃取 / 维护者突变这类供应链面 SkillSpector 没有对等物；若拿它替换一套已含供应链检测的闸，是能力面降级
4. **集成成本**：Python 3.12 + LangGraph + Docker + 多 LLM provider，重于一套纯静态规则闸

## 值得借鉴（无需引入即可白拿）

- 它的 64-pattern / 16-category 清单是很好的「规则面盘点」参考语料：跨行污点流、MCP metadata unicode 投毒、Python AST 检测等面，可当自有规则集扩面时的思路来源

## 为什么是待审而非拒绝

单件重叠不等于永久无价值。保留复评路径，等以下任一条件满足再正式重评：

- 想扩自有规则集时，回看其 64-pattern 清单有无新面思路
- 出现可利用「跨行污点流 / MCP metadata / unicode 投毒」的真实恶意 skill 样本，需要成套检测能力

## 评估记录

- 2026-06-22：首次评估
