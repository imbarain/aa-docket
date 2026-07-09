# aa-docket

**English**

**Agent Ability Docket** — a lifecycle docket for evaluating agent capabilities (skills / MCP servers / CLIs) before you adopt them, and a validator that keeps every card honest.

A *docket* is a case-file: each candidate capability is one card that moves through evaluation states to a durable, reviewable decision. Archived is not a permanent seal — a rejected card can be re-opened when the evidence changes.

## Why this exists

The agent ecosystem moves fast — CLIs, skills, MCP servers, orchestrators, frameworks appear weekly. Some age well, some are flash-in-the-pan. From the outside it's hard to tell which are genuinely useful and which are marketing. This docket is where you record your own evaluations through a pipeline matched to your real needs — so the verdict is yours, not the hype.

## The state machine

```
        active/                          archived/
  ┌──────────────────┐            ┌──────────────────────┐
  │ pending          │──decide──▶ │ rejected   (no)      │
  │  (evaluating)    │            │ eol        (removed)  │
  │ imported         │──retire──▶ │                       │
  │  (in use)        │            └──────────┬───────────┘
  └──────────────────┘                       │
             ▲                                │
             └──────── re-open ───────────────┘
                (evidence changed / stronger
                 assessor or method available)
```

| state | meaning | lives in |
|---|---|---|
| `pending` | under evaluation, no decision yet | `active/` |
| `imported` | adopted into the stack | `active/` |
| `rejected` | evaluated, decision is no | `archived/` |
| `eol` | was in the stack, now removed (end-of-life) | `archived/` |

Archived cards are **decided testimony, not a permanent seal.** Re-open when a card's re-assessment condition is met — the original verdict was a single un-cross-checked model, its basis is now doubtful, or a stronger assessor / experimental method became available.

## Layout

```
active/
  <name>-pending.md          # + optional hidden companion  .<name>-pending/
  <name>-imported.md
archived/
  <name>-rejected.md
  <name>-eol.md
TEMPLATE.md                  # card format, naming, and body rules (the full spec)
validate.py                  # mechanical validator
tests/test_validate.sh
```

A card is one markdown file with YAML frontmatter. Its filename encodes `<name>-<state>`, which must agree with the frontmatter. Detailed per-model notes, screenshots, and clusters go in a hidden companion folder `.<name>-<state>/` next to the card. See **[TEMPLATE.md](./TEMPLATE.md)** for the full contract.

## Usage

```sh
python3 validate.py .          # validate active/ + archived/
python3 validate.py active/    # validate one subdir
bash tests/test_validate.sh    # run the test suite
```

> On an empty repo (only `.gitkeep` in `active/` and `archived/`), the validator exits 1 with `no files to check` — add a card first.

The validator checks, mechanically: filename ↔ frontmatter agreement, the state enum, `last_assessed` presence by state, body rules per state (pending = dated links only; decided = prose reasons), companion-folder hygiene (hidden, matched, no orphans), and that every relative link target exists. Card **prose is never validated and may be in any language** — only the state token is constrained to ASCII so filenames and tooling stay grep-friendly.

## Requirements

- Python 3 (standard library only)
- [`yq`](https://github.com/mikefarah/yq) **v4.x** (Mike Farah's Go implementation) on `PATH` — used to parse frontmatter (`yq -o=json`). Note: `python3-yq` (the PyYAML wrapper) is **not** compatible.

## License

MIT — see [LICENSE](./LICENSE).

---

# aa-docket(中文）

**中文**

**Agent Ability Docket —— agent 能力评估台账。** 在引入一个 skill / MCP / CLI 之前,用一张卡片跟踪它从「评估中」到「已决」的全过程;配一个 validator 保证每张卡片格式诚实。

*docket*(案卷)的取意:每个候选能力是一桩「案子」,在状态间流转直到一个**可复查的裁决**。归档不是永久封存 —— 证据变化时,被否决的卡片可以重新开评。

## 为什么需要这个

agent 生态演进极快 —— CLI、skill、MCP、orchestrator、framework 不断冒头。有的历久弥新,有的昙花一现;哪些真有用、哪些只是营销,外部观察很难分辨。本 docket 用你自己的评估管线(匹配你的真实需求)记录每个候选的结论,把决定权留在自己手里,不跟着热度走。

## 状态机

```
        active/                          archived/
  ┌──────────────────┐            ┌──────────────────────┐
  │ pending          │──decide──▶ │ rejected   (no)      │
  │  (evaluating)    │            │ eol        (removed)  │
  │ imported         │──retire──▶ │                       │
  │  (in use)        │            └──────────┬───────────┘
  └──────────────────┘                       │
             ▲                                │
             └──────── re-open ───────────────┘
                (evidence changed / stronger
                 assessor or method available)
```

| 状态 | 含义 | 存放 |
|---|---|---|
| `pending` | 评估中,未决 | `active/` |
| `imported` | 已引入在用 | `active/` |
| `rejected` | 已评估,否决 | `archived/` |
| `eol` | 曾在用,已退役 | `archived/` |

`archived/` 是**已决证词库,不是永久封存**。满足重评条件即可回迁重开:原裁决只有单模型未交叉、依据已存疑、或出现了更强的评估者 / 实验方法。

## 目录布局

```
active/
  <name>-pending.md          # + 可选隐藏 companion .<name>-pending/
  <name>-imported.md
archived/
  <name>-rejected.md
  <name>-eol.md
TEMPLATE.md                  # 卡片格式 / 命名 / 正文规则(完整契约)
validate.py                  # 机械校验
tests/test_validate.sh
```

一张卡片就是一个带 YAML frontmatter 的 markdown 文件,文件名 `<name>-<state>`,必须与 frontmatter 一致。详细 per-model 笔记、截图、聚类放在 `.name-state/` 隐藏目录。完整契约见 **[TEMPLATE.md](./TEMPLATE.md)**。

## 用法

```sh
python3 validate.py .          # 校验 active/ + archived/
bash tests/test_validate.sh    # 跑测试
```

> 空仓库(`active/` 和 `archived/` 只有 `.gitkeep`)下,validator 会以 `no files to check` 退出 1 —— 先放一张卡片再校验。

validator 机械校验:文件名↔frontmatter 一致、状态枚举、`last_assessed` 按状态、正文规则(pending 只放带日期的链接;已决须有 `## ` 理由段)、companion 目录卫生、以及所有相对链接目标存在。**正文散文不校验、任何语言都行**,只有状态 token 限 ASCII 以保证 grep 友好。卡片格式完整契约见 **[TEMPLATE.md](./TEMPLATE.md)**。

## 依赖

- Python 3(仅标准库)
- [`yq`](https://github.com/mikefarah/yq) **v4.x**(Mike Farah 的 Go 实现,解析 frontmatter)。注意:`python3-yq`(PyYAML 包装版)**不**兼容。

## 协议

MIT —— 见 [LICENSE](./LICENSE)。
