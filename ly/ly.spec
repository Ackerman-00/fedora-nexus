Name:           ly
Version:        1.3.2
Release:        1%{?dist}
Summary:        A lightweight TUI (ncurses-like) display manager (Nexus Optimized)

License:        WTFPL
URL:            https://codeberg.org/fairyglade/ly
Source0:        https://codeberg.org/fairyglade/ly/archive/v%{version}.tar.gz
Source1:        ly.pam

ExclusiveArch:  x86_64 aarch64

BuildRequires:  zig >= 0.13.0
BuildRequires:  kernel-devel
BuildRequires:  pam-devel
BuildRequires:  libxcb-devel
BuildRequires:  systemd-rpm-macros

Requires:       pam
Requires:       xorg-x11-xauth
Requires:       xorg-x11-server-Xorg
Requires:       brightnessctl

%description
Ly is a lightweight TUI (ncurses-like) display manager for Linux and BSD.
Optimized for the Nexus repository, this package tracks stable releases and includes 
a custom PAM configuration to ensure proper authentication and SELinux compatibility.

%prep

%autosetup -n ly

%build

zig build -Doptimize=ReleaseSafe

%install
# Install to the RPM build root
zig build install --prefix %{buildroot}%{_prefix}

# Install standard configuration files
install -d -m 0755 %{buildroot}%{_sysconfdir}/ly
install -D -m 0644 res/config.ini %{buildroot}%{_sysconfdir}/ly/config.ini

# Install the Fedora-specific PAM configuration
install -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/pam.d/ly

# Install the systemd service file
install -D -m 0644 res/ly.service %{buildroot}%{_unitdir}/ly.service

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
* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 1.3.2-1
- Switched to stable release tracking for system authentication reliability
