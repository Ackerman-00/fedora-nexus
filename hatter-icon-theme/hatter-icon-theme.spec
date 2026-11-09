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
BuildRequires:  gtk-update-icon-cache

BuildArch:      noarch

%description
Hatter icon theme (V4.0 release), built from the upstream Hatter sources.

%prep
%setup -q -n Hatter-4.0
find . -depth -name '* *' -exec bash -c 'for f; do mv -- "$f" "${f// /-}"; done' _ {} +

%build
echo 2 | bash ./Build-Hatter.sh

%install
install -d -m 0755 %{buildroot}%{_datadir}/icons
shopt -s nullglob
for t in Build/*/; do
    [ -d "$t" ] || continue
    cp -a "$t" "%{buildroot}%{_datadir}/icons/$(basename "$t")"
done
shopt -u nullglob
for t in %{buildroot}%{_datadir}/icons/*/; do
    gtk-update-icon-cache -q "$t" 2>/dev/null || true
done

%files
%license COPYING
%{_datadir}/icons/Hatter*/

%post
for t in %{_datadir}/icons/Hatter*/; do
    gtk-update-icon-cache -q "$t" 2>/dev/null || :
done
%postun
for t in %{_datadir}/icons/Hatter*/; do
    gtk-update-icon-cache -q "$t" 2>/dev/null || :
done

%changelog
* Sat Nov 07 2026 Ackerman-00 <no-reply> - 4.0-1
- Initial import
