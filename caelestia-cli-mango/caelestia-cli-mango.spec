# These will be automatically populated by update.sh
%global commit          be548562464e1a6bd69bd3a64675822e83b97c5d
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260811125152

# Upstream has no releases/tags; it is tracked by commit. The python project
# version (pyproject.toml) stays 2.0.0, so the .dist-info directory is named
# after %%{pyver}, NOT the rpm %%{version} (which carries the ^gitdate suffix).
%global pyver           2.0.0

# NOTE: This package is for MangoWM only. It will NOT work with
# Hyprland setups (no Hyprland IPC coupling; uses mmsg).

Name:           caelestia-cli-mango
Version:        %{pyver}^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
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
# cliphist is missing from Fedora 43, but this repo now ships it for every
# supported release, so it can be required unconditionally again.
Requires:       cliphist
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
%{python3_sitelib}/caelestia-%{pyver}.dist-info/
%{_datadir}/fish/vendor_completions.d/caelestia.fish
%doc README.md
%license LICENSE

%changelog
* Tue Aug 11 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.0^20260811125152gitbe54856-1
- Nightly sync with upstream main branch (Commit: be54856)
