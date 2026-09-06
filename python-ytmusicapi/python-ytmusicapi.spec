# No debuginfo: pure-Python wheel, zero ELF binaries, so find-debuginfo
# would emit an empty debugsource list which rpm >= 6 rejects as a hard
# error (same failure as mixtapes build 10955014).
%global debug_package %{nil}

Name:           python-ytmusicapi
Version:        1.12.2
Release:        3%{?dist}
Summary:        Unofficial API for YouTube Music

License:        MIT
URL:            https://pypi.org/project/ytmusicapi/
Source0:        %{pypi_source ytmusicapi}

# Aliased name expected by dependent specs (e.g. mixtapes
# Requires: python3-ytmusicapi); the binary RPM is named python-ytmusicapi.
Provides:       python3-ytmusicapi

BuildRequires:  python3-devel

%description
ytmusicapi is an unofficial API for YouTube Music (library, search,
playlists, uploads, radio). Packaged for the Nexus repository as a
dependency of mixtapes.

%prep
# Unpack the PyPI sdist so %generate_buildrequires can find
# pyproject.toml (missing %prep failed COPR build 10955049: "Neither
# pyproject.toml nor setup.py found").
%autosetup -p1 -n ytmusicapi-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files ytmusicapi

%files -f %{pyproject_files}
# Upstream ships a console-script entry point (oauth CLI).
%{_bindir}/ytmusicapi

%changelog
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.12.2-3
- Provide python3-ytmusicapi (name expected by mixtapes Requires;
  COPR mixtapes install failed on unresolvable python3-* names).
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.12.2-2
- Add missing %prep/%autosetup (fixes COPR 10955049: %generate_buildrequires
  ran in an empty build dir).
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 1.12.2-1
- Initial package (dependency of mixtapes). Debuginfo disabled (pure-Python, no ELF).
