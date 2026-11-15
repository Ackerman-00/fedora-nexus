#!/usr/bin/env bash
set -u
PKG_DIR=$(cd "$(dirname "$0")" && pwd) || exit 1
[ "$(pwd)" = "$PKG_DIR" ] || { echo "FATAL: run update.sh from its package directory: cd $PKG_DIR && bash update.sh" >&2; exit 1; }

SPEC_FILE=hatter-icon-theme.spec
PACKAGER="Ackerman-00 <no-reply>"
REPO=Mibea/Hatter

api() {
  if [ -n "${GITHUB_TOKEN:-}" ]; then
    curl -sfL -H "Authorization: token $GITHUB_TOKEN" "$@"
  else
    curl -sfL "$@"
  fi
}

TAG=$(api "https://api.github.com/repos/$REPO/releases/latest" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin).get("tag_name",""))')
[ -n "$TAG" ] || { echo "Error: cannot read the latest upstream release tag" >&2; exit 1; }
VERSION=${TAG#V}
CURRENT=$(awk '/^Version:/{print $2; exit}' "$SPEC_FILE")

if [ "$CURRENT" = "$VERSION" ]; then
  echo "Package is already at $VERSION. No update needed."
  exit 0
fi

echo "Update available: $CURRENT -> $VERSION ($TAG)"
URL="https://github.com/$REPO/archive/refs/tags/$TAG.tar.gz"
SHA256=$(bash "$PKG_DIR/../tools/fetch-sha256.sh" "$URL" --http1.1) || {
  echo "Error: could not download $URL for hashing." >&2
  exit 1
}

sed -i "s/^Version:.*/Version:        $VERSION/" "$SPEC_FILE"
sed -i "s|^Source0:.*|Source0:        $URL|" "$SPEC_FILE"
sed -i "s|^%setup -q -n Hatter-.*|%setup -q -n Hatter-$VERSION|" "$SPEC_FILE"
sed -i -E "s/Hatter icon theme \(V[0-9.]+ release\)/Hatter icon theme (V$VERSION release)/" "$SPEC_FILE"
sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
if grep -q "^# sha256:" "$SPEC_FILE"; then
  sed -i -E "s|^# sha256:.*|# sha256: $SHA256|" "$SPEC_FILE"
else
  sed -i "/^Source0:/a # sha256: $SHA256" "$SPEC_FILE"
fi

DATE=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
  echo "%changelog"
  echo "* $DATE $PACKAGER - $VERSION-1"
  echo "- Update to $TAG"
} >> "$SPEC_FILE"

grep -q '^Name:' "$SPEC_FILE" || { echo "FATAL: spec lost its Name: header" >&2; exit 1; }
echo "Successfully updated to $VERSION."
echo "Rework check: upstream build script is ./build.sh --all --dest <dir> (verify %build/%install still match)."
