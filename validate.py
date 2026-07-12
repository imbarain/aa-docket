#!/usr/bin/env python3
"""Validate docket cards under capabilities/{active,archived}.

Layout: {active,archived}/*.md — active holds pending+imported,
archived holds rejected+eol. A flat layout (*.md in one dir) is also
accepted; see expand_scan_roots.

Contract (kept deliberately minimal):
  - filename matches pattern <name>-<state>.md  where state ∈ {pending, rejected, imported, eol}
  - frontmatter `state` matches the state token in filename
  - frontmatter `name` matches the <name> part of filename
  - state value is one of the 4 allowed values
  - last_assessed: required for imported/rejected/eol; forbidden for pending
  - companion folders must be hidden `.name-state/` matching an .md stem;
    a non-hidden dir is itself a violation, a hidden dir with no matching .md
    is an orphan
  - body content rules by state:
      pending:   body = assessor links only — ≥1 link, no prose `## ` sections.
                 The link date IS the assessment date (pending has no frontmatter
                 last_assessed), so requiring ≥1 link guarantees a freshness date.
                 When the companion folder .name-state/ exists, each assessor
                 link line must also link the folder itself so the rest of the
                 folder's resources (html, clusters, ...) are reachable:
                   `[model](./.name-state/model.md) — YYYY-MM-DD · [📁](./.name-state/)`
      imported/rejected/eol: body must have substantive reasons (`## ` sections)
  - assessor links: `[model](./.name-state/model.md) — YYYY-MM-DD`
    targets validated for existence

Body content (prose) is NOT validated and may be in any language; only the
state token — a technical identifier appearing in filenames, frontmatter, and
validator code — is constrained to ASCII for grep/tooling robustness.

Coined rationale for the 4 tokens (2026-06-24):
  pending   — under evaluation, no decision yet
  rejected  — evaluated, decision is no
  imported  — adopted into the stack
  eol       — was in stack, removed (industry-standard "end of life")
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ALLOWED_STATES = ("pending", "rejected", "imported", "eol")
# v2 layout: active/ and archived/ are the manifest-carrying subdirs.
LAYOUT_SUBDIRS = ("active", "archived")
NAME_RE = re.compile(
    rf"^(?P<name>[^-]+(?:-[^-]+)*)-(?P<state>{'|'.join(ALLOWED_STATES)})\.md$"
)
# Optional github frontmatter field — when present must be a github.com repo URL.
GITHUB_RE = re.compile(r"^https://github\.com/[^/]+/[^/]+/?$")
#   [model](./.name-state/model.md) — YYYY-MM-DD
LINK_LINE_RE = re.compile(
    r"\[([^\]]+)\]\(([^)]+)\)\s*[—\-]\s*(\d{4}-\d{2}-\d{2})"
)
# Folder-self link appended to an assessor line when the companion folder exists:
#   · [📁](./.name-state/)   — trailing slash distinguishes the folder from a file.
def folder_link_re(stem: str) -> re.Pattern[str]:
    return re.compile(rf"\]\(\./\.{re.escape(stem)}/\)")
# `## ` heading = prose section (not assessor link)
PROSE_HEADING_RE = re.compile(r"^## ", re.MULTILINE)


def split_doc(text: str) -> tuple[str | None, str]:
    """Split a markdown doc into (frontmatter, body).

    frontmatter is the text between the leading `---` fences, or None if the
    doc has no well-formed frontmatter. body is everything after the closing
    fence (empty when frontmatter is None). One read, no re-parsing.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, ""
    fm: list[str] = []
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(fm) + "\n", "\n".join(lines[i + 1 :])
        fm.append(line)
    return None, ""  # unterminated frontmatter


