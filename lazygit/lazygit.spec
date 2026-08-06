%global debug_package %{nil}

Name:           lazygit
Version:        0.64.0
Release:        1%{?dist}
Summary:        A simple terminal UI for git commands (Nexus Optimized)

License:        MIT
URL:            https://github.com/jesseduffield/lazygit
Source0:        %{url}/releases/download/v%{version}/lazygit_%{version}_Linux_x86_64.tar.gz

ExclusiveArch:  x86_64

%description
A simple terminal UI for git commands, written in Go with the gocui
library. Packaged exclusively for the Nexus repository via automated
GitHub release tracking (pre-built official binary).

%prep
%setup -c -T
tar xf %{SOURCE0}

%build
# Pre-built binary, no compilation needed

%install
rm -rf %{buildroot}
install -Dpm0755 lazygit -t %{buildroot}%{_bindir}/

%files
%{_bindir}/lazygit

%license LICENSE

%changelog
* Thu Aug 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.64.0-1
- Initial package for Nexus repository