# Card template — full spec

The complete contract for a docket card. The HTML comment block below is the formal spec; the two examples at the end are copyable templates.

<!--
Layout: capabilities/{active,archived}  (+ stateless kinds orchestrators/, surveys/)
  - capabilities/active/   ← what you're tracking now: pending (under evaluation) + imported (in use)
  - capabilities/archived/ ← decided testimony: rejected + eol (end-of-life).
                Not a permanent seal; a card can be re-opened when its
                re-assessment condition is met or the evidence changes.
  - validator scans these two subdirs, never recursing into hidden companion dirs.
  - orchestrators/ and surveys/ are stateless kinds (no adopt/retire cycle),
    reserved for future cards; this spec covers the capabilities state machine.

Filename: <name>-<state>.md
  - <name>: all-lowercase kebab, owner prefix dropped, keep the project-identifying
    name (`<owner>/<repo>` → `repo`). Exception: a multi-source topic (choosing
    among options for one problem, not a single repo) uses a `<topic-slug>` —
    these have no owner to strip.
  - state ∈ {pending, rejected, imported, eol}
  - the state token in the filename must equal frontmatter `state` (validator-enforced)
  - the state token is a technical identifier, ASCII only; body prose may be any language
  - no sequence numbers

Frontmatter fields:
  - name           required, must equal the <name> part of the filename (enforced)
  - state          required, 4-value enum (enforced)
  - last_assessed  by state (enforced):
                   - pending:  forbidden — the date lives in the body assessor links
                   - rejected/imported/eol: required, YYYY-MM-DD
  - github         optional. GitHub repo URL only (validator checks github.com format).
                   Omit for non-GitHub sources (npm/PyPI/vendor site) or multi-source topics.

Companion folder: a hidden `.name-state/` (stem matching the .md) placed next to its
card in the same subdir (capabilities/active/ or capabilities/archived/). Holds detailed docs (per-model notes,
screenshots, HTML, clusters, ...). The validator flags a hidden dir with no matching
.md as an orphan, and a non-hidden companion dir as a violation.

Body rules by state (enforced):

  pending (under evaluation, not yet decided):
    - body = link lines only, ≥1, format:
        `- [model](./.name-state/model.md) — YYYY-MM-DD · [📁](./.name-state/)`
    - when the companion folder exists, the link line must also link the folder
      itself (`· [📁](./.name-state/)`) so its other resources stay reachable (enforced).
    - no prose `## ` sections; put analysis in the companion folder notes (free format).
    - the link date IS the assessment date (pending has no frontmatter last_assessed).

  rejected/imported/eol (decided):
    - body states the reasons — at least one `## ` section explaining the decision.
    - frontmatter carries last_assessed.

State transitions:
  - pending/imported live in active/; rejected/eol live in archived/.
  - archived is not a one-way terminal: a rejected/eol card can move back to active/
    and re-enter the pending/imported flow when its re-assessment condition is met.
  - record the re-assessment reason in the card. Triggers include: single-model
    verdict never cross-checked, the original basis is now doubtful, a stronger
    assessor or a stronger experimental method became available.

Self-check (mechanical: filename ↔ frontmatter + link targets exist):
  python3 validate.py .
-->

---

## pending — no last_assessed, body = link lines only

```markdown
---
name: <name>
state: pending
github: https://github.com/<owner>/<repo>   # optional; omit for non-GitHub sources
---

# <repo-name> — <short positioning>

- [model](./.<name>-pending/model.md) — YYYY-MM-DD · [📁](./.<name>-pending/)
```

## decided — has last_assessed, body states reasons

```markdown
---
name: <name>
state: rejected
last_assessed: YYYY-MM-DD
github: https://github.com/<owner>/<repo>   # optional; omit for non-GitHub sources
---

# <repo-name> — <short positioning>

## Reason (rejected / imported / eol)

...
```
