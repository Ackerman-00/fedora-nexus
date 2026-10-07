# Debuginfo disabled: every binary here is prebuilt upstream, so there are
# no build sources to extract debug symbols from (Fedora requires stating why).
%global debug_package %{nil}
# No strip protection needed: the only strip-fragile file upstream ships
# (the Bun-compiled sidecar) is replaced by a shell wrapper below, and plain
# strip is a no-op on the remaining prebuilt ELFs. Never write RPM macro
# syntax inside comments: conditionals and directives get expanded even
# there and break parsing (COPR build 11085303 failed exactly this way).

# Electron app repacked from upstream's own .rpm. Everything travels under
# /opt/OpenCode, so bundled Chromium libraries must not leak into system
# Provides/Requires; genuine system deps are declared explicitly below.
%global __provides_exclude_from ^/opt/OpenCode/.*$
%global __requires_exclude_from ^/opt/OpenCode/.*$

Name:           opencode-desktop
Version:        2.0.24
Release:        6%{?dist}
Summary:        AI coding agent desktop app

License:        MIT
URL:            https://opencode.ai
# Upstream rpm carries a strip-damaged opencode-cli (answers 1.4.2, serve dies
# Script not found); the same-release deb verified good (v2.0.24, serve OK).
# fpm-built debs have no rpmbuild brp-strip phase, so repack from the deb.
Source0:        https://opencode.ai/files/bin/%{version}/opencode-desktop-linux-amd64.deb
# sha256: e69f2e7d535fdfcfb504fa39dade7ef76316bd499fe112c5312ec4352b8ae30d

ExclusiveArch:  x86_64

# The install section validates the desktop entry; minimal buildroots lack it.
# Unpack the upstream deb natively (same idiom as ghostty).
BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  zstd
BuildRequires:  desktop-file-utils

# Runtime deps: upstream rpm's own Requires (verified from the 2.0.22 header:
# gtk3, nss, libXScrnSaver, libnotify, at-spi2-core, xdg-utils), with the
# Debian-style rich deps mapped to Fedora names (libXtst, libuuid).
Requires:       gtk3
Requires:       nss
Requires:       libXScrnSaver
Requires:       libnotify
Requires:       at-spi2-core
Requires:       xdg-utils
Requires:       libXtst
Requires:       libuuid
Requires:       libsecret
Requires:       hicolor-icon-theme

%description
OpenCode desktop app: chat sessions, background commands and subagents, file
editing, terminal, browser panel and session management driven by local or
remote models. (For the CLI, use the upstream installer instead.)

%prep
%setup -T -c
# Rip open the upstream deb natively; detect whichever data archive it holds.
ar x %{SOURCE0}
for data_archive in data.tar.zst data.tar.xz data.tar.gz; do
    if [ -f "$data_archive" ]; then
        tar xf "$data_archive"
        break
    fi
done

