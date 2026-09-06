# No debuginfo: pure-Python wheel, zero ELF binaries, so find-debuginfo
# would emit an empty debugsource list which rpm >= 6 rejects as a hard
# error (same failure as mixtapes build 10955014).
%global debug_package %{nil}

Name:           python-mprisify
Version:        1.0.1
Release:        3%{?dist}
Summary:        MPRIS D-Bus interface library for Python

License:        LGPL-3.0-only
URL:            https://gitlab.com/zehkira/mprisify
# GitLab tag archive (no PyPI release published upstream)
Source0:        https://gitlab.com/zehkira/mprisify/-/archive/v%{version}/mprisify-v%{version}.tar.gz

# Aliased name expected by dependent specs (e.g. mixtapes
# Requires: python3-mprisify); the binary RPM is named python-mprisify.
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
# Fedora's Python (>= 3.11) ships enum.StrEnum in the stdlib and the PyPI
# StrEnum backport (0.4.15) is not packaged in Fedora (COPR build 10955043:
# "No match for argument: python3dist(strenum)"). Upstream requires-python
# is >=3.12, so map the imports to the stdlib. stdlib StrEnum auto() already
# lowercases, making this LowercaseStrEnum shim behavior-identical.
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

%files -f %{pyproject_files}

%changelog
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.0.1-3
- Provide python3-mprisify (name expected by mixtapes Requires;
  COPR mixtapes install failed on unresolvable python3-* names).
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.0.1-2
- Map StrEnum backport imports to stdlib enum.StrEnum (not in Fedora;
  COPR 10955043 failed on python3dist(strenum)).
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 1.0.1-1
- Initial package (dependency of mixtapes). Debuginfo disabled (pure-Python, no ELF).
