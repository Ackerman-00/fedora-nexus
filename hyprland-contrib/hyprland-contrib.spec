%global commit          3dcbce715ae8b93107fa8632db15bf976862a573
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260630092427

Name:           hyprland-contrib
Version:        0.1^%{gitdate}git%{shortcommit}
Release:        3%{?dist}
Summary:        Community scripts and utilities for Hypr projects
BuildArch:      noarch
License:        MIT
URL:            https://github.com/hyprwm/contrib
Source0:        %{url}/archive/%{commit}/contrib-%{shortcommit}.tar.gz
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  make
BuildRequires:  scdoc

Recommends:     try_swap_workspace
Recommends:     shellevents
Recommends:     scratchpad
Recommends:     hyprprop
Recommends:     grimblast
Recommends:     hdrop

%description
%{summary}.

%package -n grimblast
Summary:        A helper for screenshots within hyprland
Requires:       grim slurp wl-clipboard jq /usr/bin/notify-send hyprpicker /usr/bin/gdbus
# killhyprpicker() uses pidof + pkill; hyprctl is used to query the active window
Requires:       procps-ng
Requires:       /usr/bin/hyprctl

%description -n grimblast
%{summary}.

%files -n grimblast
%{_bindir}/grimblast
%{_mandir}/man1/grimblast.1.*

%package -n hyprprop
Summary:        An xprop replacement for hyprland
Requires:       slurp jq
# upstream header documents hyprctl as a hard requirement
Requires:       /usr/bin/hyprctl

%description -n hyprprop
%{summary}.

%files -n hyprprop
%{_bindir}/hyprprop
%{_mandir}/man1/hyprprop.1.*

%package -n scratchpad
Summary:        Send focused window to a special workspace named scratchpad
Requires:       jq
# basicChecks() requires hyprctl and pgrep; the menu handling uses killall
Requires:       /usr/bin/hyprctl
Requires:       procps-ng
Requires:       psmisc
Recommends:     /usr/bin/notify-send
# scratchpad:8 hardcodes `rofi -dmenu -i -p scratchpad` as the default menu
# used by -g/-l to pick a window. It is overridable with -m, so this is a
# Recommends rather than a hard Requires.
Recommends:     rofi

%description -n scratchpad
%{summary}.

%files -n scratchpad
%{_bindir}/scratchpad

%package -n shellevents
Summary:        Invoke shell functions in response to hyprland socket2 events
Requires:       socat

%description -n shellevents
%{summary}.

%files -n shellevents
%{_bindir}/shellevents
%{_bindir}/shellevents_default.sh

%package -n try_swap_workspace
Summary:        Move arbitrary workspace to arbitrary monitor and swap workspaces
# parses hyprctl -j output with jq; basicChecks() uses hyprctl and pgrep -x
Requires:       jq
Requires:       /usr/bin/hyprctl
Requires:       procps-ng
Recommends:     /usr/bin/notify-send

%description -n try_swap_workspace
%{summary}.

%files -n try_swap_workspace
%{_bindir}/try_swap_workspace

%package -n hdrop
Summary:        Emulates the main feature of tdrop in Hyprland
Requires:       jq
# drives the compositor entirely through hyprctl (22 call sites)
Requires:       /usr/bin/hyprctl
Recommends:     /usr/bin/notify-send

%description -n hdrop
%{summary}.

%files -n hdrop
%{_bindir}/hdrop
%{_mandir}/man1/hdrop.1.*

%prep
%autosetup -n contrib-%{commit}

%install
for script in grimblast hyprprop scratchpad shellevents try_swap_workspace hdrop
do
pushd $script
%make_install DESTDIR=%{buildroot} PREFIX=%{buildroot}%{_prefix}
popd
done

%files
%license LICENSE
%doc README.md

%changelog
* Sat Aug 08 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1^20260630092427git3dcbce7-3
- scratchpad: add Recommends: rofi. scratchpad:8 hardcodes
  `_menu_cmd="rofi -dmenu -i -p scratchpad"`, which is what -g/-l pipe the
  client list into (scratchpad:128) and what -g kills first (scratchpad:101).
  Without rofi installed the window picker silently produces no selection.
  Recommends (not Requires) because -m overrides the menu program.

* Fri Aug 07 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1^20260630092427git3dcbce7-2
- Fix missing runtime dependencies of the contrib scripts (verified against
  upstream commit 3dcbce7):
  * grimblast: add procps-ng (killhyprpicker() uses `pidof -q hyprpicker &&
    pkill hyprpicker`, grimblast:27 - previously failed with
    "grimblast: line 27: pidof: command not found") and /usr/bin/hyprctl
  * hyprprop: add /usr/bin/hyprctl (documented as required in the script
    header, 5 call sites)
  * scratchpad: add /usr/bin/hyprctl, procps-ng (basicChecks() `pgrep
    Hyprland`, scratchpad:55) and psmisc (`killall` on the menu cmd,
    scratchpad:101)
  * try_swap_workspace: had NO Requires at all - add jq (parses `hyprctl -j`
    output), /usr/bin/hyprctl and procps-ng (`pgrep -x Hyprland`,
    try_swap_workspace:51) plus a notify-send Recommends
  * hdrop: add /usr/bin/hyprctl (22 call sites)
  hyprctl is expressed as a file dependency on /usr/bin/hyprctl (provided by
  hyprland) so it stays valid if the binary moves package.

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1^20260630092400git3dcb981-1
- Initial packaging for Fedora Nexus (Nexus Optimized)