%install
install -dm755 %{buildroot}/opt/OpenCode
cp -a opt/OpenCode/* %{buildroot}/opt/OpenCode/
# No bundled self-updater on a distro package: electron-updater reads
# resources/app-update.yml, and Electron's own docs say Linux updates belong
# to the package manager. Deleting it is the documented kill-switch
# (electron-builder#8838). dnf/COPR owns updates from here.
rm -f %{buildroot}/opt/OpenCode/resources/app-update.yml
# Prune musl native modules: dead weight on glibc Fedora (same prune as AUR).
find %{buildroot}/opt/OpenCode -name '*.musl.node' -delete
find %{buildroot}/opt/OpenCode -depth -type d -name '*-musl' -exec rm -rf {} + 2>/dev/null || true
# Warn if upstream's bundle is strip-damaged again (answers 1.x, not opencode
# v2*). Non-fatal: the wrapper below resolves a working CLI regardless, but
# the log should say when the bundle regresses.
if ! opt/OpenCode/resources/opencode-cli --version 2>/dev/null | grep -q '^opencode v2'; then
  echo "WARNING: bundled opencode-cli does not answer as v2 (strip damage?)" >&2
fi
# Upstream's bundled opencode-cli is a Bun --compile binary that rpm
# stripping truncates into bare bun: it answers 1.4.2 while its stamp says
# 2.x, and `serve` dies with Script not found. The desktop stages and spawns
# exactly this path with no fallback and no checksum, so every fresh install
# is broken. Replace it with a resolver wrapper (survives the desktop's
# copy+chmod staging); the original stays as last resort.
mv %{buildroot}/opt/OpenCode/resources/opencode-cli %{buildroot}/opt/OpenCode/resources/opencode-cli.bundled
cat > %{buildroot}/opt/OpenCode/resources/opencode-cli <<'CLI_EOF'
#!/bin/sh
# Resolve a working v2 CLI: user install first, then system paths, then the
# upstream bundle as last resort. Each candidate must answer `opencode v2*`.
for c in "$HOME/.opencode/bin/opencode" /usr/local/bin/opencode /usr/bin/opencode; do
    if [ -x "$c" ]; then
        case $("$c" --version 2>/dev/null) in
            "opencode v2"*) exec "$c" "$@" ;;
        esac
    fi
done
b=$(dirname "$0")/opencode-cli.bundled
[ -x "$b" ] && exec "$b" "$@"
echo "error: no working opencode v2 CLI (checked ~/.opencode/bin, /usr/local/bin, /usr/bin)" >&2
exit 127
CLI_EOF
chmod 0755 %{buildroot}/opt/OpenCode/resources/opencode-cli

install -dm755 %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/opencode-desktop <<'WRAPPER_EOF'
#!/bin/sh
# The sidecar CLI self-updates out from under the desktop version
# (packages/cli updater.ts, default policy "notify", "auto" installs).
# A distro package owns its versions, so updates stay off here.
export OPENCODE_DISABLE_AUTOUPDATE=1
exec /opt/OpenCode/ai.opencode.desktop "$@"
WRAPPER_EOF
chmod 755 %{buildroot}%{_bindir}/opencode-desktop


install -Dm0644 usr/share/icons/hicolor/32x32/apps/ai.opencode.desktop.png \
    %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/opencode-desktop.png
install -Dm0644 usr/share/icons/hicolor/64x64/apps/ai.opencode.desktop.png \
    %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/opencode-desktop.png
install -Dm0644 usr/share/icons/hicolor/128x128/apps/ai.opencode.desktop.png \
    %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/opencode-desktop.png

# Upstream desktop entries point straight at /opt and carry NoDisplay on the
# clean one; ours goes through the PATH wrapper with the SUID sandbox intact.
install -dm755 %{buildroot}%{_datadir}/applications/
cat > %{buildroot}%{_datadir}/applications/opencode-desktop.desktop <<DESKTOP_EOF
[Desktop Entry]
Type=Application
Name=OpenCode
Comment=Open source AI coding agent
Exec=opencode-desktop %U
Icon=opencode-desktop
Terminal=false
StartupWMClass=ai.opencode.desktop
MimeType=x-scheme-handler/opencode;
Categories=Development;IDE;
DESKTOP_EOF

desktop-file-validate %{buildroot}%{_datadir}/applications/opencode-desktop.desktop || true

%files
%license opt/OpenCode/LICENSE.electron.txt
%{_bindir}/opencode-desktop
/opt/OpenCode/
%{_datadir}/applications/opencode-desktop.desktop
%{_datadir}/icons/hicolor/*/apps/opencode-desktop.png
# Chromium SUID sandbox MUST stay setuid root (AGENTS.md Electron rule, Oct 2026:
# 0755 fatally aborts launch for every non-root user, proven rc=133 under xvfb).
%attr(4755, root, root) /opt/OpenCode/chrome-sandbox

%changelog
* Tue Oct 06 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.24-6
- Repack from the upstream deb: its bundled opencode-cli is intact
  (v2.0.24, serve OK) where the rpm's is strip-damaged; add libsecret
  from the deb Depends

* Tue Oct 06 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.24-5
- Purge RPM macro syntax from comments (it broke parsing in 11085303);
  add the missing desktop-file-utils BuildRequires

* Tue Oct 06 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.24-4
- Prune musl modules, warn on bundle regression; no strip hack needed

* Tue Oct 06 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.24-3
- Replace strip-damaged bundled opencode-cli with a v2 resolver wrapper

* Tue Oct 06 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.24-2
- Drop bundled electron-updater config; dnf owns updates on Fedora

* Tue Oct 06 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.24-1
- Auto-update to upstream release 2.0.24
