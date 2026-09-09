Name:           hellwal
Version:        1.0.7
Release:        2%{?dist}
Summary:        Pywal-like color palette generator, but faster and in C

License:        MIT
URL:            https://github.com/danihek/hellwal
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Patch:          hellwal.patch

BuildRequires:  gcc

%description
%{summary}.

%prep
%autosetup -p1

%build
%make_build hellwal

%install
%make_install
# Upstream completion ships a #!/usr/bin/env bash shebang but the file is
# sourced by bash-completion, never executed (rpmlint non-executable-script)
# — drop the shebang, keep mode 644.
sed -i '1{/^#!/d}' assets/hellwal-completion.bash
install -Dpm0644 assets/hellwal-completion.bash %{buildroot}%{bash_completions_dir}/%{name}

%files
%license LICENSE
%doc templates
%doc themes
%{_bindir}/%{name}
%{bash_completions_dir}/%{name}

%changelog
* Wed Sep 09 2026 Ackerman-00 <quietcraft@gmail.com> - 1.0.7-2
- Strip upstream shebang from bash completion (sourced, never executed;
  fixes rpmlint non-executable-script error)
* Mon Aug 17 2026 Ackerman-00 <quietcraft@gmail.com> - 1.0.7-1
- Initial package