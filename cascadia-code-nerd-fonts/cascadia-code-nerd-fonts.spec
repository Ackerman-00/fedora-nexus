Name:           cascadia-code-nerd-fonts
Version:        3.5.1
Release:        2%{?dist}
Summary:        Cascadia Code patched with Nerd Fonts icons
License:        OFL-1.1
URL:            https://github.com/ryanoasis/nerd-fonts
Source0:        %{url}/releases/download/v%{version}/CascadiaCode.tar.xz

BuildArch:      noarch

%description
Cascadia Code font patched with Nerd Fonts glyphs for terminal and editor use.

%prep
%autosetup -c

%build

%install
install -m 0755 -d %{buildroot}%{_datadir}/fonts/%{name}
install -m 0644 -p *.ttf %{buildroot}%{_datadir}/fonts/%{name}/

%files
%license LICENSE
%doc README.md
%{_datadir}/fonts/%{name}

%changelog
* Mon Oct 19 2026 Ackerman-00 <quietcraft@gmail.com> - 3.5.1-2
- Ship the OFL-1.1 LICENSE and README.md that CascadiaCode.tar.xz carries as
  %license/%doc; previously the package shipped fonts with no license text
* Fri Aug 21 2026 Ackerman-00 <quietcraft@gmail.com> - 3.5.1-1
- Update to nerd-fonts 3.5.1 (CascadiaCode)
* Mon Aug 03 2026 Ackerman-00 <quietcraft@gmail.com> - 3.5.0-1
- Auto-update to version 3.5.0
