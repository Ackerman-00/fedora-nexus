# These will be automatically populated by update.sh
%global commit          6379fe287bb02b0bb538ad155fe18b1bf8615daf
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260902080638

Name:           noctalia-greeter
Version:        1.3.1^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        A minimal login greeter for greetd that matches the look and feel of Noctalia Shell

License:        MIT
URL:            https://github.com/noctalia-dev/noctalia-greeter
Source0:        %{url}/archive/%{commit}/%{name}-%{commit}.tar.gz

BuildRequires:  meson
BuildRequires:  gcc-c++
BuildRequires:  just
BuildRequires:  greetd
BuildRequires:  dbus
BuildRequires:  polkit
BuildRequires:  json-devel
BuildRequires:  tomlplusplus-devel
BuildRequires:  stb_image_resize2-devel
BuildRequires:  libwebp-devel
BuildRequires:  librsvg2-devel
BuildRequires:  libinput-devel
BuildRequires:  wlroots-devel >= 0.20
BuildRequires:  libEGL-devel
BuildRequires:  mesa-libGLES-devel
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(librsvg-2.0)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(xkbcommon)

Requires:       dbus
Requires:       greetd
Requires:       wlroots >= 0.20

%description
A minimal login greeter for greetd that matches the look and feel of Noctalia
Shell, built with wlroots. Compiled specifically for the Nexus repository via
automated Git snapshot.

%prep
%autosetup -n %{name}-%{commit}

%build
%meson -Db_pie=true
%meson_build

%install
%meson_install
# Delete the unneeded tmpfiles.d fallback configuration
rm -f %{buildroot}%{_tmpfilesdir}/noctalia-greeter.conf
install -d %{buildroot}%{_licensedir}/%{name}/third_party
find third_party -type f \( -name "LICENSE*" -o -name "COPYING*" -o -name "NOTICE*" \) | while read -r file; do
    dest_dir="%{buildroot}%{_licensedir}/%{name}/$(dirname "$file")"
    install -d "$dest_dir"
    install -p -m 0644 "$file" "$dest_dir/"
done

%files
%doc README.md
%license LICENSE
%{_licensedir}/%{name}/third_party/
%{_bindir}/%{name}
%{_bindir}/%{name}-apply-appearance
%{_bindir}/%{name}-compositor
%{_bindir}/%{name}-print-greetd-config
%{_bindir}/%{name}-session
%{_datadir}/%{name}/*
%{_datadir}/polkit-1/actions/org.noctalia.greeter.apply-appearance.policy

%post
# One-time enable instructions on fresh installs (not on upgrades)
if [ "$1" -eq 1 ]; then
    echo
    echo "================================================================"
    echo "  noctalia-greeter is installed but NOT enabled yet."
    echo
    echo "  1. Run the system setup script (PAM patch, state dir, config):"
    echo "    sudo /usr/share/noctalia-greeter/setup_greeter_system.sh"
    echo
    echo "  2. Point greetd at the greeter - /etc/greetd/config.toml:"
    echo "    [default_session]"
    echo "    command = \"/usr/bin/noctalia-greeter-session\""
    echo "    user = \"greetd\""
    echo
    echo "  3. Enable and start it:"
    echo "    sudo systemctl enable --now greetd"
    echo
    echo "  Tip: user avatars on the login screen need accountsservice:"
    echo "    sudo dnf install accountsservice"
    echo "================================================================"
fi

%changelog
* Wed Sep 02 2026 Ackerman-00 <quietcraft@gmail.com> - 1.3.1^20260902080638git6379fe2-1
- Nightly sync with upstream main branch (Commit: 6379fe2)
