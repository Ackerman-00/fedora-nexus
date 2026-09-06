#!/bin/bash
# update.sh for python-mprisify (GitLab tag tracking - no PyPI releases)
#
# This package MUST have its own updater. The generic release scanner in
# .github/workflows/update-engine.yml only rewrites "Version:" - it does not
# reset Release and does not add a %changelog entry. Packages with an
# update.sh are skipped by that scanner.

SPEC_FILE="python-mprisify.spec"
GITLAB_PROJECT="zehkira%2Fmprisify"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking GitLab tags for zehkira/mprisify..."

# Newest stable tag first (skip pre-releases like v1.0.0-pre.4)
LATEST_TAG=$(python3 -c "
import json,urllib.request
tags = json.load(urllib.request.urlopen('https://gitlab.com/api/v4/projects/$GITLAB_PROJECT/repository/tags?per_page=20&order_by=updated',timeout=20))
import re
stable = [t['name'] for t in tags if re.match(r'^v?[0-9]+\.[0-9]+\.[0-9]+$', t['name'] or '')]
print(stable[0] if stable else '')
" 2>/dev/null)
LATEST_VERSION=${LATEST_TAG#v}

if [ -z "$LATEST_VERSION" ]; then
    echo "  -> [ERROR] Failed to fetch latest tag."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$LATEST_VERSION" == "$CURRENT_VERSION" ]; then
    echo "  -> [OK] Package is already at $CURRENT_VERSION. No update needed."
    exit 0
fi

echo "  -> [UPDATE] $CURRENT_VERSION -> $LATEST_VERSION"

# New upstream version -> Release restarts at 1 (rpm-version(7)).
sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

DATE=$(LC_ALL=C date +"%a %b %d %Y")
CHANGELOG_ENTRY="* $DATE $PACKAGER - $LATEST_VERSION-1\n- Auto-update to upstream tag $LATEST_TAG\n"
if grep -q '^%changelog' "$SPEC_FILE"; then
    sed -i "0,/^%changelog$/s//%changelog\n$CHANGELOG_ENTRY/" "$SPEC_FILE"
else
    printf '\n%%changelog\n%b' "$CHANGELOG_ENTRY" >> "$SPEC_FILE"
fi

echo "  -> [DONE] Successfully patched $SPEC_FILE."
