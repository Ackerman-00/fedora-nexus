%global commit          459a4c3b1059671e766a46c7cc223827dc67e3d0
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260602133554

Name:           lazyvim-git
Epoch:          1
Version:        0.1^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Neovim setup for lazy people (Nexus Optimized Git Snapshot)
BuildArch:      noarch
License:        Apache-2.0
URL:            https://github.com/LazyVim/LazyVim
Source0:        %{url}/archive/%{commit}/lazyvim-%{shortcommit}.tar.gz
Packager:       Ackerman-00 <quietcraft@gmail.com>

%description
LazyVim is a Neovim setup powered by lazy.nvim to make it easy to
customize and extend your configuration. Packaged exclusively for the
Nexus repository via automated main-branch tracking.

%prep
%autosetup -n LazyVim-%{commit}

%install
rm -rf %{buildroot}
install -d -m 0755 %{buildroot}%{_datadir}/lazyvim
cp -a init.lua lua doc queries scripts LICENSE NEWS.md %{buildroot}%{_datadir}/lazyvim/

%files
%license LICENSE
%doc README.md
%{_datadir}/lazyvim/

%changelog
* Thu Aug 06 2026 Ackerman-00 <quietcraft@gmail.com> - 1:0.1^20260602133554git459a4c3-1
- Initial main-branch snapshot (Commit: 459a4c3)