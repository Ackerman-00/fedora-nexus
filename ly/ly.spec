# Vendored Zig dependency versions, synced by update.sh from vendor.tar.zst.
%global clap_ver 0.12.0
%global zigini_ver 0.6.0
%global ini_ver 0.1.0
%global zlua_ver 0.1.0

Name:           ly
Version:        1.5.0
Release:        1%{?dist}
Summary:        Lightweight TUI display manager

License:        WTFPL AND MIT
URL:            https://codeberg.org/fairyglade/ly
# Codeberg archive 503s; fetch the GitHub mirror instead.
Source0:        https://github.com/fairyglade/ly/archive/v%{version}.tar.gz#/ly-%{version}.tar.gz
# Upstream vendor bundle: every Zig dependency, fetched with --system zig-pkg.
Source1:        %{url}/releases/download/v%{version}/vendor.tar.zst#/ly-%{version}-vendor.tar.zst
Patch0:         0001-build-enable-pie.patch

# zig0.17 is x86_64-only; ly 1.5.0 needs the 0.17 series.
ExclusiveArch:  x86_64

BuildRequires:  gcc
BuildRequires:  help2man
BuildRequires:  pam-devel
BuildRequires:  pkgconfig(xcb)
BuildRequires:  systemd-rpm-macros
BuildRequires:  tar
BuildRequires:  zig0.17
BuildRequires:  zstd

Requires(post):      policycoreutils
Requires(posttrans): policycoreutils

Provides:       bundled(zig-clap) = %{clap_ver}
Provides:       bundled(zigini) = %{zigini_ver}
Provides:       bundled(ini) = %{ini_ver}
Provides:       bundled(zlua) = %{zlua_ver}
Provides:       bundled(termbox2)
Provides:       bundled(luajit)
Provides:       bundled(zig-translate-c)
Provides:       bundled(aro)

Recommends:     brightnessctl

%description
Ly is a lightweight TUI display manager for Linux and BSD, designed with
portability in mind and without a dependency on systemd.

%prep
%autosetup -n %{name}-%{version} -a 1 -p1

%build
# 0.17 takes its caches from the environment; the flags moved.
export ZIG_GLOBAL_CACHE_DIR=%{_builddir}/zig-cache
export ZIG_LOCAL_CACHE_DIR=%{_builddir}/zig-cache
zig0.17 build --release=safe --system zig-pkg \
    -Dtarget=native -Dcpu=baseline --build-id=sha1

%install
export ZIG_GLOBAL_CACHE_DIR=%{_builddir}/zig-cache
export ZIG_LOCAL_CACHE_DIR=%{_builddir}/zig-cache
zig0.17 build installexe -Ddest_directory=%{buildroot} --release=safe \
    --system zig-pkg -Dtarget=native -Dcpu=baseline --build-id=sha1

# Hooks are config; invoke via /bin/sh, mode 644.
sed -i '1{/^#!/d}' %{buildroot}%{_sysconfdir}/ly/setup.sh
sed -i 's|%{_sysconfdir}/ly/setup.sh|/bin/sh %{_sysconfdir}/ly/setup.sh|' \
    %{buildroot}%{_sysconfdir}/ly/config.ini
sed -i '1{/^#!/d}' %{buildroot}%{_sysconfdir}/ly/startup.sh
sed -i 's|%{_sysconfdir}/ly/startup.sh|/bin/sh %{_sysconfdir}/ly/startup.sh|' \
    %{buildroot}%{_sysconfdir}/ly/config.ini

rm -f %{buildroot}%{_sysconfdir}/ly/config.ini.example

mkdir -p %{buildroot}%{_mandir}/man1
help2man --no-discard-stderr -o %{buildroot}%{_mandir}/man1/ly.1 %{buildroot}%{_bindir}/ly

