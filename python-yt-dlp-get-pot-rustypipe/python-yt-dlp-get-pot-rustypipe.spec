# No debuginfo: pure-Python wheel, zero ELF binaries, so find-debuginfo
# would emit an empty debugsource list which rpm >= 6 rejects as a hard
# error (same failure as mixtapes build 10955014).
%global debug_package %{nil}

Name:           python-yt-dlp-get-pot-rustypipe
Version:        0.2.0
Release:        2%{?dist}
Summary:        PO token provider plugin for yt-dlp using rustypipe-botguard

License:        MIT
URL:            https://pypi.org/project/yt-dlp-get-pot-rustypipe/
# NOTE: the pypi_source macro emits a dashed tarball name that 404s on
# files.pythonhosted.org for this project; use the real underscore URL.
Source0:        https://files.pythonhosted.org/packages/source/y/yt-dlp-get-pot-rustypipe/yt_dlp_get_pot_rustypipe-%{version}.tar.gz

BuildRequires:  python3-devel

%description
yt-dlp-get-pot-rustypipe is a yt-dlp plugin that fetches PO tokens
via the rustypipe-botguard helper binary. Packaged for the Nexus
repository as a dependency of mixtapes.

%prep
# Unpack the PyPI sdist so %generate_buildrequires can find the
# sources (missing %prep fails the build the same way python-pydbus
# build 10955044 and python-ytmusicapi 10955049 failed).
%autosetup -p1 -n yt_dlp_get_pot_rustypipe-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files yt_dlp_plugins

%files -f %{pyproject_files}

%changelog
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.2.0-2
- Add missing %prep/%autosetup so %generate_buildrequires finds the
  sources (same failure as pydbus 10955044 / ytmusicapi 10955049).
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.0-1
- Initial package (dependency of mixtapes). Debuginfo disabled (pure-Python, no ELF).
