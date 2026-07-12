#!/usr/bin/env bash
# Tests for the docket-card validator.
# Pattern: fixture folders + expected output, checked by grep.
set -eEuo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
VALIDATOR="$REPO/validate.py"
FIXTURE_DIR="$(mktemp -d)"
trap 'rm -rf "$FIXTURE_DIR"' EXIT

fail() { echo "✘ $*" >&2; exit 1; }
pass() { echo "✓ $*"; }

# --- 1. happy path: all 4 states valid (pending vs concluded have different body rules)
mkdir -p "$FIXTURE_DIR/ok"
# pending: no last_assessed, body = assessor links only
mkdir -p "$FIXTURE_DIR/ok/.foo-pending"
cat > "$FIXTURE_DIR/ok/foo-pending.md" <<'EOF'
---
name: foo
state: pending
---

- [opus](./.foo-pending/opus.md) — 2026-06-24 · [📁](./.foo-pending/)
EOF
echo "# test" > "$FIXTURE_DIR/ok/.foo-pending/opus.md"
# concluded states: last_assessed + prose reasons
for s in rejected imported eol; do
  cat > "$FIXTURE_DIR/ok/foo-$s.md" <<EOF
---
name: foo
state: $s
last_assessed: 2026-06-24
---

# foo — test

## 理由

some reason here
EOF
done
python3 "$VALIDATOR" "$FIXTURE_DIR/ok" >/dev/null || fail "happy path should pass"
pass "all 4 states valid"

# --- 2. filename ↔ frontmatter state mismatch
mkdir -p "$FIXTURE_DIR/bad-state"
cat > "$FIXTURE_DIR/bad-state/foo-pending.md" <<'EOF'
---
name: foo
state: rejected
last_assessed: 2026-06-24
---
EOF
out=$(python3 "$VALIDATOR" "$FIXTURE_DIR/bad-state" 2>&1) || true
echo "$out" | grep -q "state mismatch" || fail "should detect state mismatch"
pass "filename ↔ frontmatter state mismatch detected"

# --- 3. invalid state enum
mkdir -p "$FIXTURE_DIR/bad-enum"
cat > "$FIXTURE_DIR/bad-enum/foo-deprecated.md" <<'EOF'
---
name: foo
state: deprecated
last_assessed: 2026-06-24
---
EOF
out=$(python3 "$VALIDATOR" "$FIXTURE_DIR/bad-enum" 2>&1) || true
echo "$out" | grep -q "where state" || fail "should detect invalid state enum in filename"
pass "invalid state enum in filename detected"

# --- 4. missing frontmatter
mkdir -p "$FIXTURE_DIR/no-fm"
echo "# no frontmatter here" > "$FIXTURE_DIR/no-fm/foo-pending.md"
out=$(python3 "$VALIDATOR" "$FIXTURE_DIR/no-fm" 2>&1) || true
echo "$out" | grep -q "missing or malformed YAML frontmatter" || fail "should detect missing frontmatter"
pass "missing frontmatter detected"

# --- 5. name ↔ filename slug mismatch
mkdir -p "$FIXTURE_DIR/bad-name"
cat > "$FIXTURE_DIR/bad-name/foo-bar-rejected.md" <<'EOF'
---
name: baz
state: rejected
last_assessed: 2026-06-24
---

## 理由
test
EOF
out=$(python3 "$VALIDATOR" "$FIXTURE_DIR/bad-name" 2>&1) || true
echo "$out" | grep -q "name mismatch" || fail "should detect name mismatch"
pass "name ↔ filename slug mismatch detected"

# --- 7. detail folder with full stem (including state) is allowed
mkdir -p "$FIXTURE_DIR/folder-ok/.foo-pending"
cat > "$FIXTURE_DIR/folder-ok/foo-pending.md" <<'EOF'
---
name: foo
state: pending
---

- [opus](./.foo-pending/opus.md) — 2026-06-24 · [📁](./.foo-pending/)
EOF
echo "# any content" > "$FIXTURE_DIR/folder-ok/.foo-pending/opus.md"
python3 "$VALIDATOR" "$FIXTURE_DIR/folder-ok" >/dev/null || fail "same-name detail folder should pass"
pass "same-stem detail folder allowed"

# --- 8. detail folder missing state suffix is rejected (was previously too lax)
mkdir -p "$FIXTURE_DIR/folder-no-state/foo"
cat > "$FIXTURE_DIR/folder-no-state/foo-pending.md" <<'EOF'
---
name: foo
state: pending
---
EOF
out=$(python3 "$VALIDATOR" "$FIXTURE_DIR/folder-no-state" 2>&1) || true
echo "$out" | grep -q "orphan folder" || fail "should reject folder without state suffix"
pass "folder without state suffix rejected"

