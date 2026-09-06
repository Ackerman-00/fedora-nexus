# No debuginfo: pure-Python wheel, zero ELF binaries, so find-debuginfo
# would emit an empty debugsource list which rpm >= 6 rejects as a hard
# error (same failure as mixtapes build 10955014).
%global debug_package %{nil}

Name:           python-pydbus
Version:        0.6.0
Release:        1%{?dist}
Summary:        Pythonic D-Bus library

License:        LGPL-2.0-or-later
URL:            https://pypi.org/project/pydbus/
Source0:        %{pypi_source pydbus}

BuildRequires:  python3-devel

%description
pydbus provides Pythonic bindings for D-Bus. Packaged for the Nexus
repository as a dependency of mixtapes (MPRIS/tray integration).

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files pydbus

%files -f %{pyproject_files}

%changelog
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.6.0-1
- Initial package (dependency of mixtapes). Debuginfo disabled (pure-Python, no ELF).
