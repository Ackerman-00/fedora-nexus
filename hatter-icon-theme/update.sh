#!/usr/bin/env bash
# owner 2026-11-14: auto-update disabled; updates are published by Ackerman-00
if [ -z "${NEXUS_OWNER_UPDATE:-}" ]; then
    echo "auto-update disabled (owner rule 2026-11-14); updates are published manually by Ackerman-00"
    exit 0
fi
set -u
echo "icon theme updates managed manually." 
