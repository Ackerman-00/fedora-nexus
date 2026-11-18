%global debug_package %{nil}

Name:           rustypipe-botguard
Version:        0.1.2
Release:        5%{?dist}
Summary:        YouTube Botguard challenge solver for PO token generation

License:        MIT
URL:            https://codeberg.org/ThetaDev/rustypipe-botguard

# sha256: 4f2ec561e8f9fadece7deadc6ce0624fbdedd852222c3eb194c22153b1323129
Source0:        rustypipe-botguard-v%{version}-x86_64-unknown-linux-gnu.tar.xz
Source1:        LICENSE
# sha256: fc3908dc021285b75d2fb91464dcb03545d966b9011cc009f8a230f4ce468701

ExclusiveArch:  x86_64

%description
rustypipe-botguard runs YouTube Botguard challenges and generates PO
tokens, unlocking PO-token-gated formats (e.g. seekable Opus) in
yt-dlp based players. Packaged for the Nexus repository as a helper
binary for mixtapes (expected on PATH by yt-dlp-get-pot-rustypipe).

%prep
%setup -c -T
tar xJf %{SOURCE0}

%build

%install
install -Dpm0755 rustypipe-botguard -t %{buildroot}%{_bindir}
install -Dpm0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/rustypipe-botguard

%changelog
* Wed Nov 18 2026 Ackerman-00 <no-reply> - 0.1.2-5
- Vendor the v0.1.2 release tarball as a local Source (sha256 4f2ec561, byte
  identical to the Codeberg asset, recovered from the COPR SRPM of build
  11326585) so the SRPM stage no longer depends on Codeberg DNS.

* Wed Nov 18 2026 Ackerman-00 <no-reply> - 0.1.2-4
- Vendor the MIT LICENSE as a local Source (build-time fetch from codeberg
  broke when the host did not resolve); same bytes, sha256 fc3908dc.

* Sat Nov 14 2026 Ackerman-00 <no-reply> - 0.1.2-3
- Move the in-app updater strip into %install

* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.1.2-2
- Ship the upstream MIT LICENSE (Source1, same v0.1.2 tag); the release
  tarball contains only the binary.

* Sun Sep 06 2026 Ackerman-00 <no-reply> - 0.1.2-1
- Initial package (PO-token helper for mixtapes). Debuginfo disabled (prebuilt stripped binary).
