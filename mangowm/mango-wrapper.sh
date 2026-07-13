#!/bin/sh
# Mango WM wrapper — imports Wayland env into systemd and activates session target
systemctl --user import-environment WAYLAND_DISPLAY DISPLAY XDG_CURRENT_DESKTOP
systemctl --user start mango-session.service
exec /usr/bin/mango.real "$@"
