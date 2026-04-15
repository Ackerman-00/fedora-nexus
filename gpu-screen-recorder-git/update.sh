#!/bin/bash
# 1. Scrape the log page and strictly extract the real commit hash (ignoring trees/blobs)
latest_commit=$(curl -s "https://git.dec05eba.com/gpu-screen-recorder/log/" | grep -oE 'id=[a-f0-9]{40}' | head -n 1 | cut -d'=' -f2)

# 2. Generate an RPM-safe version string from today's date
latest_date=$(date +%Y%m%d)

if [ -z "$latest_commit" ]; then
    echo "GSR-GIT: Error - Could not scrape commit from dec05eba.com"
    exit 1
fi

current_commit=$(grep "%global commit" gpu-screen-recorder-git.spec | awk '{print $3}')

# 4. If a new commit exists, update the spec
if [ "$latest_commit" != "$current_commit" ]; then
    echo "GSR-GIT: New commit found: $latest_commit"
    sed -i "s/%global commit.*/%global commit          $latest_commit/" gpu-screen-recorder-git.spec
    sed -i "s/^Version:.*/Version:        $latest_date/" gpu-screen-recorder-git.spec
    echo "GSR-GIT: Updated spec to $latest_date snapshot"
else
    echo "GSR-GIT: Already on latest snapshot ($latest_commit)"
fi
