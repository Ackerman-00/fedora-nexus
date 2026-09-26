# Disable debuginfo extraction since we are repackaging pre-compiled binaries
%global debug_package %{nil}

Name:           freebuff
Version:        0.0.204
Release:        1%{?dist}
Summary:        The free coding agent for your desktop

License:        Apache-2.0
URL:            https://freebuff.com/desktop
# Standalone ELF binary + tree-sitter.wasm (upstream switched from AppImage to
# tar.gz format starting ~v0.0.80; this tag is the latest with a working release)
Source0:        https://github.com/CodebuffAI/codebuff-community/releases/download/freebuff-v%{version}/freebuff-linux-x64.tar.gz
# sha256: 9b090e66c07804bd1975e6986d73826ad07fb1fbb70b10268067a2d5371f10e7

ExclusiveArch:  x86_64
BuildRequires:  desktop-file-utils

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

# 3. Install the standard desktop entry (no Icon: upstream ships no icon
# in the tar.gz and a zero-byte placeholder breaks icon lookup, 2026-09-23)
install -dm755 %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/freebuff.desktop <<'EOF'
[Desktop Entry]
Name=Freebuff
Comment=The free coding agent for your desktop
Exec=freebuff %U
Terminal=false
Type=Application
StartupWMClass=Freebuff
Categories=Development;
EOF

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/freebuff.desktop

%files
%defattr(-,root,root,-)
%{_bindir}/freebuff
%{_datadir}/freebuff/tree-sitter.wasm
%{_datadir}/applications/freebuff.desktop

%changelog
* Sat Sep 26 2026 Ackerman-00 <quietcraft@gmail.com> - 0.0.204-1
- Auto-updated to 0.0.204 via update.sh
