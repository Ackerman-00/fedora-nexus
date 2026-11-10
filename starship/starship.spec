Name:           starship
Version:        1.27.0
Release:        3%{?dist}
Summary:        Minimal, blazing-fast, and customizable prompt for any shell (Nexus Optimized)

License:        ISC
URL:            https://github.com/starship/starship
# sha256:  f1887ffa88a7ba437d2932501794047e28d03387996f7d1c364631c053cffc44
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz
# GHSA-q54r-jf2p-rfr2
Patch0:         starship-gix-0.90.patch

ExclusiveArch:  x86_64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  rust-srpm-macros
BuildRequires:  gcc

%description
Starship is the minimal, blazing-fast, and infinitely customizable prompt for any shell.
Packaged exclusively for the Nexus repository via automated GitHub release tracking.

%prep
%autosetup -n %{name}-%{version}

%build
export CARGO_NET_OFFLINE=false
export RUSTFLAGS="%{build_rustflags}"
cargo build --release --locked

%install
install -Dpm0755 target/release/starship %{buildroot}%{_bindir}/starship

install -d -m 0755 %{buildroot}%{bash_completions_dir}
install -d -m 0755 %{buildroot}%{zsh_completions_dir}
install -d -m 0755 %{buildroot}%{fish_completions_dir}

%{buildroot}%{_bindir}/starship completions bash > %{buildroot}%{bash_completions_dir}/starship
%{buildroot}%{_bindir}/starship completions zsh > %{buildroot}%{zsh_completions_dir}/_starship
%{buildroot}%{_bindir}/starship completions fish > %{buildroot}%{fish_completions_dir}/starship.fish

%files
%license LICENSE
%{_bindir}/starship
%{bash_completions_dir}/starship
%{zsh_completions_dir}/_starship
%{fish_completions_dir}/starship.fish

%changelog
* Tue Nov 10 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.27.0-3
- Build from the v1.27.0 source tarball instead of repacking the prebuilt
  release binary, and backport upstream commit 86e1e7f0 (gix 0.90.0).
- That backport clears GHSA-q54r-jf2p-rfr2: with gix 0.89.0 an untrusted
  .git/config could disable the filesystem path-protection checks.

* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.27.0-2
- Ship the upstream ISC LICENSE as a license file (Source1, pinned to the same
  v1.27.0 tag as the binary release, which ships no license text).

* Sat Oct 17 2026 Nexus Auto-Updater <bot@github.com> - 1.27.0-1
- Update to version 1.27.0

* Sun Aug 02 2026 Ackerman-00 <no-reply> - 1.26.0-1
- Update to version 1.26.0

* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 1.24.2-1
- Initial Automated Release Build utilizing native Fedora completion macros
