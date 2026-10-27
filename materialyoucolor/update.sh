#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="python3-materialyoucolor.spec"
PYPI_NAME="materialyoucolor"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking PyPI for $PYPI_NAME updates..."

META=$(python3 - "$PYPI_NAME" <<'PY'
import json, sys, urllib.request

name = sys.argv[1]
data = json.load(urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json", timeout=20))
sdist = next((u for u in data["urls"] if u["packagetype"] == "sdist"), None)
if sdist is None:
    raise SystemExit("no sdist on PyPI")
print(data["info"]["version"])
print(sdist["url"])
print(sdist["digests"]["sha256"])
PY
) || { echo "  -> [ERROR] Failed to read PyPI metadata."; exit 1; }

{ read -r LATEST_VERSION; read -r SDIST_URL; read -r SDIST_SHA256; } <<< "$META"

if [ -z "$LATEST_VERSION" ] || [ -z "$SDIST_URL" ]; then
    echo "  -> [ERROR] Failed to fetch latest version from PyPI."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$LATEST_VERSION" = "$CURRENT_VERSION" ]; then
    echo "  -> [OK] Package is already at $CURRENT_VERSION. No update needed."
    exit 0
fi

echo "  -> [UPDATE] $CURRENT_VERSION -> $LATEST_VERSION"

TMP=$(mktemp)
if ! curl -fsSL -o "$TMP" "$SDIST_URL"; then
    echo "  -> [ERROR] sdist download failed: $SDIST_URL"
    rm -f "$TMP"
    exit 1
fi
GOT_SHA256=$(sha256sum "$TMP" | awk '{print $1}')
rm -f "$TMP"
if [ "$GOT_SHA256" != "$SDIST_SHA256" ]; then
    echo "  -> [ERROR] sha256 mismatch: PyPI says $SDIST_SHA256, download is $GOT_SHA256"
    exit 1
fi

python3 - "$SPEC_FILE" "$LATEST_VERSION" "$SDIST_URL" "$SDIST_SHA256" "$PACKAGER" <<'PY'
import datetime, sys

spec, version, url, sha, packager = sys.argv[1:6]
text = open(spec, encoding="utf-8").read()
lines = text.splitlines()
out = []
for line in lines:
    if line.startswith("Version:"):
        out.append(f"Version:        {version}")
    elif line.startswith("Release:"):
        out.append("Release:        1%{?dist}")
    elif line.startswith("Source0:"):
        out.append(f"# sha256: {sha}")
        out.append(f"Source0:        {url}")
    else:
        out.append(line)
text = "\n".join(out) + "\n"
date = datetime.datetime.now(datetime.timezone.utc).strftime("%a %b %d %Y")
entry = (f"* {date} {packager} - {version}-1\n"
         f"- Auto-update to upstream PyPI release {version}\n")
if "%changelog" in text:
    text = text[:text.index("%changelog")] + "%changelog\n" + entry
else:
    text = text.rstrip("\n") + "\n\n%changelog\n" + entry
open(spec, "w", encoding="utf-8").write(text)
PY

if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi

echo "  -> [DONE] Successfully patched $SPEC_FILE."
