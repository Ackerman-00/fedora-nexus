%global debug_package %{nil}

Name:           python-yt-dlp-get-pot
Version:        0.3.0
Release:        5%{?dist}
Summary:        PO token provider plugin for yt-dlp

License:        Unlicense
URL:            https://pypi.org/project/yt-dlp-get-pot/
Source0:        https://files.pythonhosted.org/packages/source/y/yt-dlp-get-pot/yt_dlp_get_pot-%{version}.tar.gz

Provides:       python3-yt-dlp-get-pot

BuildRequires:  python3-devel

Requires:       yt-dlp

%description
yt-dlp-get-pot is a yt-dlp plugin that fetches PO tokens so
PO-token-gated formats (e.g. seekable Opus) keep working. Packaged
for the Nexus repository as a dependency of mixtapes.

%prep
%autosetup -p1 -n yt_dlp_get_pot-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files yt_dlp_plugins

install -Dpm 0644 LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE

%files -f %{pyproject_files}
%license %{_licensedir}/%{name}/LICENSE

%changelog
* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.3.0-5
- Install the LICENSE that the 0.3.0 sdist already ships as a %license file
  (it was extracted but never installed).

* Sun Oct 04 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.3.0-4
- Declare Requires: yt-dlp (plugin ships yt_dlp_plugins extractor code
  that only loads inside yt-dlp; fresh-container smoke import failed
  with ModuleNotFoundError without it).
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.3.0-3
- Provide python3-yt-dlp-get-pot (name expected by mixtapes Requires;
  COPR mixtapes install failed on unresolvable python3-* names).
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.3.0-2
- Add missing %prep/%autosetup so %generate_buildrequires finds the
  sources (same failure as pydbus 10955044 / ytmusicapi 10955049).
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.3.0-1
- Initial package (dependency of mixtapes). Debuginfo disabled (pure-Python, no ELF).
