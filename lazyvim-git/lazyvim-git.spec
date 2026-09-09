%global commit          999700997f72227187d49d8b92667183dc7fc809
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260908200953

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

# Upstream requirements (lazyvim.org): Neovim >= 0.11.2 + Git are mandatory
# (lazy.nvim clones plugins on first run); ripgrep/fd/gcc are needed for
# live-grep, file finding and treesitter parsers.
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
# One-time usage instructions on fresh installs (not on upgrades)
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
* Tue Sep 08 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1^20260908200953git9997009-1
- Sync with upstream main branch (Commit: 9997009)
