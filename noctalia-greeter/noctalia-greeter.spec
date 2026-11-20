%global commit          2726e75375d95d5458d021f76c330ab14f6a5d03
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261120141153

Name:           noctalia-greeter
Version:        1.7.1^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Login greeter for greetd with the Noctalia Shell look and feel

License:        MIT AND Apache-2.0
URL:            https://github.com/noctalia-dev/noctalia-greeter
Source0:        %{url}/archive/%{commit}/%{name}-%{commit}.tar.gz
# sha256: d42775b045a373c610f1fa06ea4eded68d4096d446dfe87ab4b6ce0836c5823d
Source1:        https://raw.githubusercontent.com/google/wuffs/a14745aa458fd2b2785034efa04eab3c7b5b91e0/LICENSE-APACHE
# sha256: 0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594
Source2:        https://raw.githubusercontent.com/google/wuffs/a14745aa458fd2b2785034efa04eab3c7b5b91e0/LICENSE-MIT
# sha256: bb811a4b485eac3caeb8bdc58bbafb355fbcb6116010a7ea9179e5c70b0bc878

BuildRequires:  meson
BuildRequires:  gcc-c++
BuildRequires:  diffutils
BuildRequires:  stb_image_resize2-devel
BuildRequires:  libinput-devel
BuildRequires:  pkgconfig(wlroots-0.20) >= 0.20.2
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(glesv2)
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
BuildRequires:  systemd-rpm-macros

Requires:       dbus
# polkit: optional in upstream PACKAGING.md, the shipped .policy is inert without polkitd
Recommends:     polkit
Requires:       /usr/bin/bash
Requires:       /usr/bin/dbus-run-session
Requires:       greetd
Requires:       wlroots >= 0.20.2

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

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true
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
# Fresh-install auto-setup
if [ "$1" -eq 1 ]; then
    # PAM seat patch
    if [ ! -f /etc/pam.d/greetd ] && [ -f /usr/lib/pam.d/greetd ]; then
        cp /usr/lib/pam.d/greetd /etc/pam.d/greetd 2>/dev/null || :
    fi
    SETUP=/usr/share/noctalia-greeter/setup_greeter_system.sh
    if [ -x "$SETUP" ] && command -v systemctl >/dev/null 2>&1; then
        "${SETUP}" >/dev/null 2>&1 || :
    fi

    # greetd config + backup
    greeter_user=$(awk -F= '/^[[:space:]]*user[[:space:]]*=/{gsub(/["[:space:]]/,"",$2); u=$2} END{print (u?u:"greetd")}' /etc/greetd/config.toml 2>/dev/null || echo greetd)
    [ -n "$greeter_user" ] || greeter_user=greetd
    if [ -f /etc/greetd/config.toml ] &&
       ! grep -q 'noctalia-greeter-session' /etc/greetd/config.toml 2>/dev/null; then
        cp -a /etc/greetd/config.toml /etc/greetd/config.toml.bak.noctalia.$(date +%%Y%%m%%d%%H%%M%%S) 2>/dev/null || :
        cat > /etc/greetd/config.toml <<EOF
[terminal]
vt = 1

[default_session]
command = "/usr/bin/noctalia-greeter-session"
user = "$greeter_user"
EOF
    fi

    # VT1 kmscon -> greetd, VT2 text console
    systemctl disable kmsconvt@tty1.service >/dev/null 2>&1 || :
    systemctl enable getty@tty2.service >/dev/null 2>&1 || :
    systemctl enable greetd.service >/dev/null 2>&1 || :
    if [ ! -e /etc/systemd/system/display-manager.service ]; then
        ln -s /usr/lib/systemd/system/greetd.service /etc/systemd/system/display-manager.service 2>/dev/null || :
    fi
fi

%postun
# On final removal, undo the display-manager alias if it still points here.
if [ "$1" -eq 0 ] && [ -L /etc/systemd/system/display-manager.service ]; then
    target=$(readlink /etc/systemd/system/display-manager.service 2>/dev/null || :)
    case "$target" in *greetd.service*) rm -f /etc/systemd/system/display-manager.service ;; esac
fi

%changelog
* Fri Nov 20 2026 Ackerman-00 <no-reply> - 1.7.1^20261120141153git2726e75-1
- Nightly sync with upstream main branch (Commit: 2726e75)
