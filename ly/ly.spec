Name:           ly
Version:        1.3.2
Release:        5%{?dist}
Summary:        A lightweight TUI (ncurses-like) display manager (Nexus Universal)

License:        WTFPL
URL:            https://codeberg.org/fairyglade/ly
Source0:        https://codeberg.org/fairyglade/ly/archive/v%{version}.tar.gz
Source1:        ly.pam

ExclusiveArch:  x86_64 aarch64

# Fedora 43+ has the required Zig 0.15+
BuildRequires:  zig >= 0.15.0
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
Optimized for the Nexus repository, this package utilizes the native F43+ Zig compiler
and delegates the installation of configs and systemd units entirely to the Zig build system.

%prep
%autosetup -n ly

# This modifies Ly's internal systemd template before building
sed -i '/\[Unit\]/a Conflicts=getty@tty2.service\nAfter=getty@tty2.service' res/systemd/ly.service

%build
# Build the release-safe binary
zig build -Doptimize=ReleaseSafe

%install
# Delegate the entire installation
DESTDIR="%{buildroot}" zig build install --prefix /usr -Doptimize=ReleaseSafe -Dinit_system=systemd

# Ensure the Fedora-specific PAM configuration is used
install -d -m 0755 %{buildroot}%{_sysconfdir}/pam.d
install -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/pam.d/ly

%post
%systemd_post ly.service
# Make Ly the default display manager
if [ $1 -eq 1 ]; then
    systemctl set-default graphical.target || :
    ln -sf /usr/lib/systemd/system/ly.service /etc/systemd/system/display-manager.service || :
fi

%preun
%systemd_preun ly.service
# Clean up symlink on removal
if [ $1 -eq 0 ]; then
    rm -f /etc/systemd/system/display-manager.service || :
fi

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
* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 1.3.2-5
- Switched to native F43+ Zig compiler
- Delegated config and systemd installation to Zig build system
- Added TTY conflict resolution
- Added post-install hooks to set Ly as the default display manager
