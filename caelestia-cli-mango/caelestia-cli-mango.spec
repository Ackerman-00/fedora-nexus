# These will be automatically populated by update.sh
%global commit          5c443b504b355dfe16c015144b60d96e4074413c
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260808212545

# NOTE: This package is for MangoWM only. It will NOT work with
# Hyprland setups (no Hyprland IPC coupling; uses mmsg).

Name:           caelestia-cli-mango
Version:        2.0.0
Release:        3%{?dist}
Summary:        The main control script for the Caelestia dotfiles (MangoWM)

License:        GPL-3.0-only
URL:            https://github.com/Ackerman-00/caelestia-cli-mango
Source0:        %{url}/archive/%{commit}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-hatchling
BuildRequires:  python3-pip

# === RUNTIME DEPENDENCIES ===
# Compositor (MangoWM only!)
Requires:       mangowm
# Shell (caelestia-shell IPC for picker/shell/emojis)
Requires:       caelestia-shell-mango >= 2.0.0
# Notifications
Requires:       libnotify
Requires:       glib2
# Screenshots
Requires:       swappy
Requires:       grim
Requires:       slurp
# Clipboard
Requires:       wl-clipboard
# cliphist is only packaged in Fedora >= 44; keep F43 installable (clipboard
# history is a helper feature - hard-failing the install on F43 is worse)
Requires:       (cliphist if fedora-release >= 44)
Requires:       fuzzel
# Launcher
Requires:       app2unit
# Screen recording
Requires:       gpu-screen-recorder
# Theme/process helpers
Requires:       procps-ng
Requires:       psmisc
Requires:       dconf
# Python deps
Requires:       python3-pillow
Requires:       python3-materialyoucolor

%description
The main control script for the Caelestia dotfiles, ported to MangoWM
(uses mmsg IPC instead of Hyprland sockets). Provides colour scheme &
wallpaper management, screenshots, recordings, clipboard history, emoji
picking, and shell control.

Tracks the main branch of https://github.com/Ackerman-00/caelestia-cli-mango.

%prep
%autosetup -n caelestia-cli-mango-%{commit}

%build
# Replace qs config call with system shell wrapper (mirrors nix patchPhase)
sed -i 's/"qs", "-c", "caelestia"/"caelestia-shell"/' src/caelestia/subcommands/shell.py
sed -i 's/"qs", "-c", "caelestia", "ipc"/"caelestia-shell", "ipc"/' src/caelestia/subcommands/screenshot.py
sed -i 's/\["todoist"\]/["todoist.desktop"]/' src/caelestia/subcommands/toggle.py

%pyproject_wheel

%install
%pyproject_install
install -Dpm 0644 completions/caelestia.fish %{buildroot}%{_datadir}/fish/vendor_completions.d/caelestia.fish

%files
%{_bindir}/caelestia
%{python3_sitelib}/caelestia/
%{python3_sitelib}/caelestia-%{version}.dist-info/
%{_datadir}/fish/vendor_completions.d/caelestia.fish
%doc README.md
%license LICENSE

%changelog
* Sat Aug 08 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.0-3
- Make cliphist a conditional requirement (cliphist only exists in Fedora >= 44;
  without this the package is uninstallable on Fedora 43)

* Sat Aug 08 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.0-2
- Add BuildRequires: python3-pip (COPR %pyproject_wheel failed: no pip module in buildroot)

* Sat Aug 08 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.0-1
- Initial package (commit 5c443b5): MangoWM port of caelestia CLI.
  Requires python3-materialyoucolor for scheme generation.