# Disable debuginfo extraction since we are repackaging pre-compiled binaries
%global debug_package %{nil}

Name:           freebuff
Version:        0.0.160
Release:        1%{?dist}
Summary:        The free coding agent for your desktop

License:        Apache-2.0
URL:            https://freebuff.com/desktop
# Standalone ELF binary + tree-sitter.wasm (upstream switched from AppImage to
# tar.gz format starting ~v0.0.80; this tag is the latest with a working release)
Source0:        https://github.com/CodebuffAI/codebuff-community/releases/download/freebuff-v%{version}/freebuff-linux-x64.tar.gz
# sha256: 2e759c6bfbebe0578b4db1712e4d14b5743876efcf6f08091c449dd697745649

ExclusiveArch:  x86_64

# Freebuff is a standalone ELF binary with minimal system deps (libc, libm,
# libpthread, libdl — all part of glibc). No Electron/AppImage runtime needed.
Recommends:     git

%description
Freebuff is the free, ad-supported tier of Codebuff: a coding agent that runs
in your desktop with parallel agents, each isolated in its own workspace.
No subscriptions, no API keys — powerful coding models funded by text ads.

%prep
%setup -c -T
tar xf %{SOURCE0}

%build
# Nothing to compile.

%install
# 1. Install the standalone binary
install -dm755 %{buildroot}%{_bindir}
install -m755 freebuff %{buildroot}%{_bindir}/freebuff

# 2. Install the tree-sitter WASM module alongside the binary
install -dm755 %{buildroot}%{_datadir}/freebuff
install -m644 tree-sitter.wasm %{buildroot}%{_datadir}/freebuff/tree-sitter.wasm

# 3. Install the standard desktop entry
install -dm755 %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/freebuff.desktop <<'EOF'
[Desktop Entry]
Name=Freebuff
Comment=The free coding agent for your desktop
Exec=freebuff %U
Icon=freebuff
Terminal=false
Type=Application
StartupWMClass=Freebuff
Categories=Development;
EOF

# 4. Install the icon (create a minimal one if upstream doesn't ship one in the tarball)
install -dm755 %{buildroot}%{_datadir}/icons/hicolor/512x512/apps
if [ -f usr/share/icons/hicolor/512x512/apps/freebuff.png ]; then
    install -m644 usr/share/icons/hicolor/512x512/apps/freebuff.png \
        %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/freebuff.png
else
    # Fallback: copy from old AppImage icon if available, or skip
    touch %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/freebuff.png
fi

%files
%defattr(-,root,root,-)
%{_bindir}/freebuff
%{_datadir}/freebuff/tree-sitter.wasm
%{_datadir}/applications/freebuff.desktop
%{_datadir}/icons/hicolor/512x512/apps/freebuff.png

%changelog
* Fri Aug 28 2026 Ackerman-00 <quietcraft@gmail.com> - 0.0.160-1
- Auto-updated to 0.0.160 via update.sh
