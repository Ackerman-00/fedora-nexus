#!/bin/bash
# MAINTENANCE: zed is maintained MANUALLY in ackerman/nexus COPR only.
# Auto-update is DISABLED (2026-09-17): upstream publishes 2-3 builds per
# week and every bump is a multi-hour COPR Rust build, so updates are done
# deliberately by the maintainer, not by update-engine.yml.
# This intentional no-op keeps the generic scanner skipping zed.spec
# (update-engine.yml skips specs that have an update.sh) while changing nothing.
echo "zed is COPR-only, manually maintained (ackerman/nexus) — auto-update disabled, nothing to do."
exit 0
