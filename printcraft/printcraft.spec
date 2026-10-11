# Keep upstream appid: renames break StartupWMClass/AppStream matching.
# Upstream renamed the project printcraft -> pdfcraft at v0.4.0; the appid
# moved with it and the desktop file's StartupWMClass/Exec are now `pdfcraft`,
# so follow upstream's new id instead of freezing the old one.
%global appid ai.storyteller.pdfcraft

# Native binary: no bundled runtime, so no Provides pruning, no setuid sandbox.
%global debug_package %{nil}

Name:           printcraft
Version:        0.6.0
Release:        1%{?dist}
Summary:        PDF reading, organizing and protection

# Upstream nfpm.yaml and metainfo declare (MIT OR Apache-2.0). The bundled
# OFL font texts ship as %license files: BIZ UD Mincho, BIZ UD PGothic,
# Shippori Mincho and Noto Sans Arabic are embedded in the binary (strings
# output, verified 2026-10-11); upstream added the Noto Sans CJK SC OFL text
# alongside them at v0.6.0 and ships it in its rpm, so ship it too.
License:        (MIT OR Apache-2.0) AND OFL-1.1
URL:            https://getartcraft.com/apps/pdfcraft
Source0:        https://github.com/storytold/pdfcraft/releases/download/v0.6.0/pdfcraft-%{version}-linux-x86_64.rpm
# sha256: 33e4e947115ad886b23241fce750ffcd55fd1eab4e2ee90dc2503b3f86aa9802

# Upstream renamed at v0.4.0, but the package keeps its name so existing
# `dnf install printcraft` invocations keep resolving; provide the new name
# too for anyone following the renamed upstream docs.
Provides:       pdfcraft = %{version}-%{release}

# %install runs desktop-file-validate; the buildroot does not provide it.
BuildRequires:  desktop-file-utils

# Verified against upstream packaging/linux/nfpm.yaml at v0.4.0. The binary
# dlopens both stacks (eframe enables wayland+x11; strings confirm libdbus),
# so loaders are hard Requires. PDF rendering is in-tree Rust.
# readelf -d on the 0.6.0 binary lists only libgcc_s/libm/libc/ld-linux in
# NEEDED (verified 2026-10-11), so rpm's ELF generator cannot see any of the
# libraries below: these explicit Requires are load-bearing, not duplicates.
# That is why rpmlint reports explicit-lib-dependency here - false positive
# for a dlopen-based binary.
# Arch->Fedora: libglvnd->mesa-libGL, vulkan-icd-loader->vulkan-loader.
Requires:       dbus
Requires:       libX11
Requires:       libXcursor
Requires:       libXi
Requires:       libXrandr
Requires:       libwayland-client
Requires:       libxkbcommon
Requires:       libxkbcommon-x11
Requires:       mesa-libGL
Requires:       vulkan-loader
Requires:       xkeyboard-config
Requires:       hicolor-icon-theme
# wgpu picks Vulkan or GL at runtime; drivers stay Recommends.
Recommends:     mesa-vulkan-drivers
Recommends:     xdg-desktop-portal
Recommends:     xdg-utils

%description
PdfCraft (this package keeps the printcraft name for installed systems) is a
PDF workbench: read, comment on, fill and sign forms, organize, combine and
split pages, redact and protect documents with its own pure-Rust rendering
engine, plus a headless CLI.

%prep
%setup -T -c
# Upstream rpm is a plain FHS tree (see packaging/linux/package.sh); repack it.
rpm2cpio %{SOURCE0} | cpio -idmv

%install
mkdir -p %{buildroot}%{_bindir}
install -m755 usr/bin/pdfcraft %{buildroot}%{_bindir}/pdfcraft
install -m755 usr/bin/pdfcraft-cli %{buildroot}%{_bindir}/pdfcraft-cli

# Ship the desktop file as-is: Icon/StartupWMClass already match the appid.
install -Dm0644 usr/share/applications/%{appid}.desktop \
    %{buildroot}%{_datadir}/applications/%{appid}.desktop

# Fixed pngs plus one scalable svg; the .attribution sidecar is not shipped.
for size in 16x16 24x24 32x32 48x48 64x64 128x128 256x256 512x512; do
    i=usr/share/icons/hicolor/$size/apps/%{appid}.png
    [ -e "$i" ] || continue
    install -Dm0644 "$i" \
        %{buildroot}%{_datadir}/icons/hicolor/$size/apps/%{appid}.png
done
i=usr/share/icons/hicolor/scalable/apps/%{appid}.svg
[ -e "$i" ] && install -Dm0644 "$i" \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{appid}.svg
true

install -Dm0644 usr/share/metainfo/%{appid}.metainfo.xml \
    %{buildroot}%{_datadir}/metainfo/%{appid}.metainfo.xml

# One shared-mime-info stub, empty at 0.4.0 (application/pdf is already in
# the base database); ship it so future upstream type additions land without
# a spec edit. shared-mime-info's file trigger runs update-mime-database, so
# no scriptlet here (obsidian precedent).
install -Dm0644 usr/share/mime/packages/%{appid}.xml \
    %{buildroot}%{_datadir}/mime/packages/%{appid}.xml

# OCR models. The binary resolves them at ../share/pdfcraft/models relative to
# its own path (/usr/bin -> /usr/share/pdfcraft/models) and prints "the text
# recognition models are not installed" when they are missing (strings output,
# verified 2026-10-11); upstream's rpm ships them there too. Without this
# install Scan & OCR and searchable-text export are dead in our package.
mkdir -p %{buildroot}%{_datadir}/pdfcraft/models
install -m0644 usr/share/pdfcraft/models/* \
    %{buildroot}%{_datadir}/pdfcraft/models/

desktop-file-validate %{buildroot}%{_datadir}/applications/%{appid}.desktop

%files
%license usr/share/doc/pdfcraft/LICENSE-MIT
%license usr/share/doc/pdfcraft/LICENSE-APACHE
%license usr/share/doc/pdfcraft/NOTICE
%license usr/share/doc/pdfcraft/OFL-biz-ud-mincho.txt
%license usr/share/doc/pdfcraft/OFL-biz-ud-pgothic.txt
%license usr/share/doc/pdfcraft/OFL-noto-sans-arabic.txt
%license usr/share/doc/pdfcraft/OFL-noto-sans-cjk-sc.txt
%license usr/share/doc/pdfcraft/OFL-shippori-mincho.txt
%doc usr/share/doc/pdfcraft/README.md
%{_bindir}/pdfcraft
%{_bindir}/pdfcraft-cli
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/icons/hicolor/*/apps/%{appid}.png
%{_datadir}/icons/hicolor/*/apps/%{appid}.svg
%{_datadir}/metainfo/%{appid}.metainfo.xml
%{_datadir}/mime/packages/%{appid}.xml
%{_datadir}/pdfcraft/models/

%post
# || : so a locked icon cache never fails the install.
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :

%postun
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :

%changelog
* Sun Oct 11 2026 Ackerman-00 <quietcraft@gmail.com> - 0.6.0-1
- Auto-update to upstream release v0.6.0
- Ship the OCR models in %%{_datadir}/pdfcraft/models: the binary looks for
  them there and Scan & OCR was dead without them (present since 0.4.0)
- Ship the NOTICE file and the two OFL texts upstream added at v0.6.0
