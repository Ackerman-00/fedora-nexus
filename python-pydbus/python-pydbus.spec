# No debuginfo: pure-Python wheel, no ELF binaries.
%global debug_package %{nil}

Name:           python-pydbus
Version:        0.6.0
Release:        5%{?dist}
Summary:        Pythonic D-Bus library

License:        LGPL-2.0-or-later
URL:            https://pypi.org/project/pydbus/
Source0:        %{pypi_source pydbus}

# Aliased name expected by dependent specs.
Provides:       python3-pydbus

BuildRequires:  python3-devel

# pydbus needs PyGObject; upstream declares no dep.
Requires:       python3-gobject

%description
pydbus provides Pythonic bindings for D-Bus. Packaged for the Nexus
repository as a dependency of mixtapes (MPRIS/tray integration).

%prep
# Unpack sdist so build-requires generation finds setup.py.
%autosetup -p1 -n pydbus-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files pydbus

# Upstream LGPL-2.0-or-later license text shipped inside the sdist
install -Dpm 0644 LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE

%files -f %{pyproject_files}
%license %{_licensedir}/%{name}/LICENSE

%changelog
* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.6.0-5
- Install the LGPL-2.0-or-later LICENSE that the 0.6.0 sdist already ships
  as a %license file (it was extracted but never installed).

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
