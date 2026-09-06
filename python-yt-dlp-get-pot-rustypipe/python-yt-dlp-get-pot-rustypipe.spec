Name:           python-yt-dlp-get-pot-rustypipe
Version:        0.2.0
Release:        1%{?dist}
Summary:        PO token provider plugin for yt-dlp using rustypipe-botguard

License:        MIT
URL:            https://pypi.org/project/yt-dlp-get-pot-rustypipe/
Source0:        %{pypi_source yt-dlp-get-pot-rustypipe}

BuildRequires:  python3-devel

%description
yt-dlp-get-pot-rustypipe is a yt-dlp plugin that fetches PO tokens
via the rustypipe-botguard helper binary. Packaged for the Nexus
repository as a dependency of mixtapes.

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files yt_dlp_get_pot_rustypipe

%files -f %{pyproject_files}

%changelog
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.0-1
- Initial package (dependency of mixtapes)