install -d %{buildroot}%{_licensedir}/ly
install -pm0644 license.md %{buildroot}%{_licensedir}/ly/LICENSE-ly.md
# Every bundled dependency's own license text, whatever upstream ships it as.
for lic in zig-pkg/*/LICENSE zig-pkg/*/LICENCE zig-pkg/*/license \
    zig-pkg/*/LICENSE-* zig-pkg/*/COPYRIGHT zig-pkg/*/COPYING; do
    [ -f "$lic" ] || continue
    dep=$(basename "$(dirname "$lic")")
    base=$(basename "$lic")
    case "$base" in
        LICENSE|LICENCE|license|COPYRIGHT|COPYING)
            install -pm0644 "$lic" "%{buildroot}%{_licensedir}/ly/LICENSE-$dep" ;;
        *)
            install -pm0644 "$lic" "%{buildroot}%{_licensedir}/ly/LICENSE-$dep-${base#LICENSE-}" ;;
    esac
done

%check
# Upstream ships no test target: prove the linked binary starts.
./zig-out/bin/ly --help > /dev/null

%post
%systemd_post ly@.service ly-kmsconvt@.service

# https://codeberg.org/fairyglade/ly/issues/494
%{_sbindir}/semanage fcontext -a -t xdm_exec_t %{_bindir}/ly 2>/dev/null || \
%{_sbindir}/semanage fcontext -m -t xdm_exec_t %{_bindir}/ly 2>/dev/null || :
%{_sbindir}/restorecon %{_bindir}/ly 2>/dev/null || :

# One-time enable instructions on fresh installs (not on upgrades)
if [ "$1" -eq 1 ]; then
    echo
    echo "================================================================"
    echo "  ly is installed but NOT enabled as your display manager yet."
    echo
    echo "  Enable it with:"
    echo "    sudo systemctl enable ly@tty2.service"
    if [ "$(systemctl get-default 2>/dev/null)" = "multi-user.target" ]; then
        echo "  Your system boots to multi-user.target - switch to graphical.target:"
        echo "    sudo systemctl set-default graphical.target"
    fi
    echo "  Start it right away with:"
    echo "    sudo systemctl start ly@tty2.service"
    echo
    echo "  Tip: disable getty on the same tty to avoid conflicts:"
    echo "    sudo systemctl disable getty@tty2.service"
    echo "================================================================"
fi

%preun
%systemd_preun ly@.service ly-kmsconvt@.service

if [ $1 -eq 0 ]; then
    %{_sbindir}/semanage fcontext -d %{_bindir}/ly 2>/dev/null || :
fi

%files
%license %{_licensedir}/ly/*
%doc readme.md

%{_bindir}/ly
%{_mandir}/man1/ly.1*
%{_unitdir}/ly@.service
%{_unitdir}/ly-kmsconvt@.service
%dir %{_sysconfdir}/ly
%dir %{_sysconfdir}/ly/custom-sessions
%dir %{_sysconfdir}/ly/lang
%config(noreplace) %{_sysconfdir}/pam.d/ly
%config(noreplace) %{_sysconfdir}/pam.d/ly-autologin
%config(noreplace) %{_sysconfdir}/ly/config.ini
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/ly/setup.sh
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/ly/startup.sh
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/ly/example.dur
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/ly/example.lua
%config(noreplace) %{_sysconfdir}/ly/custom-sessions/README
%config(noreplace) %{_sysconfdir}/ly/lang/*.ini

%changelog
* Wed Oct 21 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.5.0-1
- Update to upstream 1.5.0, which requires Zig 0.17.0 (Fedora ships 0.16):
  build with the new zig0.17 parallel toolchain instead of the distro zig.
- Declare --system zig-pkg and drop the %%zig_fetch calls: the vendor bundle
  supplies every dependency and the 0.17 series renamed the cache flags.
- Install every bundled license text found in the vendor bundle, including
  the LuaJIT COPYRIGHT and zlua's license, which 1.4.1 never shipped.
- Refresh the PIE patch against the 1.5.0 build.zig.
