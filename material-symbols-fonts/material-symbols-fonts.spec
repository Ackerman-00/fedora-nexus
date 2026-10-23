%global commit          10ecc14790612ca8fd164e3f4ffe9c16fc50d5b7
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate         20261023021843

Name:           material-symbols-fonts
Version:        4.0.0^%{snapdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Material Symbols variable icon font by Google
License:        Apache-2.0
URL:            https://github.com/google/material-design-icons
Source0:        %{url}/raw/%{commit}/variablefont/MaterialSymbolsOutlined%%5BFILL%%2CGRAD%%2Copsz%%2Cwght%%5D.ttf#/MaterialSymbolsOutlined.ttf
Source1:        %{url}/raw/%{commit}/variablefont/MaterialSymbolsRounded%%5BFILL%%2CGRAD%%2Copsz%%2Cwght%%5D.ttf#/MaterialSymbolsRounded.ttf
Source2:        %{url}/raw/%{commit}/variablefont/MaterialSymbolsSharp%%5BFILL%%2CGRAD%%2Copsz%%2Cwght%%5D.ttf#/MaterialSymbolsSharp.ttf
# Fonts lack license text; repo text is Apache-2.0.
Source3:        %{url}/raw/%{commit}/LICENSE

BuildArch:      noarch

Requires:       fonts-filesystem

%description
Material Symbols variable icon font in Outlined, Rounded, and Sharp styles.

%prep
# Font files are used directly as sources

%build
# Nothing to build

%install
install -m 0755 -d %{buildroot}%{_datadir}/fonts/%{name}
install -m 0644 -p "%{SOURCE0}" %{buildroot}%{_datadir}/fonts/%{name}/MaterialSymbolsOutlined.ttf
install -m 0644 -p "%{SOURCE1}" %{buildroot}%{_datadir}/fonts/%{name}/MaterialSymbolsRounded.ttf
install -m 0644 -p "%{SOURCE2}" %{buildroot}%{_datadir}/fonts/%{name}/MaterialSymbolsSharp.ttf
install -Dpm 0644 %{SOURCE3} %{buildroot}%{_licensedir}/%{name}/LICENSE

%files
%license %{_licensedir}/%{name}/LICENSE
%{_datadir}/fonts/%{name}

%changelog
* Fri Oct 23 2026 Ackerman-00 <quietcraft@gmail.com> - 4.0.0^20261023021843git10ecc14-1
- Nightly sync with upstream master branch (Commit: 10ecc14)
