#!/bin/bash
# MAINTENANCE: helium-browser is maintained MANUALLY in ackerman/nexus COPR only.
# Auto-update is DISABLED (2026-09-17): Helium re-releases often (Chromium
# rebuilds, sometimes tag-before-assets) and each bump re-downloads ~130MB,
# so updates are done deliberately by the maintainer, not by update-engine.yml.
# This intentional no-op keeps the generic scanner skipping helium-browser.spec
# (update-engine.yml skips specs that have an update.sh) while changing nothing.
echo "helium-browser is COPR-only, manually maintained (ackerman/nexus) — auto-update disabled, nothing to do."
exit 0
# Guard: an updater must never leave a spec without its header. If the
# changelog rewrite or a sed wiped the file, restore from git and fail loudly.
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
