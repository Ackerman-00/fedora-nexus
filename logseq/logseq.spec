%global debug_package %{nil}

Name:           logseq
Version:        2.0.2
Release:        2%{?dist}
Summary:        A privacy-first, local-first platform for knowledge management and collaboration

License:        AGPL-3.0-only
URL:            https://logseq.com/
ExclusiveArch:  x86_64

# sha256: 289eadd4dfcbdd2ab71aeb6cf02a53d0b5d7340865c528b1434bef8001900a9a
Source0:        https://github.com/logseq/logseq/releases/download/%{version}/Logseq-linux-x86_64-%{version}.zip
Source1:        https://raw.githubusercontent.com/logseq/logseq/%{version}/resources/icons/logseq.png
Source2:        https://raw.githubusercontent.com/logseq/logseq/%{version}/LICENSE.md

AutoReqProv:    no

BuildRequires:  binutils
BuildRequires:  patchelf
BuildRequires:  unzip

Requires:       zlib
Requires:       nss
Requires:       alsa-lib
Requires:       gtk3
Requires:       hicolor-icon-theme
Requires:       at-spi2-core
Requires:       libnotify
Requires:       libsecret
Requires:       libuuid
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       mesa-libgbm
Requires:       xdg-utils
Requires:       libaio

%description
Logseq is a privacy-first, open-source platform for knowledge management and
collaboration. It is a local-first outliner for notes, tasks and knowledge
graphs: everything is stored as plain Markdown (or Org-mode) files you control,
with support for backlinks, block-level queries and offline use.

%prep
%setup -c -T

unzip -q %{SOURCE0}

%build

%install
install -dm755 %{buildroot}/opt/logseq
cp -a logseq chrome-sandbox chrome_crashpad_handler libEGL.so libGLESv2.so \
    libffmpeg.so libvk_swiftshader.so libvulkan.so.1 locales *.pak \
    resources resources.pak snapshot_blob.bin v8_context_snapshot.bin \
    vk_swiftshader_icd.json icudtl.dat LICENSE.electron.txt LICENSES.chromium.html \
    %{buildroot}/opt/logseq/

find %{buildroot}/opt/logseq/resources/app.asar.unpacked -type f \( -name '*.node' -o -name '*.so' \) -print0 |
while IFS= read -r -d '' f; do
    if readelf -d "$f" 2>/dev/null | grep -q 'RUNPATH'; then
        patchelf --remove-rpath "$f"
    fi
done

install -dm755 %{buildroot}%{_bindir}
ln -sf /opt/logseq/logseq %{buildroot}%{_bindir}/logseq

install -dm755 %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/logseq-app.desktop <<'EOF'
[Desktop Entry]
Name=Logseq
Comment=A privacy-first, local-first knowledge base
Exec=/opt/logseq/logseq %U
Icon=logseq
Terminal=false
Type=Application
Categories=Office;Utility;TextEditor;
Keywords=notes;knowledge;markdown;org;
StartupWMClass=logseq
MimeType=x-scheme-handler/logseq;
EOF

install -dm755 %{buildroot}%{_datadir}/icons/hicolor/512x512/apps
install -m644 %{SOURCE1} %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/logseq.png

install -Dpm 0644 %{SOURCE2} %{buildroot}%{_licensedir}/%{name}/LICENSE.md

%files
%defattr(-,root,root,-)
%license %{_licensedir}/%{name}/LICENSE.md
%{_bindir}/logseq
/opt/logseq/
%attr(4755, root, root) /opt/logseq/chrome-sandbox
%{_datadir}/applications/logseq-app.desktop
%{_datadir}/icons/hicolor/512x512/apps/logseq.png

%changelog
* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 2.0.2-2
- Ship the upstream AGPL-3.0 LICENSE.md (Source2, same 2.0.2 tag); the
  release zip only bundles Electron/Chromium third-party notices.

* Wed Oct 07 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.2-1
- Auto-updated to 2.0.2 via update.sh