def parse_yaml(frontmatter: str) -> dict | None:
    """Parse the frontmatter block with yq (see README Requirements)."""
    proc = subprocess.run(
        ["yq", "-o=json", "."],
        input=frontmatter,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    import json

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def check_file(
    path: Path, filename_name: str, filename_state: str, fm_str: str | None
) -> tuple[list[str], dict | None]:
    """Validate frontmatter against the filename tokens.

    Returns (errors, parsed_frontmatter). parsed_frontmatter is None when the
    frontmatter is missing or unparseable — callers skip body-state checks then.
    """
    errors: list[str] = []

    if fm_str is None:
        errors.append(f"{path.name}: missing or malformed YAML frontmatter (need `---` fences)")
        return errors, None

    fm = parse_yaml(fm_str)
    if fm is None:
        errors.append(f"{path.name}: frontmatter is not valid YAML")
        return errors, None

    fm_state = fm.get("state")
    if fm_state is None:
        errors.append(f"{path.name}: frontmatter missing required `state` field")
    elif fm_state not in ALLOWED_STATES:
        errors.append(
            f"{path.name}: frontmatter state={fm_state!r} not in {ALLOWED_STATES}"
        )
    elif fm_state != filename_state:
        errors.append(
            f"{path.name}: state mismatch — filename token is {filename_state!r} "
            f"but frontmatter state is {fm_state!r}"
        )

    fm_name = fm.get("name")
    if fm_name is None:
        errors.append(f"{path.name}: frontmatter missing required `name` field")
    elif fm_name != filename_name:
        errors.append(
            f"{path.name}: name mismatch — filename slug is {filename_name!r} "
            f"but frontmatter name is {fm_name!r}"
        )

    # last_assessed: forbidden for pending, required for concluded states
    if fm_state == "pending":
        if "last_assessed" in fm:
            errors.append(
                f"{path.name}: pending card must not have `last_assessed` "
                f"— date is per-assessor in body links"
            )
    else:
        if "last_assessed" not in fm:
            errors.append(
                f"{path.name}: {fm_state} card must have `last_assessed` (YYYY-MM-DD)"
            )

    # Optional github field — when present, must be a github.com repo URL.
    # Non-GitHub sources (npm/PyPI/vendor site) or multi-source topics omit it.
    if "github" in fm and not GITHUB_RE.match(str(fm["github"]).strip()):
        errors.append(
            f"{path.name}: frontmatter `github` must be a github.com repo URL "
            f"(got {fm['github']!r}); omit the field for non-GitHub sources"
        )

    return errors, fm


def check_body_state_rules(path: Path, body: str, state: str) -> list[str]:
    """Pending: body must not contain prose sections (only assessor links + optional title).
    Non-pending: body must have substantive reasons (at least one `## ` section).
    """
    errors: list[str] = []
    has_prose = bool(PROSE_HEADING_RE.search(body))

    if state == "pending":
        if has_prose:
            errors.append(
                f"{path.name}: pending card body must not contain prose sections "
                f"(found '## ' heading); move analysis into companion folder assessor files"
            )
        if not LINK_LINE_RE.search(body):
            errors.append(
                f"{path.name}: pending card must have ≥1 assessor link "
                f"`[model](./.name-state/model.md) — YYYY-MM-DD` "
                f"(the link date is the assessment date)"
            )
        # When the companion folder exists, its other resources (html, clusters,
        # screenshots, ...) are only reachable if the card links the folder itself.
        companion = path.parent / f".{path.stem}"
        if companion.is_dir() and not folder_link_re(path.stem).search(body):
            errors.append(
                f"{path.name}: pending card has companion folder .{path.stem}/ "
                f"but does not link it — append "
                f'" · [📁](./.{path.stem}/)" to the assessor link line'
            )
    else:
        if not has_prose:
            errors.append(
                f"{path.name}: {state} card body must contain reasons "
                f"(at least one '## ' section explaining the decision)"
            )

    return errors


# All relative links (./ or ../), not just dated assessor lines — concluded cards
# link companion attachments without a date and those went unchecked before.
REL_LINK_RE = re.compile(r"\[([^\]]+)\]\((\.\.?/[^)#]+)")


def check_body_links(path: Path, body: str) -> list[str]:
    """Validate that every relative link target in body exists."""
    errors: list[str] = []
    for m in REL_LINK_RE.finditer(body):
        label, target = m.group(1), m.group(2)
        target_path = (path.parent / target).resolve()
        if not target_path.exists():
            errors.append(
                f"{path.name}: link [{label}] → {target} does not exist"
            )
    return errors


def check_orphan_dirs(scan_root: Path, valid_stems: set[str]) -> list[str]:
    """Companion folders must be hidden `.name-state/` matching an .md stem.

    A non-hidden directory is itself a violation (convention is hidden-only);
    a hidden directory whose stem has no matching .md is an orphan.
    Run per scan-root (active/ or archived/ or a flat fixture dir), never on the
    capabilities/ or repo root itself — that would flag the layout subdirs
    active/archived as non-hidden.
    """
    errors: list[str] = []
    for entry in scan_root.iterdir():
        if not entry.is_dir():
            continue
        name = entry.name
        if not name.startswith("."):
            errors.append(
                f"{name}/: orphan folder — companion folders must be hidden (.{name}/)"
            )
            continue
        if name[1:] not in valid_stems:
            errors.append(
                f"{name}/: orphan folder "
                f"(no matching <name>-<state>.md in {scan_root.name}/)"
            )
    return errors


def expand_scan_roots(paths: list[Path]) -> tuple[list[Path], list[str]]:
    """Expand the repo root into its capability layout subdirs (active/, archived/).

    v3 layout: capability cards live under capabilities/{active,archived}/. When a
    passed dir has a capabilities/ subdir it is the layout base; otherwise the dir
    itself is (so the flat single-layer test fixtures keep working). Within the
    base, active/ and/or archived/ become the scan roots; the base and repo root
    (and their non-hidden nature) are exempt from orphan checks. orchestrators/ and
    surveys/ are stateless kinds with no cards yet — they carry no scan rule here.

    Returns (scan_roots, errors). A dir that has layout subdirs but also stray
    top-level *.md (besides TEMPLATE.md) reports an error each — those would be
    silently skipped once subdirs take over, and a partial migration leaving a
    card at root is exactly the failure mode this validator exists to catch.
    """
    expanded: list[Path] = []
    errors: list[str] = []
    for p in paths:
        if p.is_dir():
            cap = p / "capabilities"
            base = cap if cap.is_dir() else p
            subdirs = [base / s for s in LAYOUT_SUBDIRS if (base / s).is_dir()]
            if subdirs:
                expanded.extend(subdirs)
                strays = [
                    f.name for f in base.glob("*.md") if f.name != "TEMPLATE.md"
                ]
                for name in strays:
                    errors.append(
                        f"{name}: stranded outside active/archived/ — that layout "
                        f"is present, move it into the matching subdir or it is "
                        f"silently ignored"
                    )
                continue
        expanded.append(p)
    return expanded, errors


def main(argv: list[str]) -> int:
    if not argv:
        argv = ["."]

    paths = [Path(p).expanduser() for p in argv]
    scan_roots, all_errors = expand_scan_roots(paths)
    # Top-level *.md per scan root only — companion detail folders are exempt.
    files = sorted(
        f
        for p in scan_roots
        for f in (p.glob("*.md") if p.is_dir() else [p])
        if f.name != "TEMPLATE.md"
    )

    if not files:
        print("no files to check", file=sys.stderr)
        return 1

    # Group files by scan root so orphan checks are per-subdir (active/ vs archived/),
    # not against the global stem set — a hidden folder in active/ is not an orphan
    # just because its md stem lives in archived/.
    files_by_root: dict[Path, list[Path]] = {}
    for f in files:
        files_by_root.setdefault(f.parent, []).append(f)

    for root, root_files in files_by_root.items():
        valid_stems: set[str] = set()
        for f in root_files:
            m = NAME_RE.match(f.name)
            if not m:
                all_errors.append(
                    f"{f.name}: filename must match <name>-<state>.md "
                    f"where state ∈ {ALLOWED_STATES}"
                )
                continue
            filename_name, filename_state = m.group("name"), m.group("state")
            valid_stems.add(f.stem)

            fm_str, body = split_doc(f.read_text(encoding="utf-8"))
            errs, fm = check_file(f, filename_name, filename_state, fm_str)
            all_errors.extend(errs)
            all_errors.extend(check_body_links(f, body))
            # Body-state rules only when frontmatter state agrees with the filename
            # token; a mismatch is already reported, no need to pile on a body error
            # keyed off the (possibly wrong) filename token.
            if fm is not None and fm.get("state") == filename_state:
                all_errors.extend(check_body_state_rules(f, body, filename_state))

        # Orphan folder check: only inside a real scan-root dir.
        if root.is_dir():
            all_errors.extend(check_orphan_dirs(root, valid_stems))

    checked = len(files)
    if all_errors:
        print(f"✘ validate-docket: {len(all_errors)} error(s) across {checked} file(s)")
        for e in all_errors:
            print(f"  {e}")
        return 1

    state_tokens = []
    for f in files:
        m = NAME_RE.match(f.name)
        assert m is not None
        state_tokens.append(m.group("state"))
    states = sorted(set(state_tokens))
    print(f"✓ validate-docket: {checked} file(s) ok, states={states}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
