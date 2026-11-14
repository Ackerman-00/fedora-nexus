%global debug_package %{nil}

Name:           python-ytmusicapi
Version:        1.12.3
Release:        3%{?dist}
Summary:        Unofficial API for YouTube Music

License:        MIT
URL:            https://pypi.org/project/ytmusicapi/
Source0:        %{pypi_source ytmusicapi}

Provides:       python3-ytmusicapi

BuildRequires:  python3-devel

%description
ytmusicapi is an unofficial API for YouTube Music (library, search,
playlists, uploads, radio). Packaged for the Nexus repository as a
dependency of mixtapes.

%prep
%autosetup -p1 -n ytmusicapi-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files ytmusicapi
install -Dpm 0644 LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

%files -f %{pyproject_files}
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/ytmusicapi

%changelog
* Sat Nov 14 2026 Ackerman-00 <no-reply> - 1.12.3-3
- Move the in-app updater strip into %install

* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.12.3-2
- Ship the MIT LICENSE from the sdist as a proper license file.
* Wed Sep 16 2026 Ackerman-00 <no-reply> - 1.12.3-1
- Auto-update to upstream PyPI release 1.12.3

* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.12.2-3
- Provide python3-ytmusicapi (name expected by mixtapes Requires;
  COPR mixtapes install failed on unresolvable python3-* names).
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.12.2-2
- Add missing %prep/%autosetup (fixes COPR 10955049: %generate_buildrequires
  ran in an empty build dir).
* Sun Sep 06 2026 Ackerman-00 <no-reply> - 1.12.2-1
- Initial package (dependency of mixtapes). Debuginfo disabled (pure-Python, no ELF).
