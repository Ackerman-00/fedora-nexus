%global commit          301a3f71007c4aa5da5dab82f1a7a08389091224
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261028082036

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

Requires:       neovim >= 0.11.2
Requires:       git
Recommends:     ripgrep
Recommends:     fd-find
Recommends:     gcc
Recommends:     cascadia-code-nerd-fonts

%description
LazyVim is a Neovim setup powered by lazy.nvim to make it easy to
customize and extend your configuration. Packaged exclusively for the
Nexus repository via automated main-branch tracking.

%prep
%autosetup -n LazyVim-%{commit}

%install
install -d -m 0755 %{buildroot}%{_datadir}/lazyvim
cp -a init.lua lua doc queries scripts LICENSE NEWS.md %{buildroot}%{_datadir}/lazyvim/

%post
if [ "$1" -eq 1 ]; then
    echo
    echo "================================================================"
    echo "  lazyvim-git installs the LazyVim config to %{_datadir}/lazyvim."
    echo
    echo "  To use it, back up any existing config and link it into place:"
    echo "    mv ~/.config/nvim ~/.config/nvim.bak"
    echo "    ln -s %{_datadir}/lazyvim ~/.config/nvim"
    echo "    nvim   # plugins install on first run (needs network)"
    echo "================================================================"
fi

%files
%license LICENSE
%doc README.md
%{_datadir}/lazyvim/

%changelog
* Wed Oct 28 2026 Ackerman-00 <quietcraft@gmail.com> - 1:0.1^20261028082036git301a3f7-1
- Sync with upstream main branch (Commit: 301a3f7)
