%global debug_package %{nil}

Name:           hatter-icon-theme
Version:        4.2
Release:        1%{?dist}
Summary:        Icon theme from Mibea/Hatter
License:        GPL-3.0-or-later
URL:            https://github.com/Mibea/Hatter
Source0:        https://github.com/Mibea/Hatter/archive/refs/tags/V4.2.tar.gz
# sha256: e82a1a5a8049c0778b454fbb2a746cb344d65ad2f59ad3b715106ea1b7fea095

BuildRequires:  bash
BuildRequires:  rsync
BuildRequires:  gtk3
BuildRequires:  findutils
BuildRequires:  coreutils
BuildRequires:  sed
BuildRequires:  gtk-update-icon-cache

BuildArch:      noarch

%description
Hatter icon theme (V4.2 release), built from the upstream Hatter sources.
Ships the base theme, nine colour variants and nine Yaru colour variants.

%prep
%setup -q -n Hatter-4.2
find . -depth -name '* *' -exec bash -c 'for f; do mv -- "$f" "${f// /-}"; done' _ {} +

%build
bash ./build.sh --all --dest dist --version %{version} --whitespace fail

%install
install -d -m 0755 %{buildroot}%{_datadir}/icons
shopt -s nullglob
for t in dist/*/; do
    cp -a "$t" "%{buildroot}%{_datadir}/icons/$(basename "$t")"
done
shopt -u nullglob
for t in %{buildroot}%{_datadir}/icons/*/; do
    gtk-update-icon-cache -q "$t" 2>/dev/null || true
done

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

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
* Sun Nov 22 2026 Ackerman-00 <no-reply> - 4.2-1
- Update to V4.2
