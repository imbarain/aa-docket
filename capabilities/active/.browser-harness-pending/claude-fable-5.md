# browser-harness deep review — claude-fable-5, 2026-07-05

> Executed along five dimensions (upstream health / functional differentiation / minimal hands-on test / cost surface / recommendation); source evidence comes from reading a full-history clone (431 commits).

## 0. Positioning

A new-form product from the browser-use company: not an "agent with a built-in LLM loop" (that was browser-use's earlier flagship product line), but the reverse — a harness where "the LLM directly writes Python code speaking raw CDP." `run.py:180` bare-`exec()`s the code from stdin, a daemon holds a long-lived connection to a real Chrome, the helper primitives are 508 lines, and it additionally exposes `cdp(method, **params)` for arbitrary CDP calls. Explicitly positioned as a skill to drop into Claude Code / Codex.

## 1. Upstream health

- Repo created 2026-04-17, 2.5 months old at assessment time; 15.7k stars / 1.4k forks / 162 open issues / 60+ contributors. Halo effect of the browser-use parent company (main repo 102k stars, has a commercial Cloud line) — **under a parent-company halo, discount the star count to ~30%**, and parent-company resources ≠ a commitment to this repo.
- Version 0.1.4, classifier explicitly marks `Development Status :: 3 - Alpha`.
- Cadence: a burst of 95 commits over 6 days in early May scaffolded it → single-digit commits from mid-month on, multi-week gaps → a small burst at end of June; last push 2026-07-01. **Burst-then-cooldown type**, not a daily-active repo.
- A surprisingly good signal: tests 1,933 lines / source 2,978 lines (≈65%), covering the daemon lifecycle, IPC token, and PID-reuse races — a production-grade mindset.

## 2. Functional differentiation (vs. comparable browser-driving tools)

The primary scenario "drive a real, logged-in Chrome for ad-hoc browser operations" **overlaps ≥70%** with mature open-source browser-driving tools (e.g. opencli's browser mode): bind to a real tab, eval JS, network capture, the full form family, extract — these tools all have them, and most have already absorbed the accessibility patterns of AX snapshot / refs.

The genuine increment is only four points:
1. **Degrees of freedom**: raw CDP + arbitrary Python, no pre-built abstractions — a theoretically higher ceiling when a pre-built adapter fails;
2. **Self-accretion**: `agent_helpers.py` is dynamically imported on each call, on equal footing with the core helpers, plus `domain-skills/<host>/*.md` prose runbooks (ships with 97 site examples) — but the sitemap / adapter systems of open-source tools like opencli (structured schema/verify/fixture) already cover this same responsibility;
3. `fetch-use`, an anti-scraping HTTP proxy;
4. Browser Use Cloud remote browsers (most personal scenarios have no such need).

Conclusion: the increment is "degrees of freedom," not "capability surface," and does not constitute a "significant improvement" bar that justifies adoption.

## 3. Minimal hands-on test

- A static security scan of the repo — the high-severity hits it triggered concentrate on **one root cause**: the official path installs profile-use (the cookie-sync component) via `curl -fsSL https://browser-use.com/profile.sh | sh`, and this kind of "pipe-and-blindly-install" conflicts with the reproducible / hermetic-dependency principle. The vast majority of the remaining warnings are false positives — Chrome UA version strings (e.g. `Chrome/122.0.0.0`) misfired by IP-literal rules.
- `uvx --python 3.12 browser-harness --help` ran in a throwaway environment (12 packages, isolated, no global residue). No real Chrome-driving test was done — that would require opening a remote-debugging authorization surface on the local Chrome, which I won't open for an undecided candidate; source + test-suite reading fills the gap.

## 4. Cost surface

- Install form is clean: `uv tool install --python 3.12` (isolated venv) + `browser-harness skill > SKILL.md`; state converges under `~/.config/browser-harness`.
- **The security surface is the biggest negative**: sandbox-less bare `exec` (by design, not an oversight) × auto-discovering and directly connecting to the user's real Chrome profile by default (hardcoded scan of 28 profile paths) = the blast radius of an injection or a bug in generated code is "a real logged-in session + full local shell privileges." The guardrails (login wall / stop-and-ask on MFA) are pure prompt conventions, no technical enforcement. When the real browser profile carries persistent login state (banking / paid accounts / etc.), the risk is asymmetric.
- Telemetry on by default (opt-out, PostHog; the scrubbing blacklist is fairly conscientious).
- Token surface: +1 in the skill list, and it competes for the same intent as existing browser tools → adds routing ambiguity.

## 5. Recommendation (human decides)

**Do not adopt at this stage.** ≥70% overlap in the primary scenario with mature browser-driving tools; the increment is degrees of freedom, not capability. What you'd trade for it: a bare-exec × real-login-state security surface, alpha maturity, and a curl|sh dependency chain.

**Re-assessment conditions (any one)**:
1. A beta / 1.0 ships and a code-execution sandbox or permission boundary appears;
2. A mainstream open-source browser tool like opencli goes 3 months without updates (at which point its adapter / sitemap system loses maintenance and the harness's "write-code-to-self-heal" model reverses in value);
3. A concrete case appears in a real workflow where a pre-built adapter repeatedly fails and "write-code-to-self-heal" is proven to be the solution (≥3 times).

An idea worth taking for free (no adoption needed): domain-skills' "per-host pitfall runbook" is isomorphic to a structured sitemap, and its 97 site examples can serve as reference corpus for writing sitemaps.
