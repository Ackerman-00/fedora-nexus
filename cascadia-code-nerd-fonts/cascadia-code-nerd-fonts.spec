Name:           cascadia-code-nerd-fonts
Version:        3.4.0
Release:        1%{?dist}
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
# Nothing to build

%install
install -m 0755 -d %{buildroot}%{_datadir}/fonts/%{name}
install -m 0644 -p *.ttf %{buildroot}%{_datadir}/fonts/%{name}/

%files
%{_datadir}/fonts/%{name}

%changelog
* Sun Aug 02 2026 Ackerman-00 <quietcraft@gmail.com> - 3.4.0-1
- Revert to 3.4.0 (3.5.0 is a tag without a release; source asset 404s)
