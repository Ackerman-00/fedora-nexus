Name:           hellwal
Version:        1.0.9
Release:        2%{?dist}
Summary:        Pywal-like color palette generator, but faster and in C

License:        MIT
URL:            https://github.com/danihek/hellwal
%global tag     v%{version}
Source:         %{url}/archive/%{tag}/%{name}-%{version}.tar.gz
Patch:          hellwal.patch

BuildRequires:  gcc

%description
%{summary}.

%prep
%autosetup -p1

%build
%set_build_flags
%make_build hellwal

%install
%make_install
sed -i '1{/^#!/d}' assets/hellwal-completion.bash
install -Dpm0644 assets/hellwal-completion.bash %{buildroot}%{bash_completions_dir}/%{name}
install -Dpm0644 assets/hellwal.fish %{buildroot}%{fish_completions_dir}/%{name}.fish

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

%files
%license LICENSE
%doc templates
%doc themes
%{_bindir}/%{name}
%{bash_completions_dir}/%{name}
%{fish_completions_dir}/%{name}.fish

%changelog
* Sat Nov 14 2026 Ackerman-00 <no-reply> - 1.0.9-2
- Move the in-app updater strip into %install

* Fri Oct 23 2026 Ackerman-00 <no-reply> - 1.0.9-1
- Auto-update to version 1.0.9
