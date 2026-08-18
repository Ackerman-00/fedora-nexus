#!/bin/bash

SPEC_FILE="protonplus.spec"
GITHUB_REPO="vysp3r/ProtonPlus"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# This package derives Version from the forge tag (%forgemeta -> %{fileref}), so the
# tag MUST be a plain dotted version. Upstream sometimes publishes re-roll tags such
# as "v0.6.1-1"; a dash is an illegal character in an RPM Version and makes the spec
# unparsable ("Illegal char '-' (0x2d) in: Version"). Only accept v<digits.dots>.
LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null \
    | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' \
    | grep -E '^v[0-9]+(\.[0-9]+)*$' \
    | sort -V | tail -1)

if [ -z "$LATEST_TAG" ]; then
    echo "Error: Failed to fetch a usable upstream tag."
    exit 1
fi

LATEST_VERSION=${LATEST_TAG#v}
CURRENT_TAG=$(grep -E "^%global tag" "$SPEC_FILE" | awk '{print $3}')

if [ "$CURRENT_TAG" == "$LATEST_TAG" ]; then
    echo "Package is already at $LATEST_TAG. No update needed."
    exit 0
fi

echo "Update found: $CURRENT_TAG -> $LATEST_TAG"

# Make sure the archive really exists before bumping onto it
if ! curl -sIL -o /dev/null --fail \
        "https://github.com/$GITHUB_REPO/archive/$LATEST_TAG/ProtonPlus-$LATEST_VERSION.tar.gz"; then
    echo "Error: source archive for $LATEST_TAG is not downloadable. Aborting."
    exit 1
fi

sed -i -E "s|^%global tag .*|%global tag         $LATEST_TAG|" "$SPEC_FILE"
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

DATE_STRING=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE_STRING $PACKAGER - $LATEST_VERSION-1"
    echo "- Update to version $LATEST_VERSION"
} >> "$SPEC_FILE"

echo "Successfully patched $SPEC_FILE to $LATEST_TAG."
# Re-triggered rebuild for COPR SRPM-import outage on 2026-08-18 (spec unchanged).
