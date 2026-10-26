#!/bin/bash
# fetch-sha256.sh <url> [curl args...] - sha256 of a COMPLETE download.
# A truncated transfer hashes cleanly and would pin a wrong artifact, so the
# transfer's exit status is the verdict, never the presence of output.
set -u
url=${1:?usage: fetch-sha256.sh <url> [curl args...]}
shift
tmp=$(mktemp) || exit 1
trap 'rm -f "$tmp"' EXIT
curl -fsSL --retry 3 --retry-all-errors --max-time 1800 "$@" -o "$tmp" "$url" || exit 1
sha256sum "$tmp" | awk '{print $1}'
