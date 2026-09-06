# No debuginfo: pure-Python wheel, zero ELF binaries, so find-debuginfo
# would emit an empty debugsource list which rpm >= 6 rejects as a hard
# error (same failure as mixtapes build 10955014).
%global debug_package %{nil}

Name:           python-mprisify
Version:        1.0.1
Release:        1%{?dist}
Summary:        MPRIS D-Bus interface library for Python

License:        LGPL-3.0-only
URL:            https://gitlab.com/zehkira/mprisify
# GitLab tag archive (no PyPI release published upstream)
Source0:        https://gitlab.com/zehkira/mprisify/-/archive/v%{version}/mprisify-v%{version}.tar.gz

BuildRequires:  python3-devel

%description
mprisify is a Python library implementing the MPRIS D-Bus interface
for media players. Packaged for the Nexus repository as a dependency
of mixtapes.

%prep
# GitLab archive dir carries the commit SHA suffix; strip it.
%setup -q -c -T
tar xzf %{SOURCE0} --strip-components=1

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files mprisify

%files -f %{pyproject_files}

%changelog
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 1.0.1-1
- Initial package (dependency of mixtapes). Debuginfo disabled (pure-Python, no ELF).
