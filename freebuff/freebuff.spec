# Disable debuginfo extraction since we are repackaging pre-compiled binaries
%global debug_package %{nil}
# Never strip the prebuilt Bun binary.
%global __strip /bin/true

Name:           freebuff
Version:        0.2.32
Release:        1%{?dist}
Summary:        The free coding agent for your desktop

License:        MIT
URL:            https://freebuff.com/desktop
Source0:        https://github.com/CodebuffAI/codebuff-community/releases/download/freebuff-v%{version}/freebuff-linux-x64.tar.gz
# sha256: fe6d194ab7f0722e3243f2442c70cc7ebeeda407da6e46c8de4e891709441ffb
# The binary tarball carries no license text; the release repo's MIT
Source1:        https://raw.githubusercontent.com/CodebuffAI/codebuff-community/freebuff-v%{version}/LICENSE

ExclusiveArch:  x86_64
BuildRequires:  desktop-file-utils

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

# License text from the upstream release repo (MIT, same release tag)
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

# No upstream icon; install the standard desktop entry.
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
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/freebuff
%{_datadir}/freebuff/tree-sitter.wasm
%{_datadir}/applications/freebuff.desktop

%changelog
* Tue Oct 20 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.32-1
- Auto-updated to 0.2.32 via update.sh
* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.2.30-3
- Pin Source0's sha256 under Source0: the hash was written below Source1,
  so it read as a pin of the LICENSE text it does not match.

* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.2.30-2
- Ship the MIT LICENSE text from the release repo (Source1, same
  freebuff-v0.2.30 tag as Source0, which carries no license text).
- Correct License: Apache-2.0 -> MIT: the release repository's LICENSE and
  the GitHub license API both report MIT, and no Apache-2.0 text exists in
  the artifact or the repository root.

* Mon Oct 19 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.30-1
- Auto-updated to 0.2.30 via update.sh
* Thu Oct 15 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.29-1
- Auto-updated to 0.2.29 via update.sh
* Mon Oct 12 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.27-1
- Auto-updated to 0.2.27 via update.sh
* Thu Oct 08 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.26-1
- Auto-updated to 0.2.26 via update.sh
* Wed Oct 07 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.22-1
- Auto-updated to 0.2.22 via update.sh
* Wed Oct 07 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.21-1
- Auto-updated to 0.2.21 via update.sh
* Tue Oct 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.19-1
- Auto-updated to 0.2.19 via update.sh
* Mon Oct 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.16-1
- Auto-updated to 0.2.16 via update.sh
* Mon Oct 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.15-1
- Auto-updated to 0.2.15 via update.sh
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
