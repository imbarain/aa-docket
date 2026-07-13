# browser-harness 深评 — claude-fable-5, 2026-07-05

> 按五维（上游健康 / 功能差异化 / 最小实测 / 成本面 / 建议）执行；源码证据来自全历史 clone（431 commits）审读。

## 0. 定位

browser-use 公司的新形态产品：不是「自带 LLM 循环的 agent」（那是 browser-use 早前的主产品线），而是反向的「LLM 直写 Python 代码说裸 CDP」的 harness——`run.py:180` 对 stdin 代码裸 `exec()`，daemon 长连真实 Chrome，helper 原语 508 行，另暴露 `cdp(method, **params)` 任意 CDP 调用。明确定位为装进 Claude Code / Codex 的 skill。

## 1. 上游健康度

- 仓库 2026-04-17 创建，评估时 2.5 个月龄；15.7k stars / 1.4k forks / 162 open issues / 60+ 贡献者。browser-use 母公司光环（主仓 102k stars、有 Cloud 商业线）——**母公司光环下 star 宜打 3 折看待**，且母公司资源 ≠ 本仓承诺。
- 版本 0.1.4，classifier 明标 `Development Status :: 3 - Alpha`。
- 节奏：5 月初 6 天 95 commits 爆发搭建 → 中旬起个位数、数周空档 → 6 月末小爆发；最后 push 2026-07-01。**爆发后冷却型**，非日更活跃仓。
- 反常的好信号：测试 1,933 行 / 源码 2,978 行（≈65%），覆盖 daemon 生命周期、IPC token、PID 复用竞态——生产级心态。

## 2. 功能差异化（对照同类浏览器驱动工具）

主场景「驱动真实登录态 Chrome 做 ad-hoc 浏览器操作」与成熟的开源浏览器驱动工具（如 opencli 的 browser 模式）**重叠 ≥70%**：bind 真实 tab、eval JS、network 捕获、表单全家桶、extract，这类工具全有，且多已吸收 AX snapshot / refs 的可达性模式。

真实增量只有四点：
1. **自由度**：裸 CDP + 任意 Python，无预制抽象——预制 adapter 失灵时理论上限更高；
2. **自沉淀**：`agent_helpers.py` 每次调用动态 import、与核心 helper 平权 + `domain-skills/<host>/*.md` 散文 runbook（自带 97 个站点示例）——但 opencli 这类开源工具的 sitemap / adapter 体系（结构化 schema/verify/fixture）已覆盖同职责；
3. `fetch-use` 反爬 HTTP 代理；
4. Browser Use Cloud 远程浏览器（多数个人场景无此需求）。

结论：增量是「自由度」而非「能力面」，不构成「显著提升」的引入门槛。

## 3. 最小实测

- 对仓库做静态安全扫描，命中的高危项集中在**一个根因**——官方链路以 `curl -fsSL https://browser-use.com/profile.sh | sh` 安装 profile-use（cookie 同步组件），这类「管道盲装」与可复现 / hermetic 依赖原则冲突。其余告警绝大多数是 Chrome UA 版本串（如 `Chrome/122.0.0.0`）被 IP 字面量规则误报的假阳。
- `uvx --python 3.12 browser-harness --help` 临时环境跑通（12 包，隔离，无全局残留）。未做真实 Chrome 驱动实测——那需要给本机 Chrome 开 remote-debugging 授权面，引入未决前不开；源码 + 测试套件审读补位。

## 4. 成本面

- 安装形态干净：`uv tool install --python 3.12`（隔离 venv）+ `browser-harness skill > SKILL.md`；状态收敛在 `~/.config/browser-harness`。
- **安全面是最大负项**：无沙箱裸 `exec`（设计如此，非疏漏）× 默认自动发现并直连用户真实 Chrome profile（硬编码 28 个 profile 路径扫描）= 注入或生成代码 bug 的爆炸半径为「真实登录会话 + 本机 shell 全权限」。护栏（登录墙 / MFA 停下问人）纯提示词约定，无技术强制。真实浏览器 profile 常驻登录态（银行 / 付费等）时风险不对称。
- telemetry 默认开（opt-out，PostHog；脱敏黑名单较认真）。
- token 面：skill 列表 +1，且与既有浏览器工具在同一意图上抢答 → 增加路由歧义。

## 5. 建议（人拍板）

**现阶段不引入。** 与成熟浏览器驱动工具主场景重叠 ≥70%，增量是自由度不是能力；换来的是裸 exec × 真实登录态的安全面、alpha 成熟度和 curl|sh 依赖链。

**重评条件（满足任一）**：
1. 发布 beta / 1.0 且出现代码执行沙箱或权限边界；
2. opencli 这类主力开源浏览器工具停更 3 个月（届时其 adapter / sitemap 体系失去维护，harness 的「写代码自愈」模式价值反转）；
3. 真实工作流中出现预制 adapter 反复失灵、且「写代码自愈」被证明是解法的具体案例（≥3 次）。

值得白拿的想法（无需引入）：domain-skills 的「per-host 坑位 runbook」与结构化 sitemap 同构，其 97 个站点示例可当 sitemap 编写参考语料。
