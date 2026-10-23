Name:           hellwal
Version:        1.0.9
Release:        1%{?dist}
Summary:        Pywal-like color palette generator, but faster and in C

License:        MIT
URL:            https://github.com/danihek/hellwal
Source:         %{url}/archive/%{version}/%{name}-%{version}.tar.gz
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
# Completion is sourced, not executed; drop the shebang.
sed -i '1{/^#!/d}' assets/hellwal-completion.bash
install -Dpm0644 assets/hellwal-completion.bash %{buildroot}%{bash_completions_dir}/%{name}

%files
%license LICENSE
%doc templates
%doc themes
%{_bindir}/%{name}
%{bash_completions_dir}/%{name}

%changelog
* Fri Oct 23 2026 Ackerman-00 <quietcraft@gmail.com> - 1.0.9-1
- Auto-update to version 1.0.9
