#!/bin/sh
# Mango WM wrapper — clean env, activate session target, exec with argv[0]=mango
unset WAYLAND_DISPLAY
unset DISPLAY
export XDG_CURRENT_DESKTOP=mango
export XDG_SESSION_TYPE=wayland
systemctl --user start mango-session.service
exec -a mango /usr/bin/mango.real "$@"
