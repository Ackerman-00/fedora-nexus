# No debuginfo: pure-Python wheel, zero ELF binaries, so find-debuginfo
# would emit an empty debugsource list which rpm >= 6 rejects as a hard
# error (same failure as mixtapes build 10955014).
%global debug_package %{nil}

Name:           python-yt-dlp-ejs
Version:        0.8.0
Release:        3%{?dist}
Summary:        External JavaScript runtimes for yt-dlp

License:        Unlicense AND MIT AND ISC
URL:            https://pypi.org/project/yt-dlp-ejs/
# NOTE: the pypi_source macro emits a dashed tarball name that 404s on
# files.pythonhosted.org for this project; use the real underscore URL.
Source0:        https://files.pythonhosted.org/packages/source/y/yt-dlp-ejs/yt_dlp_ejs-%{version}.tar.gz

# Aliased name expected by dependent specs (e.g. mixtapes
# Requires: python3-yt-dlp-ejs); the binary RPM is named python-yt-dlp-ejs.
Provides:       python3-yt-dlp-ejs

BuildRequires:  python3-devel
# Upstream hatch build hook bundles the JS solvers at build time and
# requires one of pnpm/deno/bun/npm (proven: build fails without it).
BuildRequires:  nodejs-npm

%description
yt-dlp-ejs provides external JavaScript runtimes (node/deno/quickjs)
for yt-dlp YouTube challenge solving. Packaged for the Nexus
repository as a dependency of mixtapes.

%prep
# Unpack the PyPI sdist so %generate_buildrequires can find
# pyproject.toml/setup.py (missing %prep fails the build the same way
# python-pydbus build 10955044 and python-ytmusicapi 10955049 failed).
%autosetup -p1 -n yt_dlp_ejs-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files yt_dlp_ejs

%files -f %{pyproject_files}

%changelog
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.8.0-3
- Provide python3-yt-dlp-ejs (name expected by mixtapes Requires;
  COPR mixtapes install failed on unresolvable python3-* names).
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.8.0-2
- Add missing %prep/%autosetup so %generate_buildrequires finds the
  sources (same failure as pydbus 10955044 / ytmusicapi 10955049).
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.8.0-1
- Initial package (dependency of mixtapes). Debuginfo disabled (pure-Python, no ELF).
