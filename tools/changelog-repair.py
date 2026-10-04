#!/usr/bin/env python3
"""Repair %changelog history that a per-package update.sh wiped.

Tested by tools/test-changelog-repair.py. Wired into .github/workflows/
update-engine.yml as a fail-safe step before the commit.
"""
import re
import subprocess
import sys
from pathlib import Path

ENTRY_RE = re.compile(r'^\* ')


def sections(text):
    """Split a spec into (before_changelog, changelog_section)."""
    m = re.search(r'^%changelog\s*$', text, re.MULTILINE)
    if not m:
        return text, None
    return text[:m.start()], text[m.start():]


def entries(section):
    """Changelog entry blocks (a '*' line plus its continuation lines).

    Blank lines are separators, not content, so they never end up inside a
    block and the re-joined section keeps the repo's normal one-blank-line
    spacing between entries.
    """
    if not section:
        return []
    out = []
    for line in section.splitlines()[1:]:
        if not line.strip():
            continue
        if ENTRY_RE.match(line) or not out:
            out.append([line])
        else:
            out[-1].append(line)
    return ['\n'.join(e).rstrip() for e in out]


def repair(old_text, new_text):
    """Return new_text with history preserved, or None when nothing to do."""
    _, old_sec = sections(old_text)
    _, new_sec = sections(new_text)
    if new_sec is None or old_sec is None:
        return None
    old_e, new_e = entries(old_sec), entries(new_sec)
    if not old_e:
        return None
    if [e for e in old_e if e not in new_e] == [] and len(new_e) >= len(old_e):
        return None  # history intact
    fresh = [e for e in new_e if e not in old_e]
    kept = [e for e in old_e if e in new_e] or old_e
    merged, seen = [], set()
    for e in fresh + kept + [e for e in new_e if e not in old_e and e not in fresh]:
        if e not in seen:
            seen.add(e)
            merged.append(e)
    body = '%changelog\n' + '\n\n'.join(merged) + '\n'
    return sections(new_text)[0] + body


def main():
    changed = subprocess.run(['git', 'diff', '--name-only'], capture_output=True,
                             text=True, check=True).stdout.split()
    repaired = 0
    for path in changed:
        if not path.endswith('.spec'):
            continue
        p = Path(path)
        if not p.exists():
            continue
        old = subprocess.run(['git', 'show', f'HEAD:{path}'], capture_output=True,
                             text=True)
        if old.returncode != 0:
            continue
        new_text = p.read_text(encoding='utf-8')
        fixed = repair(old.stdout, new_text)
        if fixed is not None:
            p.write_text(fixed, encoding='utf-8')
            repaired += 1
            print(f"  -> [REPAIRED] {path}: changelog history restored")
    print(f"changelog-repair: {repaired} spec(s) repaired")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:  # never break the auto-updater
        print(f"changelog-repair: skipped ({exc})")
        sys.exit(0)