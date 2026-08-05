%global commit          3dcbce715ae8b93107fa8632db15bf976862a573
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260630092427

Name:           hyprland-contrib
Version:        0.1^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
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

%description -n grimblast
%{summary}.

%files -n grimblast
%{_bindir}/grimblast
%{_mandir}/man1/grimblast.1.*

%package -n hyprprop
Summary:        An xprop replacement for hyprland
Requires:       slurp jq

%description -n hyprprop
%{summary}.

%files -n hyprprop
%{_bindir}/hyprprop
%{_mandir}/man1/hyprprop.1.*

%package -n scratchpad
Summary:        Send focused window to a special workspace named scratchpad
Requires:       jq
Recommends:     /usr/bin/notify-send

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

%description -n try_swap_workspace
%{summary}.

%files -n try_swap_workspace
%{_bindir}/try_swap_workspace

%package -n hdrop
Summary:        Emulates the main feature of tdrop in Hyprland
Requires:       jq
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
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1^20260630092400git3dcb981-1
- Initial packaging for Fedora Nexus (Nexus Optimized)