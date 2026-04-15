#!/bin/bash
# Scrape the official snapshot directory for the highest version number
latest_ver=$(curl -s "https://dec05eba.com/snapshot/" | grep -oE 'gpu-screen-recorder\.git\.[0-9]+(\.[0-9]+)*\.tar\.gz' | grep -oE '[0-9]+(\.[0-9]+)*' | sort -V | tail -n 1)

if [ -z "$latest_ver" ]; then
    echo "GSR: Error - Could not scrape version from dec05eba.com/snapshot/"
    exit 1
fi

current_ver=$(grep "^Version:" gpu-screen-recorder.spec | awk '{print $2}')

if [ "$latest_ver" != "$current_ver" ]; then
    echo "GSR: Updating from $current_ver to $latest_ver"
    sed -i "s/^Version:.*/Version:        $latest_ver/" gpu-screen-recorder.spec
else
    echo "GSR: Already on latest ($latest_ver)"
fi
