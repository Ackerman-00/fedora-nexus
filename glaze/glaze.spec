%global debug_package %{nil}

Name:           glaze
Version:        8.3.0
Release:        1%{?dist}
Summary:        Extremely fast, in memory, JSON and interface library
License:        MIT
URL:            https://github.com/stephenberry/glaze
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  gcc-c++

%description
%{summary}.

%package        devel
Summary:        Development files for %{name}
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}
Provides:       %{name}-static = %{version}-%{release}

%description    devel
Development files for %{name}.

%prep
%autosetup -p1

%build
%cmake \
    -Dglaze_INSTALL_CMAKEDIR=%{_datadir}/cmake/%{name} \
    -Dglaze_DISABLE_SIMD_WHEN_SUPPORTED:BOOL=ON \
    -Dglaze_DEVELOPER_MODE:BOOL=OFF \
    -Dglaze_ENABLE_FUZZING:BOOL=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_datadir}/cmake/%{name}/
%{_includedir}/%{name}/

%files devel

%changelog
* Sun Aug 30 2026 Ackerman-00 <quietcraft@gmail.com> - 8.3.0-1
- Update to 8.3.0

* Thu Aug 27 2026 Ackerman-00 <quietcraft@gmail.com> - 8.2.0-1
- Update to 8.2.0
* Tue Aug 18 2026 Ackerman-00 <quietcraft@gmail.com> - 8.1.0-1
- Update to 8.1.0
* Mon Aug 17 2026 Ackerman-00 <quietcraft@gmail.com> - 8.0.0-2
- Ship headers and cmake config in the main package so `dnf install glaze` works.
- Keep devel subpackage as compat wrapper (provides glaze-static).
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 8.0.0-1
- Initial packaging for Fedora Nexus (Nexus Optimized)