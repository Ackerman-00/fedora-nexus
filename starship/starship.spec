%global debug_package %{nil}

Name:           starship
Version:        1.27.0
Release:        2%{?dist}
Summary:        Minimal, blazing-fast, and customizable prompt for any shell (Nexus Optimized)

License:        ISC
URL:            https://github.com/starship/starship
Source0:        %{url}/releases/download/v%{version}/starship-x86_64-unknown-linux-gnu.tar.gz
# Tarball lacks license text; fetch from the tag.
Source1:        %{url}/raw/v%{version}/LICENSE

ExclusiveArch:  x86_64

%description
Starship is the minimal, blazing-fast, and infinitely customizable prompt for any shell.
Packaged exclusively for the Nexus repository via automated GitHub release tracking.

%prep
%setup -c -T
tar xf %{SOURCE0}

%build
# Pre-built binary, no compilation needed

%install

# Install the core binary
install -Dpm0755 starship -t %{buildroot}%{_bindir}/

# Install shell completions using native Fedora macros
install -d -m 0755 %{buildroot}%{bash_completions_dir}
install -d -m 0755 %{buildroot}%{zsh_completions_dir}
install -d -m 0755 %{buildroot}%{fish_completions_dir}

%{buildroot}%{_bindir}/starship completions bash > %{buildroot}%{bash_completions_dir}/starship
%{buildroot}%{_bindir}/starship completions zsh > %{buildroot}%{zsh_completions_dir}/_starship
%{buildroot}%{_bindir}/starship completions fish > %{buildroot}%{fish_completions_dir}/starship.fish

# License text from the upstream source tree (ISC, same tag as Source0)
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/starship
%{bash_completions_dir}/starship
%{zsh_completions_dir}/_starship
%{fish_completions_dir}/starship.fish

%changelog
* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.27.0-2
- Ship the upstream ISC LICENSE as a license file (Source1, pinned to the same
  v1.27.0 tag as the binary release, which ships no license text).

* Sat Oct 17 2026 Nexus Auto-Updater <bot@github.com> - 1.27.0-1
- Update to version 1.27.0

* Sun Aug 02 2026 Ackerman-00 <quietcraft@gmail.com> - 1.26.0-1
- Update to version 1.26.0

* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 1.24.2-1
- Initial Automated Release Build utilizing native Fedora completion macros
