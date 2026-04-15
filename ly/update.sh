#!/bin/bash

# Scrape the latest stable release tag from the Codeberg API
latest_ver=$(curl -s "https://codeberg.org/api/v1/repos/fairyglade/ly/releases" | jq -r '..tag_name' | sed 's/^v//')

if [ -z "$latest_ver" ] || [ "$latest_ver" == "null" ]; then
    echo "LY: Error - Could not scrape version from Codeberg API"
    exit 1
fi

current_ver=$(grep "^Version:" ly.spec | awk '{print $2}')

if [ "$latest_ver" != "$current_ver" ]; then
    echo "LY: Updating from $current_ver to $latest_ver"
    sed -i "s/^Version:.*/Version:        $latest_ver/" ly.spec
else
    echo "LY: Already on latest stable ($latest_ver)"
fi
