#!/bin/sh
# Mango WM wrapper — unset stale TTY display vars, activate session target, exec
unset WAYLAND_DISPLAY
unset DISPLAY
systemctl --user start mango-session.service
exec /usr/bin/mango.real "$@"
