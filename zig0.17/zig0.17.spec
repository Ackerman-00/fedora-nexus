%global debug_package %{nil}

Name:           zig0.17
Version:        0.17.1
Release:        1%{?dist}
Summary:        Zig compiler and toolchain, 0.17 series
License:        MIT
URL:            https://ziglang.org/
# sha256: 3581863e3cbcfd0fce0efc682ce7e9e93da96668a977791d356a26d2a7e9b17a
Source0:        %{url}download/%{version}/zig-x86_64-linux-%{version}.tar.xz

ExclusiveArch:  x86_64

%description
Zig is a general-purpose programming language and toolchain. This package
installs the 0.17 series next to the distribution's zig: the toolchain lives
under %{_libdir}/zig/%{version} and the command is zig0.17, so both series
can be installed at once. It exists for packages that pin 0.17 syntax.

%prep
%setup -q -c -T

%build

%install
install -d %{buildroot}%{_libdir}/zig/%{version} \
    %{buildroot}%{_bindir} \
    %{buildroot}%{_licensedir}/%{name}
tar xf %{SOURCE0} -C %{buildroot}%{_libdir}/zig/%{version} --strip-components=1
install -pm0644 %{buildroot}%{_libdir}/zig/%{version}/LICENSE \
    %{buildroot}%{_licensedir}/%{name}/LICENSE
printf '#!/bin/sh\nexec %s/zig "$@"\n' \
    %{_libdir}/zig/%{version} > %{buildroot}%{_bindir}/%{name}
chmod 0755 %{buildroot}%{_bindir}/%{name}

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/%{name}
%{_libdir}/zig/%{version}

%changelog
* Tue Nov 03 2026 Nexus Auto-Updater <bot@github.com> - 0.17.1-1
- Update to the 0.17.1 Zig toolchain release
  (sha256: 3581863e3cbcfd0fce0efc682ce7e9e93da96668a977791d356a26d2a7e9b17a)
