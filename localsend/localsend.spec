%global debug_package %{nil}

%global __requires_exclude_from ^%{_libdir}/localsend_app/.*$
%global __provides_exclude_from ^%{_libdir}/localsend_app/.*$

Name:           localsend
Version:        1.18.2
Release:        5%{?dist}
Summary:        An open source cross-platform alternative to AirDrop

License:        Apache-2.0
URL:            https://github.com/localsend/localsend
Source0:        %{url}/releases/download/v1.18.2/LocalSend-1.18.2-linux-x86-64.deb
Source1:        %{url}/raw/v%{version}/LICENSE

ExclusiveArch:  x86_64

BuildRequires:  binutils
BuildRequires:  patchelf
BuildRequires:  tar

Requires:           hicolor-icon-theme
Requires:       libayatana-appindicator-gtk3
Requires:       libayatana-ido-gtk3
Requires:       libEGL.so.1()(64bit)
Requires:       libGLESv2.so.2()(64bit)
Requires:       xdg-user-dirs

%description
LocalSend is a free, open-source app that enables secure communication
between devices using a REST API and HTTPS encryption. Unlike other
messaging apps that rely on external servers, LocalSend doesn't require
an internet connection or third-party servers, making it a fast and
reliable solution for local communication.
Packaged exclusively for the Nexus repository. This version natively
extracts the upstream DEB payload.

%prep
%setup -c -T
ar x %{SOURCE0}
for data_archive in data.tar.zst data.tar.xz data.tar.gz; do
    if [ -f "$data_archive" ]; then
        tar xf "$data_archive"
        break
    fi
done

%build

%install

install -d -m 0755 %{buildroot}%{_datadir}
cp -a usr/share/* %{buildroot}%{_datadir}/

install -d -m 0755 %{buildroot}%{_libdir}
cp -a opt/localsend_app %{buildroot}%{_libdir}/localsend_app

install -d -m 0755 %{buildroot}%{_bindir}
cat <<-'EOF' > %{buildroot}%{_bindir}/localsend_app
#!/bin/sh
exec %{_libdir}/localsend_app/localsend_app "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/localsend_app

find %{buildroot}%{_libdir}/localsend_app/lib -type f -name '*.so*' \
    -exec patchelf --set-rpath '$ORIGIN' {} +

install -Dpm 0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/localsend_app
%{_datadir}/applications/localsend_app.desktop
%{_datadir}/icons/hicolor/*/apps/localsend_app.png
%{_libdir}/localsend_app/

%changelog
* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.18.2-5
- Rewrite the bundled plugins' RPATH to $ORIGIN. Upstream's Flutter build
  embeds /home/runner/work/localsend/.../ephemeral and the Debian multiarch
  dir in 13 .so files; rpm's check-rpaths rejected them, and the spec was
  silencing that check instead of fixing the rpaths. The check is armed again.

* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.18.2-4
- Ship the upstream Apache-2.0 LICENSE (Source1, same v1.18.2 tag as the deb
  payload, which contains no license text).
* Mon Oct 19 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.18.2-3
- Bump Release so the Apache-2.0 license correction (commit 794ee38) is
  actually published: without a new NVR the rebuild reused 1.18.2-2 and
  `dnf upgrade` reported "Nothing to do." on a clean fedora:44 container,
  leaving installed users on the stale GPL-3.0 metadata.
* Fri Oct 02 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.18.2-2
- Declare dlopened GL runtime deps (libEGL.so.1, libGLESv2.so.2): the bundled
  libflutter_linux_gtk.so links libepoxy, which opens both at startup. A clean
  fedora:44 container install aborted (rc 134, "Couldn't open libEGL.so.1",
  then libGLESv2.so.2) until libglvnd-egl and libglvnd-gles were present.
* Fri Aug 21 2026 Ackerman-00 <quietcraft@gmail.com> - 1.18.2-1
- Update to upstream v1.18.2 (full desktop assets; 1.18.1 was Android-only)
* Tue Aug 11 2026 Ackerman-00 <quietcraft@gmail.com> - 1.18.0-2
- Fix %%prep: upstream switched DEB data archive from data.tar.xz to data.tar.zst in v1.18.0; detect format dynamically
