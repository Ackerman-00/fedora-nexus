#!/bin/bash
# 1. latest commit hash
latest_commit=$(curl -s "https://git.dec05eba.com/gpu-screen-recorder/refs/" | grep -oE '[a-f0-9]{40}' | head -n 1)

# 2. Get today's date for versioning
latest_date=$(date +%Y%m%d)

if [ -z "$latest_commit" ]; then
    echo "GSR-GIT: Error - Could not scrape commit from git.dec05eba.com"
    exit 1
fi

# 3. Read the current commit from the .spec
current_commit=$(grep "%global commit" gpu-screen-recorder-git.spec | awk '{print $3}')

# 4. If upstream has a new commit, update the file
if [ "$latest_commit" != "$current_commit" ]; then
    echo "GSR-GIT: New commit found: $latest_commit"
    sed -i "s/%global commit.*/%global commit          $latest_commit/" gpu-screen-recorder-git.spec
    sed -i "s/^Version:.*/Version:        $latest_date/" gpu-screen-recorder-git.spec
    echo "GSR-GIT: Updated to $latest_date snapshot"
else
    echo "GSR-GIT: Already on latest commit ($current_commit)"
fi
