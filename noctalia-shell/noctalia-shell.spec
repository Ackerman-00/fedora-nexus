%global tag         v4.7.6
%global forgeurl    https://github.com/noctalia-dev/noctalia-shell
%forgemeta

# Disable debuginfo extraction since this package contains no compiled binaries
%global debug_package %{nil}

Name:           noctalia-shell
Version:        %{fileref}
Release:        %autorelease
Summary:        A sleek and minimal desktop shell thoughtfully crafted for Wayland

License:        MIT
URL:            %{forgeurl}
Source0:        %{forgesource}

# Architecture independent (pure scripts/QML)
BuildArch:      noarch

Requires:       noctalia-qs
Requires:       qt6-qtmultimedia
Requires:       qt6-qtwayland
Requires:       qt6-qtsvg
Requires:       qt6-qt5compat
Requires:       wl-clipboard
Requires:       playerctl
Requires:       libnotify
Requires:       brightnessctl
Requires:       upower
Requires:       power-profiles-daemon
Requires:       google-roboto-fonts
Requires:       xdg-desktop-portal

Recommends:     cliphist
Recommends:     ddcutil
Recommends:     matugen
Recommends:     cava
Recommends:     gpu-screen-recorder

%description
A beautiful, minimal desktop shell for Wayland that actually gets out of your way. 
Built on Quickshell. 

To use it, copy the config to your user directory:
mkdir -p ~/.config/quickshell && cp -r /usr/share/noctalia-shell/* ~/.config/quickshell/

%prep
%forgeautosetup -p1

%build
# No compilation required for shell configs

%install
rm -rf %{buildroot}

# Install globally into standard xdg system path
install -d -m 0755 %{buildroot}%{_sysconfdir}/xdg/quickshell/noctalia-shell
cp -r * %{buildroot}%{_sysconfdir}/xdg/quickshell/noctalia-shell/

# Provide it in /usr/share per standard packaging guidelines
install -d -m 0755 %{buildroot}%{_datadir}/noctalia-shell
cp -r * %{buildroot}%{_datadir}/noctalia-shell/

%files
%doc README.md
%license LICENSE
%{_sysconfdir}/xdg/quickshell/noctalia-shell/
%{_datadir}/noctalia-shell/

%changelog
%autochangelog
