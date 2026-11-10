%global debug_package %{nil}
%global __strip /bin/true

Name:           freebuff
Version:        0.2.36
Release:        3%{?dist}
Summary:        The free coding agent for your terminal

License:        MIT
URL:            https://freebuff.com
Source0:        https://github.com/CodebuffAI/codebuff-community/releases/download/freebuff-v%{version}/freebuff-linux-x64.tar.gz
# sha256: 672d66c3444f7469cc21b9c8a1c2c06c09676ca8f6a1771568282575a445a695
Source1:        https://raw.githubusercontent.com/CodebuffAI/codebuff-community/freebuff-v%{version}/LICENSE

ExclusiveArch:  x86_64
BuildRequires:  coreutils

Recommends:     git

%description
Freebuff is the free, ad-supported tier of Codebuff: a terminal coding agent
with specialized agents and a choice of leading models. No subscriptions,
no API keys — powerful coding models funded by text ads.

This package ships the command-line agent only. The graphical application is
a separate upstream product, packaged as freebuff-desktop.

%prep
%setup -c -T
tar xf %{SOURCE0}

%build

%install
# wasm beside the real binary
install -dm755 %{buildroot}%{_libexecdir}/%{name}
install -m755 freebuff %{buildroot}%{_libexecdir}/%{name}/freebuff
install -m644 tree-sitter.wasm %{buildroot}%{_libexecdir}/%{name}/tree-sitter.wasm

install -dm755 %{buildroot}%{_bindir}
ln -s ../libexec/%{name}/freebuff %{buildroot}%{_bindir}/freebuff

install -Dpm0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

%check
# smoke exits 0 on FAIL
smoke=$(timeout 120 %{buildroot}%{_libexecdir}/%{name}/freebuff --smoke-tree-sitter 2>&1)
printf '%s\n' "$smoke"
printf '%s\n' "$smoke" | grep -q '^tree-sitter smoke ok'

%files
%defattr(-,root,root,-)
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/freebuff
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/freebuff
%{_libexecdir}/%{name}/tree-sitter.wasm

%changelog
* Tue Nov 10 2026 Ackerman-00 <no-reply> - 0.2.36-3
- Drop a personal address from the prior changelog entries; metadata only, no payload change.
* Tue Nov 10 2026 Ackerman-00 <no-reply> - 0.2.36-2
- Drop the hand-written freebuff.desktop: upstream's CLI tarball ships no desktop
  entry or icon, and the file collided with freebuff-desktop, which owns the real
  one. This package is terminal-only and no longer appears in the app menu.
- Move the binary and tree-sitter.wasm to %%{_libexecdir}/freebuff with a
  /usr/bin/freebuff symlink. The agent resolves the wasm next to
  process.execPath, so the previous /usr/share/freebuff placement left every
  install unable to find it (--smoke-tree-sitter reported "no wasm available").
* Tue Nov 03 2026 Ackerman-00 <no-reply> - 0.2.36-1
- Auto-updated to 0.2.36 via update.sh
* Thu Oct 29 2026 Ackerman-00 <no-reply> - 0.2.35-1
- Auto-updated to 0.2.35 via update.sh
* Thu Oct 22 2026 Ackerman-00 <no-reply> - 0.2.34-1
- Auto-updated to 0.2.34 via update.sh
* Wed Oct 21 2026 Ackerman-00 <no-reply> - 0.2.33-1
- Auto-updated to 0.2.33 via update.sh
* Tue Oct 20 2026 Ackerman-00 <no-reply> - 0.2.32-1
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

* Mon Oct 19 2026 Ackerman-00 <no-reply> - 0.2.30-1
- Auto-updated to 0.2.30 via update.sh
* Thu Oct 15 2026 Ackerman-00 <no-reply> - 0.2.29-1
- Auto-updated to 0.2.29 via update.sh
* Mon Oct 12 2026 Ackerman-00 <no-reply> - 0.2.27-1
- Auto-updated to 0.2.27 via update.sh
* Thu Oct 08 2026 Ackerman-00 <no-reply> - 0.2.26-1
- Auto-updated to 0.2.26 via update.sh
* Wed Oct 07 2026 Ackerman-00 <no-reply> - 0.2.22-1
- Auto-updated to 0.2.22 via update.sh
* Wed Oct 07 2026 Ackerman-00 <no-reply> - 0.2.21-1
- Auto-updated to 0.2.21 via update.sh
* Tue Oct 06 2026 Ackerman-00 <no-reply> - 0.2.19-1
- Auto-updated to 0.2.19 via update.sh
* Mon Oct 05 2026 Ackerman-00 <no-reply> - 0.2.16-1
- Auto-updated to 0.2.16 via update.sh
* Mon Oct 05 2026 Ackerman-00 <no-reply> - 0.2.15-1
- Auto-updated to 0.2.15 via update.sh
* Mon Oct 05 2026 Ackerman-00 <no-reply> - 0.2.14-1
- Auto-updated to 0.2.14 via update.sh
* Sun Oct 04 2026 Ackerman-00 <no-reply> - 0.2.13-1
- Auto-updated to 0.2.13 via update.sh

* Fri Oct 02 2026 Ackerman-00 <no-reply> - 0.2.12-2
- Do not strip the prebuilt Bun binary: brp-strip flipped `freebuff --version`
  from 0.2.12 to the Bun runtime version 1.3.14; installed binary is now
  byte-identical to Source0 (sha256 124a45e0...)

* Fri Oct 02 2026 Ackerman-00 <no-reply> - 0.2.12-1
- Auto-updated to 0.2.12 via update.sh
