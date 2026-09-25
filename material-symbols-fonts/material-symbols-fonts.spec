%global commit          bd8cb85bd4bad964fe6918f79665bb40c3a8efef
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate         20260925021835

Name:           material-symbols-fonts
Version:        4.0.0^%{snapdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Material Symbols variable icon font by Google
License:        Apache-2.0
URL:            https://github.com/google/material-design-icons
Source0:        %{url}/raw/%{commit}/variablefont/MaterialSymbolsOutlined%%5BFILL%%2CGRAD%%2Copsz%%2Cwght%%5D.ttf#/MaterialSymbolsOutlined.ttf
Source1:        %{url}/raw/%{commit}/variablefont/MaterialSymbolsRounded%%5BFILL%%2CGRAD%%2Copsz%%2Cwght%%5D.ttf#/MaterialSymbolsRounded.ttf
Source2:        %{url}/raw/%{commit}/variablefont/MaterialSymbolsSharp%%5BFILL%%2CGRAD%%2Copsz%%2Cwght%%5D.ttf#/MaterialSymbolsSharp.ttf

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

%files
%{_datadir}/fonts/%{name}

%changelog
* Fri Sep 25 2026 Ackerman-00 <quietcraft@gmail.com> - 4.0.0^20260925021835gitbd8cb85-1
- Nightly sync with upstream master branch (Commit: bd8cb85)
