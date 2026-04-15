%global zig_ver 0.15.2

Name:           ly
Version:        1.3.2
Release:        8%{?dist}
Summary:        A lightweight TUI (ncurses-like) display manager (Nexus Universal)

License:        WTFPL
URL:            https://codeberg.org/fairyglade/ly
Source0:        https://codeberg.org/fairyglade/ly/archive/v%{version}.tar.gz
Source1:        ly.pam

Source2:        https://ziglang.org/download/%{zig_ver}/zig-x86_64-linux-%{zig_ver}.tar.xz
Source3:        https://ziglang.org/download/%{zig_ver}/zig-aarch64-linux-%{zig_ver}.tar.xz

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
Optimized for the Nexus repository. Uses a statically injected Zig compiler
to ensure API compatibility across Fedora 42 through Rawhide.

%prep
%autosetup -n ly

%ifarch x86_64
tar -xf %{SOURCE2}
%global zig_bin ./zig-x86_64-linux-%{zig_ver}/zig
%endif

%ifarch aarch64
tar -xf %{SOURCE3}
%global zig_bin ./zig-aarch64-linux-%{zig_ver}/zig
%endif

# Create the systemd service file manually to bypass Zig's broken installer
cat << 'EOF' > ly.service
[Unit]
Description=TUI display manager
After=systemd-user-sessions.service plymouth-quit-wait.service
After=getty@tty2.service
Conflicts=getty@tty2.service

[Service]
Type=idle
ExecStart=/usr/bin/ly
StandardInput=tty
TTYPath=/dev/tty2
TTYReset=yes
TTYVHangup=yes

[Install]
Alias=display-manager.service
EOF

%build
%{zig_bin} build -Doptimize=ReleaseSafe

%install
# Only install the binary and config using Zig
DESTDIR="%{buildroot}" %{zig_bin} build install --prefix /usr -Doptimize=ReleaseSafe

# Manually install our custom PAM configuration
install -d -m 0755 %{buildroot}%{_sysconfdir}/pam.d
install -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/pam.d/ly

# Manually install our custom systemd service file
install -d -m 0755 %{buildroot}%{_unitdir}
install -m 0644 ly.service %{buildroot}%{_unitdir}/ly.service

%post
%systemd_post ly.service
if [ $1 -eq 1 ]; then
    systemctl set-default graphical.target || :
    ln -sf /usr/lib/systemd/system/ly.service /etc/systemd/system/display-manager.service || :
fi

%preun
%systemd_preun ly.service
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
* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 1.3.2-8
- Manually generated systemd unit to bypass Zig build failures and apply TTY fixes
