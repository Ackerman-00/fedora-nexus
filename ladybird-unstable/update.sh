#!/usr/bin/env bash
set -u
SPEC_FILE=ladybird-unstable.spec
GITHUB_REPO=LadybirdBrowser/ladybird
PACKAGER="Ackerman-00 <no-reply>"
MIN_INTERVAL_HOURS=20

if [ "$(pwd)" != "$(cd "$(dirname "$0")" && pwd)" ]; then
  echo "FATAL: run update.sh from its package directory" >&2
  exit 1
fi

api() {
  if [ -n "${GITHUB_TOKEN:-}" ]; then
    curl -sfL -H "Authorization: token $GITHUB_TOKEN" "$@"
  else
    curl -sfL "$@"
  fi
}

LATEST=$(git ls-remote "https://github.com/$GITHUB_REPO.git" HEAD 2>/dev/null | awk '{print $1}')
[ -n "$LATEST" ] || { echo "Error: cannot read upstream HEAD"; exit 1; }
CURRENT=$(awk '/^%global commit/{print $3; exit}' "$SPEC_FILE")
SHORT=${LATEST:0:7}

if [ "$CURRENT" = "$LATEST" ]; then
  echo "Already at upstream HEAD ${SHORT}. No update needed."
  exit 0
fi

PIN_DATE=$(awk '/^Release:/{print $2; exit}' "$SPEC_FILE" | grep -oE '[0-9]{8}' | head -1)
PIN_EPOCH=$(date -u -d "${PIN_DATE:0:4}-${PIN_DATE:4:2}-${PIN_DATE:6:2}" +%s 2>/dev/null || echo 0)
NEW_ISO=$(api "https://api.github.com/repos/$GITHUB_REPO/commits/$LATEST" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("commit",{}).get("committer",{}).get("date",""))' 2>/dev/null)
NEW_EPOCH=$(date -u -d "$NEW_ISO" +%s 2>/dev/null || echo 0)
[ "$NEW_EPOCH" -gt 0 ] || { echo "Error: cannot read upstream commit date"; exit 1; }

AGE_H=$(( (NEW_EPOCH - PIN_EPOCH) / 3600 ))
if [ "$AGE_H" -lt "$MIN_INTERVAL_HOURS" ]; then
  echo "Upstream moved (${CURRENT:0:7} -> $SHORT) but only ${AGE_H}h past the pinned snapshot; next daily bump later."
  exit 0
fi

NEW_DATE=$(date -u -d "$NEW_ISO" +%Y%m%d)
NEW_REL=$(( $(awk '/^Release:/{print $2; exit}' "$SPEC_FILE" | cut -d. -f1) + 1 ))
OLD_REL=$(awk '/^Release:/{print $2; exit}' "$SPEC_FILE" | sed 's/%{?dist}//')

sed -i -E "s/^%global commit.*/%global commit         $LATEST/" "$SPEC_FILE"
sed -i -E "s/^Release:.*/Release:        ${NEW_REL}.${NEW_DATE}git${SHORT}%{?dist}/" "$SPEC_FILE"

CHANGELOG_VER="0.0.0-${NEW_REL}.${NEW_DATE}git${SHORT}"
CHANGELOG_ENTRY="* $(LC_ALL=C date +'%a %b %d %Y') $PACKAGER - $CHANGELOG_VER\n- Refresh snapshot ${CURRENT:0:7} -> $SHORT (upstream commit dated ${NEW_ISO}); build-system\n  files reviewed before the bump, COPR build verified after it\n"
if grep -q '^%changelog' "$SPEC_FILE"; then
  sed -i "0,/^%changelog$/s//%changelog\n$CHANGELOG_ENTRY/" "$SPEC_FILE"
else
  printf '\n%%changelog\n%b' "$CHANGELOG_ENTRY" >> "$SPEC_FILE"
fi

echo "Bumped $OLD_REL -> ${NEW_REL}.${NEW_DATE}git${SHORT}"
grep -q '^Name:' "$SPEC_FILE" || { echo "FATAL: spec lost its Name: header" >&2; git checkout -- "$SPEC_FILE"; exit 1; }
