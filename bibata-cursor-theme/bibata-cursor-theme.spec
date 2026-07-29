Name:           bibata-cursor-theme
Version:        2.0.7
Release:        1%{?dist}
Summary:        Open source, compact, and material designed cursor set

License:        GPL-3.0-or-later
URL:            https://github.com/ful1e5/Bibata_Cursor
Source0:        %{url}/releases/download/v%{version}/Bibata.tar.xz

BuildArch:      noarch

%description
Bibata is an open source, compact, and material designed cursor set that
aims to improve the cursor experience for users. It is one of the most
popular cursor sets in the Linux community and is now available for free
on Windows as well, with multiple color and size options.

%prep
%autosetup -n Bibata -a 0

%build

%install
install -d -m 0755 %{buildroot}%{_datadir}/icons
mv Bibata-* %{buildroot}%{_datadir}/icons/

%files
%{_datadir}/icons/Bibata-*

%changelog
* Wed Jul 29 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.7-1
- Initial package
