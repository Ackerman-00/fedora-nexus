%global commit          be548562464e1a6bd69bd3a64675822e83b97c5d
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260811125152

%global pyver           2.0.0


Name:           caelestia-cli-mango
Version:        %{pyver}^%{gitdate}git%{shortcommit}
Release:        2%{?dist}
Summary:        The main control script for the Caelestia dotfiles (MangoWM)

License:        GPL-3.0-only
URL:            https://github.com/Ackerman-00/caelestia-cli-mango
Source0:        %{url}/archive/%{commit}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-hatchling
BuildRequires:  python3-pip

Requires:       mangowm
Requires:       caelestia-shell-mango >= 2.0.0
Requires:       libnotify
Requires:       glib2
Requires:       dbus-tools
Requires:       swappy
Requires:       grim
Requires:       slurp
Requires:       wl-clipboard
Requires:       cliphist
Requires:       fuzzel
Requires:       app2unit
Requires:       gpu-screen-recorder
Requires:       procps-ng
Requires:       psmisc
Requires:       dconf
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
* Wed Aug 12 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.0^20260811125152gitbe54856-2
- Require dbus-tools: subcommands/record.py invokes dbus-send to reveal
  files in the file manager (org.freedesktop.FileManager1)

* Tue Aug 11 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.0^20260811125152gitbe54856-1
- Nightly sync with upstream main branch (Commit: be54856)
