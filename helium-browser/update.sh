#!/bin/bash
# MAINTENANCE: helium-browser is maintained MANUALLY in ackerman/nexus COPR only.
# Auto-update is DISABLED (2026-09-17): Helium re-releases often (Chromium
# rebuilds, sometimes tag-before-assets) and each bump re-downloads ~130MB,
# so updates are done deliberately by the maintainer, not by update-engine.yml.
# This intentional no-op keeps the generic scanner skipping helium-browser.spec
# (update-engine.yml skips specs that have an update.sh) while changing nothing.
echo "helium-browser is COPR-only, manually maintained (ackerman/nexus) — auto-update disabled, nothing to do."
exit 0
