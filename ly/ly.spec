%global zig_ver 0.15.2

%ifarch x86_64
%global zig_arch x86_64
%endif
%ifarch aarch64
%global zig_arch aarch64
%endif

Name:           ly
Version:        1.3.2
Release:        4%{?dist}
Summary:        A lightweight TUI (ncurses-like) display manager (Nexus Universal)

License:        WTFPL
URL:            https://codeberg.org/fairyglade/ly
Source0:        https://codeberg.org/fairyglade/ly/archive/v%{version}.tar.gz
Source1:        ly.pam

Source2:        https://ziglang.org/download/%{zig_ver}/zig-%{zig_arch}-linux-%{zig_ver}.tar.xz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  kernel-devel
BuildRequires:  pam-devel
BuildRequires:  libxcb-devel
BuildRequires:  systemd-rpm-macros
BuildRequires:  tar
BuildRequires:  xz

Requires:       pam
Requires:       xorg-x11-xauth
Requires:       xorg-x11-server-Xorg
Requires:       brightnessctl

%description
Ly is a lightweight TUI (ncurses-like) display manager for Linux and BSD.
Optimized for the Nexus repository, this package tracks stable releases, utilizes
a statically injected Zig compiler to bypass distro limitations (supporting Fedora 42 to Rawhide), 
and includes a custom PAM configuration to ensure proper authentication on Fedora.

%prep
%autosetup -n ly

# Unpack the static Zig compiler directly into the build environment
tar -xf %{SOURCE2}

%build
# Execute the injected compiler instead of the system compiler
./zig-%{zig_arch}-linux-%{zig_ver}/zig build -Doptimize=ReleaseSafe

%install
# Delegate the entire installation
DESTDIR="%{buildroot}" ./zig-%{zig_arch}-linux-%{zig_ver}/zig build install --prefix /usr -Doptimize=ReleaseSafe -Dinit_system=systemd

install -d -m 0755 %{buildroot}%{_sysconfdir}/pam.d
install -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/pam.d/ly

%post
%systemd_post ly.service

%preun
%systemd_preun ly.service

%postun
%systemd_postun_with_restart ly.service

%files
%license res/license.md
%doc readme.md
%config(noreplace) %{_sysconfdir}/ly/config.ini
%config(noreplace) %{_sysconfdir}/pam.d/ly
%{_bindir}/ly
%{_unitdir}/ly.service

%changelog
* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 1.3.2-4
- Restored Static Zig 0.15.2 injection for universal F42-Rawhide compatibility
- Delegated service and config installation to Zig build system (-Dinit_system=systemd)
