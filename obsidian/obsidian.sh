#!/bin/bash
OBSIDIAN_USER_FLAGS_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/obsidian/user-flags.conf"

# Allow users to override command-line options for Wayland/GPU acceleration
if [ -f "$OBSIDIAN_USER_FLAGS_FILE" ]; then
   mapfile -t OBSIDIAN_USER_FLAGS < <(sed -r "/^( *#|$)/d;s% %\n%g" "$OBSIDIAN_USER_FLAGS_FILE")
fi

# Find app launcher (Updated to look inside the resources folder we packaged)
for file in /usr/lib{64,}/obsidian/resources/app.asar; do
   [ -f "$file" ] && break
done

# Launch Obsidian via native Electron
exec electron "$file" "${OBSIDIAN_USER_FLAGS[@]}" "$@"
