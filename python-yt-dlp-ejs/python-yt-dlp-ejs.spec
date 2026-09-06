Name:           python-yt-dlp-ejs
Version:        0.8.0
Release:        1%{?dist}
Summary:        External JavaScript runtimes for yt-dlp

License:        Unlicense AND MIT AND ISC
URL:            https://pypi.org/project/yt-dlp-ejs/
Source0:        %{pypi_source yt-dlp-ejs}

BuildRequires:  python3-devel

%description
yt-dlp-ejs provides external JavaScript runtimes (node/deno/quickjs)
for yt-dlp YouTube challenge solving. Packaged for the Nexus
repository as a dependency of mixtapes.

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files yt_dlp_ejs

%files -f %{pyproject_files}

%changelog
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.8.0-1
- Initial package (dependency of mixtapes)
