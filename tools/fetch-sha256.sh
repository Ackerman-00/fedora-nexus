#!/bin/bash
set -u
url=${1:?usage: fetch-sha256.sh <url> [curl args...]}
shift
tmp=$(mktemp) || exit 1
trap 'rm -f "$tmp"' EXIT
curl -fsSL --retry 3 --retry-all-errors --max-time 1800 "$@" -o "$tmp" "$url" || exit 1
sha256sum "$tmp" | awk '{print $1}'