# --- 9. orphan detail folder (no matching MD at all) is rejected
mkdir -p "$FIXTURE_DIR/folder-orphan/ghost-pending"
echo "# detail without MD" > "$FIXTURE_DIR/folder-orphan/ghost-pending/note.md"
cat > "$FIXTURE_DIR/folder-orphan/real-pending.md" <<'EOF'
---
name: real
state: pending
---
EOF
out=$(python3 "$VALIDATOR" "$FIXTURE_DIR/folder-orphan" 2>&1) || true
echo "$out" | grep -q "orphan folder" || fail "should detect orphan folder"
pass "orphan folder detected"

# --- 10. rejects 中文 state token (legacy migrated away)
mkdir -p "$FIXTURE_DIR/legacy"
cat > "$FIXTURE_DIR/legacy/foo-研究中.md" <<'EOF'
---
name: foo
state: 研究中
last_assessed: 2026-06-24
---
EOF
out=$(python3 "$VALIDATOR" "$FIXTURE_DIR/legacy" 2>&1) || true
echo "$out" | grep -q "where state" || fail "should reject 中文 state token"
pass "中文 state token rejected"

# --- 11. pending body with prose section is rejected
mkdir -p "$FIXTURE_DIR/pending-prose/.foo-pending"
cat > "$FIXTURE_DIR/pending-prose/foo-pending.md" <<'EOF'
---
name: foo
state: pending
---

- [opus](./.foo-pending/opus.md) — 2026-06-24 · [📁](./.foo-pending/)

## 不该出现的散文
analysis belongs in the companion file
EOF
echo "# test" > "$FIXTURE_DIR/pending-prose/.foo-pending/opus.md"
out=$(python3 "$VALIDATOR" "$FIXTURE_DIR/pending-prose" 2>&1) || true
echo "$out" | grep -q "must not contain prose" || fail "should reject pending body with prose"
pass "pending body with prose rejected"

# --- 12. concluded card without prose reasons is rejected
mkdir -p "$FIXTURE_DIR/concluded-no-prose"
cat > "$FIXTURE_DIR/concluded-no-prose/foo-rejected.md" <<'EOF'
---
name: foo
state: rejected
last_assessed: 2026-06-24
---

just a line, no heading explaining why
EOF
out=$(python3 "$VALIDATOR" "$FIXTURE_DIR/concluded-no-prose" 2>&1) || true
echo "$out" | grep -q "must contain reasons" || fail "should reject concluded card without prose"
pass "concluded card without prose rejected"

# --- 13. pending card with no assessor link is rejected (freshness date blind spot)
mkdir -p "$FIXTURE_DIR/pending-no-link"
cat > "$FIXTURE_DIR/pending-no-link/foo-pending.md" <<'EOF'
---
name: foo
state: pending
---

(no assessor link, so no assessment date anywhere)
EOF
out=$(python3 "$VALIDATOR" "$FIXTURE_DIR/pending-no-link" 2>&1) || true
echo "$out" | grep -q "must have ≥1 assessor link" || fail "should reject pending without assessor link"
pass "pending without assessor link rejected"

# --- 14. non-hidden companion dir is rejected even when its name matches a stem
mkdir -p "$FIXTURE_DIR/visible-companion/foo-pending"
cat > "$FIXTURE_DIR/visible-companion/foo-pending.md" <<'EOF'
---
name: foo
state: pending
---

- [opus](./foo-pending/opus.md) — 2026-06-24
EOF
echo "# test" > "$FIXTURE_DIR/visible-companion/foo-pending/opus.md"
out=$(python3 "$VALIDATOR" "$FIXTURE_DIR/visible-companion" 2>&1) || true
echo "$out" | grep -q "must be hidden" || fail "should reject non-hidden companion folder"
pass "non-hidden companion folder rejected"

# --- 15. pending with companion folder but no folder link is rejected
mkdir -p "$FIXTURE_DIR/pending-no-folder-link/.foo-pending"
cat > "$FIXTURE_DIR/pending-no-folder-link/foo-pending.md" <<'EOF'
---
name: foo
state: pending
---

- [opus](./.foo-pending/opus.md) — 2026-06-24
EOF
echo "# test" > "$FIXTURE_DIR/pending-no-folder-link/.foo-pending/opus.md"
out=$(python3 "$VALIDATOR" "$FIXTURE_DIR/pending-no-folder-link" 2>&1) || true
echo "$out" | grep -q "does not link it" || fail "should reject pending missing the folder-self link"
pass "pending without folder link rejected"

