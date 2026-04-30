%global debug_package %{nil}

Name:           starship
Version:        1.25.1
Release:        1%{?dist}
Summary:        Minimal, blazing-fast, and customizable prompt for any shell (Nexus Optimized)

License:        ISC
URL:            https://github.com/starship/starship
Source0:        %{url}/releases/download/v%{version}/starship-x86_64-unknown-linux-gnu.tar.gz

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
rm -rf %{buildroot}

# Install the core binary
install -Dpm0755 starship -t %{buildroot}%{_bindir}/

# Install shell completions using native Fedora macros
install -d -m 0755 %{buildroot}%{bash_completions_dir}
install -d -m 0755 %{buildroot}%{zsh_completions_dir}
install -d -m 0755 %{buildroot}%{fish_completions_dir}

%{buildroot}%{_bindir}/starship completions bash > %{buildroot}%{bash_completions_dir}/starship
%{buildroot}%{_bindir}/starship completions zsh > %{buildroot}%{zsh_completions_dir}/_starship
%{buildroot}%{_bindir}/starship completions fish > %{buildroot}%{fish_completions_dir}/starship.fish

%files
%{_bindir}/starship
%{bash_completions_dir}/starship
%{zsh_completions_dir}/_starship
%{fish_completions_dir}/starship.fish

%changelog
* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 1.24.2-1
- Initial Automated Release Build utilizing native Fedora completion macros
