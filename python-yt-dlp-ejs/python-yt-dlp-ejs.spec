%global debug_package %{nil}

Name:           python-yt-dlp-ejs
Version:        0.8.0
Release:        6%{?dist}
Summary:        External JavaScript runtimes for yt-dlp

License:        Unlicense AND MIT AND ISC
URL:            https://pypi.org/project/yt-dlp-ejs/
Source0:        https://files.pythonhosted.org/packages/source/y/yt-dlp-ejs/yt_dlp_ejs-%{version}.tar.gz

Provides:       python3-yt-dlp-ejs

BuildRequires:  python3-devel
BuildRequires:  nodejs-npm

Recommends:     yt-dlp
# The shipped bundle is JavaScript: yt-dlp needs a runtime to execute it.
# nodejs is the default; deno/bun/quickjs also work, so not a hard Requires.
Recommends:     nodejs

%description
yt-dlp-ejs provides external JavaScript runtimes (node/deno/quickjs)
for yt-dlp YouTube challenge solving. Packaged for the Nexus
repository as a dependency of mixtapes.

%prep
%autosetup -p1 -n yt_dlp_ejs-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files yt_dlp_ejs

install -Dpm 0644 LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE

%files -f %{pyproject_files}
%license %{_licensedir}/%{name}/LICENSE

%changelog
* Tue Oct 27 2026 Ackerman-00 <quietcraft@gmail.com> - 0.8.0-6
- Recommend nodejs: the package ships a JavaScript bundle that only runs on
  an external JS runtime, so without one the plugin is silently inert
* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.8.0-5
- Install the LICENSE that the 0.8.0 sdist already ships as a %license file
  (it was extracted but never installed).

* Sun Oct 04 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.8.0-4
- Add Recommends: yt-dlp (JS solvers only serve yt-dlp's YouTube
  challenge provider; both directions verified optional, so Recommends
  rather than Requires).
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.8.0-3
- Provide python3-yt-dlp-ejs (name expected by mixtapes Requires;
  COPR mixtapes install failed on unresolvable python3-* names).
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.8.0-2
- Add missing %prep/%autosetup so %generate_buildrequires finds the
  sources (same failure as pydbus 10955044 / ytmusicapi 10955049).
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.8.0-1
- Initial package (dependency of mixtapes). Debuginfo disabled (pure-Python, no ELF).
