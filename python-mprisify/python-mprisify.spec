# No debuginfo: pure-Python wheel, no ELF binaries.
%global debug_package %{nil}

Name:           python-mprisify
Version:        1.0.1
Release:        4%{?dist}
Summary:        MPRIS D-Bus interface library for Python

License:        LGPL-3.0-only
URL:            https://gitlab.com/zehkira/mprisify
# GitLab tag archive (no PyPI release published upstream)
Source0:        https://gitlab.com/zehkira/mprisify/-/archive/v%{version}/mprisify-v%{version}.tar.gz
Source1:        %{url}/-/raw/v%{version}/LICENSE

# Aliased name expected by dependent specs.
Provides:       python3-mprisify

BuildRequires:  python3-devel

%description
mprisify is a Python library implementing the MPRIS D-Bus interface
for media players. Packaged for the Nexus repository as a dependency
of mixtapes.

%prep
# GitLab archive dir carries the commit SHA suffix; strip it.
%setup -q -c -T
tar xzf %{SOURCE0} --strip-components=1
# Map StrEnum imports to the stdlib.
sed -i '/^StrEnum==/d' source/requirements.txt
sed -i 's/^from strenum import StrEnum$/from enum import StrEnum/' source/mprisify/base.py source/mprisify/mpris/metadata.py
sed -i 's/^from strenum import LowercaseStrEnum, StrEnum$/from enum import StrEnum/' source/mprisify/enums.py
sed -i '/^from enum import StrEnum$/a\
\
\
class LowercaseStrEnum(StrEnum):\
    @staticmethod\
    def _generate_next_value_(name, start, count, last_values):\
        return name.lower()' source/mprisify/enums.py

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files mprisify

# Upstream LGPL-3.0 license text (the sdist ships none)
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

%files -f %{pyproject_files}
%license %{_licensedir}/%{name}/LICENSE

%changelog
* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.0.1-4
- Ship the upstream LGPL-3.0 LICENSE (Source1, same v1.0.1 tag); the GitLab
  sdist carries no license text.

* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.0.1-3
- Provide python3-mprisify (name expected by mixtapes Requires;
  COPR mixtapes install failed on unresolvable python3-* names).
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.0.1-2
- Map StrEnum backport imports to stdlib enum.StrEnum (not in Fedora;
  COPR 10955043 failed on python3dist(strenum)).
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 1.0.1-1
- Initial package (dependency of mixtapes). Debuginfo disabled (pure-Python, no ELF).
