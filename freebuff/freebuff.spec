# Disable debuginfo extraction since we are repackaging pre-compiled binaries
%global debug_package %{nil}
# Never strip the prebuilt Bun binary: brp-strip -g made `freebuff --version`
# print the Bun runtime version (1.3.14) instead of the app version (0.2.12),
# because Bun's arg handling consults ELF symbols (2026-10-02). With stripping
# disabled the installed binary is byte-identical to upstream Source0.
%global __strip /bin/true

Name:           freebuff
Version:        0.2.14
Release:        1%{?dist}
Summary:        The free coding agent for your desktop

License:        Apache-2.0
URL:            https://freebuff.com/desktop
# Standalone ELF binary + tree-sitter.wasm (upstream switched from AppImage to
# tar.gz format starting ~v0.0.80; this tag is the latest with a working release)
Source0:        https://github.com/CodebuffAI/codebuff-community/releases/download/freebuff-v%{version}/freebuff-linux-x64.tar.gz
# sha256: 79c33e091c2c31d817aad78c71b25a1b0f23d83d8648155f44a55e0e826d877b

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
* Mon Oct 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.14-1
- Auto-updated to 0.2.14 via update.sh
* Sun Oct 04 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.13-1
- Auto-updated to 0.2.13 via update.sh

* Fri Oct 02 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.12-2
- Do not strip the prebuilt Bun binary: brp-strip flipped `freebuff --version`
  from 0.2.12 to the Bun runtime version 1.3.14; installed binary is now
  byte-identical to Source0 (sha256 124a45e0...)

* Fri Oct 02 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.12-1
- Auto-updated to 0.2.12 via update.sh
