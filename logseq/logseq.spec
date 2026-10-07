%global debug_package %{nil}

Name:           logseq
Version:        2.0.2
Release:        1%{?dist}
Summary:        A privacy-first, local-first platform for knowledge management and collaboration

License:        AGPL-3.0-only
URL:            https://logseq.com/
ExclusiveArch:  x86_64

# Official Linux x86_64 payload (same files the AppImage wraps)
# sha256: 289eadd4dfcbdd2ab71aeb6cf02a53d0b5d7340865c528b1434bef8001900a9a
Source0:        https://github.com/logseq/logseq/releases/download/%{version}/Logseq-linux-x86_64-%{version}.zip
# Official icon from the matching release tag
Source1:        https://raw.githubusercontent.com/logseq/logseq/%{version}/resources/icons/logseq.png

# Disable automatic dependency generation to prevent RPM from tracking bundled Electron .so files
AutoReqProv:    no

BuildRequires:  binutils
BuildRequires:  patchelf
BuildRequires:  unzip

# Core runtime dependencies for Electron on Linux (matching the Obsidian package)
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
# @zvec/bindings-linux-x64 (the bundled DiskANN vector-search engine used by
# Logseq 2.x search) is dlopen'd at runtime and links against libaio.so.1.
# AutoReqProv is off for this package, so it must be listed explicitly.
Requires:       libaio

%description
Logseq is a privacy-first, open-source platform for knowledge management and
collaboration. It is a local-first outliner for notes, tasks and knowledge
graphs: everything is stored as plain Markdown (or Org-mode) files you control,
with support for backlinks, block-level queries and offline use.

%prep
# Create an empty build directory without looking for a tarball
%setup -c -T

# Extract the official Linux payload
unzip -q %{SOURCE0}

%build
# Nothing to compile.

%install
# 1. Install the application payload
install -dm755 %{buildroot}/opt/logseq
cp -a logseq chrome-sandbox chrome_crashpad_handler libEGL.so libGLESv2.so \
    libffmpeg.so libvk_swiftshader.so libvulkan.so.1 locales *.pak \
    resources resources.pak snapshot_blob.bin v8_context_snapshot.bin \
    vk_swiftshader_icd.json icudtl.dat LICENSE.electron.txt LICENSES.chromium.html \
    %{buildroot}/opt/logseq/

# 2. Strip build-machine RUNPATHs baked into bundled native addons (they point at
#    the upstream CI path and trip check-rpaths error 0002). All NEEDED libs of
#    these addons resolve from the system, so removing the RUNPATH is safe.
find %{buildroot}/opt/logseq/resources/app.asar.unpacked -type f \( -name '*.node' -o -name '*.so' \) -print0 |
while IFS= read -r -d '' f; do
    if readelf -d "$f" 2>/dev/null | grep -q 'RUNPATH'; then
        patchelf --remove-rpath "$f"
    fi
done

# 3. Create the global executable symlink
install -dm755 %{buildroot}%{_bindir}
ln -sf /opt/logseq/logseq %{buildroot}%{_bindir}/logseq

# 3. Install the desktop entry
install -dm755 %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/logseq.desktop <<'EOF'
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

# 4. Install the icon
install -dm755 %{buildroot}%{_datadir}/icons/hicolor/512x512/apps
install -m644 %{SOURCE1} %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/logseq.png

%files
%defattr(-,root,root,-)
%{_bindir}/logseq
/opt/logseq/
# Electron aborts at startup ("SUID sandbox helper binary was found, but is
# not configured correctly", setuid_sandbox_host.cc:166) unless chrome-sandbox
# is SUID root 4755 - proven FATAL rc=133 as non-root under xvfb 2026-10-02;
# same fix vesktop/stoat-desktop already ship, matches Google Chrome's rpm.
%attr(4755, root, root) /opt/logseq/chrome-sandbox
%{_datadir}/applications/logseq.desktop
%{_datadir}/icons/hicolor/512x512/apps/logseq.png

%changelog
* Wed Oct 07 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.2-1
- Auto-updated to 2.0.2 via update.sh
