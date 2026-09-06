#!/bin/bash
# update.sh for python-pydbus (PyPI release tracking)
#
# This package MUST have its own updater. The generic release scanner in
# .github/workflows/update-engine.yml only rewrites "Version:" - it does not
# reset Release and does not add a %changelog entry. Packages with an
# update.sh are skipped by that scanner.

SPEC_FILE="python-pydbus.spec"
PYPI_NAME="pydbus"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking PyPI for $PYPI_NAME updates..."

LATEST_VERSION=$(python3 -c \
    "import json,urllib.request; print(json.load(urllib.request.urlopen('https://pypi.org/pypi/$PYPI_NAME/json',timeout=20))['info']['version'])" 2>/dev/null)

if [ -z "$LATEST_VERSION" ]; then
    echo "  -> [ERROR] Failed to fetch latest version from PyPI."
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
CHANGELOG_ENTRY="* $DATE $PACKAGER - $LATEST_VERSION-1\n- Auto-update to upstream PyPI release $LATEST_VERSION\n"
if grep -q '^%changelog' "$SPEC_FILE"; then
    sed -i "0,/^%changelog$/s//%changelog\n$CHANGELOG_ENTRY/" "$SPEC_FILE"
else
    printf '\n%%changelog\n%b' "$CHANGELOG_ENTRY" >> "$SPEC_FILE"
fi

echo "  -> [DONE] Successfully patched $SPEC_FILE."
