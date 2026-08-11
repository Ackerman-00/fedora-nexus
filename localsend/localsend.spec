# Disable debuginfo extraction since we are repackaging pre-compiled binaries
%global debug_package %{nil}

# Upstream Flutter build embeds build-machine RPATHs in bundled plugins
%global __brp_check_rpaths %{nil}

# Prevent RPM from trying to auto-generate dependencies from the bundled Flutter libraries
%global __requires_exclude_from ^%{_libdir}/localsend_app/.*$
%global __provides_exclude_from ^%{_libdir}/localsend_app/.*$

Name:           localsend
Version:        1.18.0
Release:        2%{?dist}
Summary:        An open source cross-platform alternative to AirDrop

License:        GPL-3.0
URL:            https://github.com/localsend/localsend
# Use the upstream DEB as our raw source payload
Source0:        %{url}/releases/download/v1.18.0/LocalSend-1.18.0-linux-x86-64.deb

ExclusiveArch:  x86_64

# Required to unpack the upstream DEB natively
BuildRequires:  binutils
BuildRequires:  tar

# Explicit dependencies mapped from the upstream DEB to Fedora
# (libappindicator3-1 | libayatana-appindicator3-1, gir1.2-appindicator3-0.1 |
#  gir1.2-ayatanaappindicator3-0.1 -> libayatana-appindicator-gtk3,
#  libayatana-ido3-0.4-0 -> libayatana-ido-gtk3, xdg-user-dirs, libc6 -> glibc)
Requires:       libayatana-appindicator-gtk3
Requires:       libayatana-ido-gtk3
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
# Rip open the upstream DEB natively
ar x %{SOURCE0}
# Upstream switched from data.tar.xz (<=1.17.0) to data.tar.zst (>=1.18.0);
# detect whichever data archive the .deb actually contains and extract it.
for data_archive in data.tar.zst data.tar.xz data.tar.gz; do
    if [ -f "$data_archive" ]; then
        tar xf "$data_archive"
        break
    fi
done

%build
# No compilation required for pre-built binaries

%install
rm -rf %{buildroot}

# 1. Install standard desktop entries and icons
install -d -m 0755 %{buildroot}%{_datadir}
cp -a usr/share/* %{buildroot}%{_datadir}/

# 2. Install the application tree (binary + bundled lib/ + data/).
#    Upstream moved the app from usr/share/localsend_app (pre-1.18) to
#    opt/localsend_app in v1.18.0. The binary uses $ORIGIN/lib RUNPATH, so
#    the binary and its lib/ directory MUST stay adjacent.
install -d -m 0755 %{buildroot}%{_libdir}
cp -a opt/localsend_app %{buildroot}%{_libdir}/localsend_app

# 3. Create the launcher wrapper (upstream DEB ships no /usr/bin entry)
install -d -m 0755 %{buildroot}%{_bindir}
cat <<-'EOF' > %{buildroot}%{_bindir}/localsend_app
#!/bin/sh
exec %{_libdir}/localsend_app/localsend_app "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/localsend_app

%files
%{_bindir}/localsend_app
%{_datadir}/applications/localsend_app.desktop
%{_datadir}/icons/hicolor/*/apps/localsend_app.png
%{_libdir}/localsend_app/

%changelog
* Tue Aug 11 2026 Ackerman-00 <quietcraft@gmail.com> - 1.18.0-2
- Fix %%prep: upstream switched DEB data archive from data.tar.xz to data.tar.zst in v1.18.0; detect format dynamically
