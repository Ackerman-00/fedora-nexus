%global commit          dbace1c834a9e0f2e1b5d4ef186db8ec3b422a49
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261025021409

Name:           noctalia-greeter
Version:        1.7.0^%{gitdate}git%{shortcommit}
Release:        2%{?dist}
Summary:        Login greeter for greetd with the Noctalia Shell look and feel

License:        MIT AND Apache-2.0
URL:            https://github.com/noctalia-dev/noctalia-greeter
Source0:        %{url}/archive/%{commit}/%{name}-%{commit}.tar.gz
# sha256: 3fae5d0c4ec5043a60c4e66ed13d8dad6ea32340fee9c3ba2321288ab48e1cd4
Source1:        https://raw.githubusercontent.com/google/wuffs/a14745aa458fd2b2785034efa04eab3c7b5b91e0/LICENSE-APACHE
# sha256: 0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594
Source2:        https://raw.githubusercontent.com/google/wuffs/a14745aa458fd2b2785034efa04eab3c7b5b91e0/LICENSE-MIT
# sha256: bb811a4b485eac3caeb8bdc58bbafb355fbcb6116010a7ea9179e5c70b0bc878

BuildRequires:  meson
BuildRequires:  gcc-c++
BuildRequires:  greetd
BuildRequires:  dbus
BuildRequires:  polkit
BuildRequires:  diffutils
BuildRequires:  stb_image_resize2-devel
BuildRequires:  libinput-devel
BuildRequires:  pkgconfig(wlroots-0.20) >= 0.20
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  mesa-libGLES-devel
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(cairo-ft)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  pkgconfig(librsvg-2.0)
BuildRequires:  pkgconfig(libjxl)
BuildRequires:  pkgconfig(libjxl_threads)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pangoft2)
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(xkbcommon)

Requires:       dbus
Requires:       /usr/bin/dbus-run-session
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
rm -f %{buildroot}%{_tmpfilesdir}/noctalia-greeter.conf
install -d %{buildroot}%{_licensedir}/%{name}/third_party
install -d %{buildroot}%{_licensedir}/%{name}/third_party/wuffs
install -p -m 0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/third_party/wuffs/LICENSE-APACHE
install -p -m 0644 %{SOURCE2} %{buildroot}%{_licensedir}/%{name}/third_party/wuffs/LICENSE-MIT
find third_party -type f \( -name "LICENSE*" -o -name "COPYING*" -o -name "NOTICE*" \) | while read -r file; do
    dest_dir="%{buildroot}%{_licensedir}/%{name}/$(dirname "$file")"
    install -d "$dest_dir"
    install -p -m 0644 "$file" "$dest_dir/"
done

%check
%meson_test

%files
%doc README.md
%license LICENSE
%{_licensedir}/%{name}/third_party/
%{_bindir}/%{name}
%{_bindir}/%{name}-apply-appearance
%{_bindir}/%{name}-compositor
%{_bindir}/%{name}-print-greetd-config
%{_bindir}/%{name}-session
%{_bindir}/%{name}-xsession
%{_datadir}/%{name}/*
%{_datadir}/polkit-1/actions/org.noctalia.greeter.apply-appearance.policy

%post
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
* Sun Oct 25 2026 Ackerman-00 <quietcraft@gmail.com> - 1.7.0^20261025021409gitdbace1c-2
- Declare diffutils for the %check test that calls cmp
- Require the dbus-run-session provider the session script execs

* Sun Oct 25 2026 Ackerman-00 <quietcraft@gmail.com> - 1.7.0^20261025021409gitdbace1c-1
- Nightly sync with upstream main branch (Commit: dbace1c)
