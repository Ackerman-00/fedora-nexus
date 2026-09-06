Name:           python-ytmusicapi
Version:        1.12.2
Release:        1%{?dist}
Summary:        Unofficial API for YouTube Music

License:        MIT
URL:            https://pypi.org/project/ytmusicapi/
Source0:        %{pypi_source ytmusicapi}

BuildRequires:  python3-devel

%description
ytmusicapi is an unofficial API for YouTube Music (library, search,
playlists, uploads, radio). Packaged for the Nexus repository as a
dependency of mixtapes.

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files ytmusicapi

%files -f %{pyproject_files}

%changelog
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 1.12.2-1
- Initial package (dependency of mixtapes)
