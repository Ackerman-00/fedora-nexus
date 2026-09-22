# No debuginfo: pure-Python wheel, zero ELF binaries, so find-debuginfo
# would emit an empty debugsource list which rpm >= 6 rejects as a hard
# error (same failure as mixtapes build 10955014).
%global debug_package %{nil}

Name:           python-pydbus
Version:        0.6.0
Release:        4%{?dist}
Summary:        Pythonic D-Bus library

License:        LGPL-2.0-or-later
URL:            https://pypi.org/project/pydbus/
Source0:        %{pypi_source pydbus}

# Aliased name expected by dependent specs (e.g. mixtapes
# Requires: python3-pydbus); the binary RPM is named python-pydbus.
Provides:       python3-pydbus

BuildRequires:  python3-devel

# Runtime: pydbus/__init__.py does `from gi.repository.GLib import Variant`
# (PyGObject), but upstream setup.py declares no install_requires and PyPI
# requires_dist is empty, so %pyproject_* generates no dep for it. Without
# this, `import pydbus` fails with ModuleNotFoundError: No module named 'gi'
# on minimal installs (proven in f44 container teardown).
Requires:       python3-gobject

%description
pydbus provides Pythonic bindings for D-Bus. Packaged for the Nexus
repository as a dependency of mixtapes (MPRIS/tray integration).

%prep
# Unpack the PyPI sdist so %generate_buildrequires can find setup.py
# (missing %prep failed COPR build 10955044: "Neither pyproject.toml
# nor setup.py found").
%autosetup -p1 -n pydbus-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files pydbus

%files -f %{pyproject_files}

%changelog
* Tue Sep 22 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.6.0-4
- Add missing Requires: python3-gobject (pydbus/__init__.py imports
  gi.repository.GLib, but upstream declares no install_requires so the
  dep was never generated; `import pydbus` failed on minimal installs).
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.6.0-3
- Provide python3-pydbus (name expected by mixtapes Requires;
  COPR mixtapes install failed on unresolvable python3-* names).
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.6.0-2
- Add missing %prep/%autosetup (fixes COPR 10955044: %generate_buildrequires
  ran in an empty build dir).
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.6.0-1
- Initial package (dependency of mixtapes). Debuginfo disabled (pure-Python, no ELF).
