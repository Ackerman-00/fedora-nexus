Name:           python-yt-dlp-get-pot
Version:        0.3.0
Release:        1%{?dist}
Summary:        PO token provider plugin for yt-dlp

License:        Unlicense
URL:            https://pypi.org/project/yt-dlp-get-pot/
Source0:        %{pypi_source yt-dlp-get-pot}

BuildRequires:  python3-devel

%description
yt-dlp-get-pot is a yt-dlp plugin that fetches PO tokens so
PO-token-gated formats (e.g. seekable Opus) keep working. Packaged
for the Nexus repository as a dependency of mixtapes.

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files yt_dlp_get_pot

%files -f %{pyproject_files}

%changelog
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.3.0-1
- Initial package (dependency of mixtapes)