# --- 16. flat layout: active/archived/ auto-expanded, root not flagged orphan
mkdir -p "$FIXTURE_DIR/v2-layout/active/.foo-pending" "$FIXTURE_DIR/v2-layout/archived"
cat > "$FIXTURE_DIR/v2-layout/active/foo-pending.md" <<'EOF'
---
name: foo
state: pending
github: https://github.com/o/foo
---

- [opus](./.foo-pending/opus.md) — 2026-06-24 · [📁](./.foo-pending/)
EOF
echo "# test" > "$FIXTURE_DIR/v2-layout/active/.foo-pending/opus.md"
cat > "$FIXTURE_DIR/v2-layout/archived/bar-eol.md" <<'EOF'
---
name: bar
state: eol
last_assessed: 2026-06-24
---

## 理由
test
EOF
python3 "$VALIDATOR" "$FIXTURE_DIR/v2-layout" >/dev/null || fail "v2 layout should pass; active/archived must not be flagged as non-hidden orphans"
pass "v2 active/archived layout accepted (root subdirs not flagged)"

# --- 17. github field format validated when present
mkdir -p "$FIXTURE_DIR/bad-github/.foo-pending"
cat > "$FIXTURE_DIR/bad-github/foo-pending.md" <<'EOF'
---
name: foo
state: pending
github: https://gitee.com/o/foo
---

- [opus](./.foo-pending/opus.md) — 2026-06-24 · [📁](./.foo-pending/)
EOF
echo "# test" > "$FIXTURE_DIR/bad-github/.foo-pending/opus.md"
out=$(python3 "$VALIDATOR" "$FIXTURE_DIR/bad-github" 2>&1) || true
echo "$out" | grep -q "must be a github.com repo URL" || fail "should reject non-github URL in github field"
pass "non-github URL in github field rejected"

# --- 18. v2 layout with a stranded root-level md must fail loud
# (partial migration leaving a card at root is silently skipped otherwise)
mkdir -p "$FIXTURE_DIR/stranded/active/.foo-pending" "$FIXTURE_DIR/stranded/archived"
cat > "$FIXTURE_DIR/stranded/active/foo-pending.md" <<'EOF'
---
name: foo
state: pending
---

- [opus](./.foo-pending/opus.md) — 2026-06-24 · [📁](./.foo-pending/)
EOF
echo "# test" > "$FIXTURE_DIR/stranded/active/.foo-pending/opus.md"
cat > "$FIXTURE_DIR/stranded/stray-pending.md" <<'EOF'
---
name: stray
state: pending
---
EOF
out=$(python3 "$VALIDATOR" "$FIXTURE_DIR/stranded" 2>&1) || true
echo "$out" | grep -q "stranded outside active/archived" || fail "should reject md stranded outside active/archived when that layout exists"
pass "stranded root-level md rejected (no silent skip)"

# --- 19. v3 layout: capability cards nested under capabilities/{active,archived}
mkdir -p "$FIXTURE_DIR/v3/capabilities/active/.foo-pending" "$FIXTURE_DIR/v3/capabilities/archived"
mkdir -p "$FIXTURE_DIR/v3/orchestrators" "$FIXTURE_DIR/v3/surveys"
cat > "$FIXTURE_DIR/v3/capabilities/active/foo-pending.md" <<'EOF'
---
name: foo
state: pending
---

- [opus](./.foo-pending/opus.md) — 2026-06-24 · [📁](./.foo-pending/)
EOF
echo "# test" > "$FIXTURE_DIR/v3/capabilities/active/.foo-pending/opus.md"
python3 "$VALIDATOR" "$FIXTURE_DIR/v3" >/dev/null || fail "v3 capabilities/ nesting should pass"
pass "v3 capabilities/{active,archived} layout accepted"

# --- 20. v3 layout: a card stranded at capabilities/ root must fail loud
cat > "$FIXTURE_DIR/v3/capabilities/stray-pending.md" <<'EOF'
---
name: stray
state: pending
---
EOF
out=$(python3 "$VALIDATOR" "$FIXTURE_DIR/v3" 2>&1) || true
echo "$out" | grep -q "stranded outside active/archived" || fail "should reject md stranded at capabilities/ root"
pass "stranded capabilities/-root md rejected (no silent skip)"

echo ""
echo "✓ all docket-card validator tests passed"
