#!/usr/bin/env python3
"""Regression tests for tools/changelog-repair.py (run from the repo root).

Each case: (name, old_spec_tail_entries, new_spec_tail_entries, expect_repair)
Covers the real failure classes seen in the auto-updater.
"""
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "changelog_repair", Path(__file__).parent / "changelog-repair.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

HEAD = "%define name foo\nVersion: 1\nRelease: 2\n\n%description\nfoo\n\n"


def spec_text(entries, release="2"):
    body = HEAD.replace("Release: 2", f"Release: {release}")
    return body + "%changelog\n" + "\n\n".join(entries) + "\n"


CASES = [
    ("wipe-on-bump",
     ["* Mon Sep 01 2025 Ackerman-00 <quietcraft@gmail.com> - 1.0-1", "- old a",
      "* Sun Aug 03 2025 Ackerman-00 <quietcraft@gmail.com> - 0.9-1", "- old b"],
     ["* Sun Oct 04 2026 Ackerman-00 <quietcraft@gmail.com> - 1.1-1", "- new"], True),
    ("no-history-yet",
     ["* Sun Aug 03 2025 Ackerman-00 <quietcraft@gmail.com> - 0.9-1", "- old"],
     ["* Sun Oct 04 2026 Ackerman-00 <quietcraft@gmail.com> - 1.1-1", "- new"], True),
    ("already-good-insert-on-top",
     ["* Mon Sep 01 2025 Ackerman-00 <quietcraft@gmail.com> - 1.0-1", "- a"],
     ["* Sun Oct 04 2026 Ackerman-00 <quietcraft@gmail.com> - 1.1-1", "- new",
      "* Mon Sep 01 2025 Ackerman-00 <quietcraft@gmail.com> - 1.0-1", "- a"], False),
    ("scanner-style-insert",
     ["* Mon Sep 01 2025 Ackerman-00 <quietcraft@gmail.com> - 1.0-1", "- a"],
     ["* Sun Oct 04 2026 Nexus Auto-Updater <bot@github.com> - 1.1-1", "- Update",
      "* Mon Sep 01 2025 Ackerman-00 <quietcraft@gmail.com> - 1.0-1", "- a"], False),
    ("identical-noop",
     ["* Mon Sep 01 2025 Ackerman-00 <quietcraft@gmail.com> - 1.0-1", "- a"],
     ["* Mon Sep 01 2025 Ackerman-00 <quietcraft@gmail.com> - 1.0-1", "- a"], False),
    ("no-changelog-in-old",
     [], ["* Sun Oct 04 2026 Ackerman-00 <quietcraft@gmail.com> - 1.1-1", "- new"], False),
]


def main():
    failed = 0
    for name, old, new, expect in CASES:
        got = mod.repair(spec_text(old), spec_text(new))
        ok = (got is not None) == expect
        if ok and got is not None:
            e = mod.entries(mod.sections(got)[1])
            old_n = sum(1 for x in old if x.startswith('* '))
            new_n = sum(1 for x in new if x.startswith('* '))
            kept = old_n if any(x in new for x in old) else 0
            ok = len(e) == old_n + kept * 0 + (new_n - kept)
            ok = ok and e[0].startswith('* Sun Oct 04 2026')  # newest entry on top
            ok = ok and all(o in "\n\n".join(e) for o in old)  # history kept
            ok = ok and all(n in "\n\n".join(e) for n in new)  # new entry kept
        print(f"  {'ok' if ok else 'FAIL'}  {name} (repaired={got is not None})")
        failed += 0 if ok else 1
    print(f"changelog-repair tests: {len(CASES) - failed}/{len(CASES)} passed")
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())