%global             full_name zen-browser
%global             application_name zen
%global             debug_package %{nil}

# Zen ships a private copy of the Gecko runtime (libxul, NSS/NSPR, ffmpeg
# codecs, ...) under /opt/zen. Those bundled libraries must not be advertised
# as system-wide Provides - otherwise dnf can satisfy an unrelated dependency
# on e.g. libnss3.so with the whole browser. The internal-only libraries must
# likewise not become system Requires; genuine system library dependencies
# (gtk, X11, wayland, ...) are still auto-generated and kept.
%global             __provides_exclude_from ^/opt/%{application_name}/.*$
%global             __requires_exclude ^lib(gkcodecs|lgpllibs|mozavutil|mozgtk|mozsandbox|mozsqlite3|mozwayland)\\.so.*$

Name:               zen-browser
# Upstream DELETED the 1.21.13b release after we had already shipped
# zen-browser-1.21.13b-1 to COPR. Reverting the spec to the real current
# release (1.21.12b) is not enough: 1.21.12b-3 sorts BELOW the withdrawn
# 1.21.13b-1, so dnf would keep offering users the withdrawn build forever.
# An Epoch is the only correct way to supersede a higher version.
Epoch:              1
Version:        1.21.13b
Release:        1%{?dist}
Summary:            Zen Browser - A privacy-focused Firefox fork

License:            MPLv2.0
URL:                https://github.com/zen-browser/desktop
Source0:            https://github.com/zen-browser/desktop/releases/download/1.21.13b/zen.linux-x86_64.tar.xz
Source1:            %{full_name}.desktop
Source2:            policies.json
Source3:            %{full_name}

ExclusiveArch:      x86_64
BuildRequires:      patchelf

Recommends:         (plasma-browser-integration if plasma-workspace)
Recommends:         (gnome-browser-connector if gnome-shell)

Requires(post):     gtk-update-icon-cache
Conflicts:          zen-browser-avx2
Provides:           zen-browser-avx2 = %{epoch}:%{version}-%{release}
Obsoletes:          zen-browser-avx2 < 1.0.2.b.3-3

%description
Zen Browser is a highly optimized, privacy-focused fork of Firefox designed for performance and simplicity. 

%prep
%setup -q -n %{application_name}

%install
rm -rf %{buildroot}

install -d %{buildroot}/opt/%{application_name}
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_datadir}/applications
install -d %{buildroot}%{_datadir}/icons/hicolor/{16x16,32x32,48x48,64x64,128x128}/apps
install -d %{buildroot}%{_datadir}/pixmaps

cp -r * %{buildroot}/opt/%{application_name}

install -D -m 0644 %{SOURCE1} -t %{buildroot}%{_datadir}/applications
install -D -m 0444 %{SOURCE2} -t %{buildroot}/opt/%{application_name}/distribution
install -D -m 0755 %{SOURCE3} -t %{buildroot}%{_bindir}

# Convenience symlink
ln -sf %{full_name} %{buildroot}%{_bindir}/zen

# Safeguard: Only run patchelf if upstream actually shipped libonnxruntime.so in the root
if [ -f "%{buildroot}/opt/%{application_name}/libonnxruntime.so" ]; then
    patchelf --set-rpath '$ORIGIN' %{buildroot}/opt/%{application_name}/libonnxruntime.so
fi

# Icons - symlinks from upstream icons
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{full_name}.png
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default64.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/%{full_name}.png
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default48.png %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/%{full_name}.png
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default32.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{full_name}.png
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default16.png %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/%{full_name}.png

# Pixmaps icon for legacy apps
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default128.png %{buildroot}%{_datadir}/pixmaps/%{full_name}.png

%post
# Added || : to prevent post-install scriptlet failures if the icon cache is locked
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :

%files
%{_datadir}/applications/%{full_name}.desktop
%{_datadir}/icons/hicolor/128x128/apps/%{full_name}.png
%{_datadir}/icons/hicolor/64x64/apps/%{full_name}.png
%{_datadir}/icons/hicolor/48x48/apps/%{full_name}.png
%{_datadir}/icons/hicolor/32x32/apps/%{full_name}.png
%{_datadir}/icons/hicolor/16x16/apps/%{full_name}.png
%{_datadir}/pixmaps/%{full_name}.png
%{_bindir}/%{full_name}
%{_bindir}/zen
/opt/%{application_name}

%changelog
* Mon Aug 10 2026 Ackerman-00 <quietcraft@gmail.com> - 1:1.21.13b-1
- Auto-update to upstream release 1.21.13b
