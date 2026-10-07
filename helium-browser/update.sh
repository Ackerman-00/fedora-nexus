#!/bin/bash

# Run this from its own package directory. update-engine.yml does `pushd <pkg>`
# first; running update.sh from the repo root instead let the changelog append
# create a stray <pkg>.spec at the repo root, and the Name: check then reported
# a false corruption (hit twice, 2026-10-07: stray umbriel-git.spec, then 32
# stray root specs during an agent sweep).
_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi
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
