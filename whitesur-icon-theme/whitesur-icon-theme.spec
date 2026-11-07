%global debug_package %{nil}

Name:           whitesur-icon-theme
Version:        2026.09.10
Release:        1%{?dist}
Summary:        WhiteSur macOS-like icon theme
License:        GPL-3.0-or-later
URL:            https://github.com/vinceliuice/WhiteSur-icon-theme
Source0:        https://github.com/vinceliuice/WhiteSur-icon-theme/archive/refs/tags/2026-09-10.tar.gz

BuildArch:      noarch
BuildRequires:  bash
BuildRequires:  coreutils
BuildRequires:  sed

%description
WhiteSur macOS-like icon theme (2026-09-10 release), packaged from upstream git.

%prep
%setup -q -n WhiteSur-icon-theme-2026-09-10

%build

%install
install -d -m 0755 %{buildroot}%{_datadir}/icons
bash ./install.sh --dest %{buildroot}%{_datadir}/icons --theme all 2>&1 || bash ./install.sh --dest %{buildroot}%{_datadir}/icons 2>&1

%files
%{_datadir}/icons/WhiteSur*

%post
gtk-update-icon-cache -q %{_datadir}/icons/WhiteSur 2>/dev/null || :
# secondary colors have their own cache
for t in %{_datadir}/icons/WhiteSur*; do gtk-update-icon-cache -q "$t" 2>/dev/null || :; done

%changelog
* Sat Nov 08 2026 Ackerman-00 <quietcraft@gmail.com> - 2026.09.10-1
- Initial import
