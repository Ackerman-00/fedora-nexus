%global debug_package %{nil}

Name:           hatter-icon-theme
Version:        4.0
Release:        1%{?dist}
Summary:        Icon theme from Mibea/Hatter
License:        GPL-3.0-or-later
URL:            https://github.com/Mibea/Hatter
Source0:        https://github.com/Mibea/Hatter/archive/refs/tags/V4.0.tar.gz

BuildRequires:  bash
BuildRequires:  rsync
BuildRequires:  gtk3
BuildRequires:  findutils
BuildRequires:  coreutils
BuildRequires:  sed

BuildArch:      noarch

%description
Hatter icon theme (V4.0 release), built from the upstream Hatter sources.

%prep
%setup -q -n Hatter-V4.0

%build
bash ./Build-Hatter.sh >/dev/null

%install
install -d -m 0755 %{buildroot}%{_datadir}/icons
shopt -s nullglob
for t in Build/*/; do
    [ -d "$t" ] || continue
    cp -a "$t" "%{buildroot}%{_datadir}/icons/$(basename %{t})"
done
shopt -u nullglob
for t in %{buildroot}%{_datadir}/icons/*/; do
    gtk-update-icon-cache -q "$t" 2>/dev/null || true
done

%files
%{_datadir}/icons/Hatter*/
%{_datadir}/icons/Hatter-Yaru-*/

%post
gtk-update-icon-cache -q %{_datadir}/icons/Hatter 2>/dev/null || :
gtk-update-icon-cache -q %{_datadir}/icons/Hatter-Yaru-2>/dev/null || :

%changelog
* Sat Nov 08 2026 Ackerman-00 <quietcraft@gmail.com> - 4.0-1
- Initial import
