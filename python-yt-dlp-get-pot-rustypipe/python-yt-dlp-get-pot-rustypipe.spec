# No debuginfo: pure-Python wheel, no ELF binaries.
%global debug_package %{nil}

Name:           python-yt-dlp-get-pot-rustypipe
Version:        0.2.0
Release:        5%{?dist}
Summary:        PO token provider plugin for yt-dlp using rustypipe-botguard

License:        MIT
URL:            https://pypi.org/project/yt-dlp-get-pot-rustypipe/
# pypi_source name 404s; use the underscore URL.
Source0:        https://files.pythonhosted.org/packages/source/y/yt-dlp-get-pot-rustypipe/yt_dlp_get_pot_rustypipe-%{version}.tar.gz
# The sdist ships no license file and PyPI metadata carries no author or
# project URL. The plugin itself lives in the rustypipe-botguard repo (tag
# yt-dlp-get-pot-rustypipe/v0.2.0), whose root LICENSE is this MIT text.
Source1:        https://codeberg.org/ThetaDev/rustypipe-botguard/raw/tag/yt-dlp-get-pot-rustypipe/v%{version}/LICENSE
# sha256: fc3908dc021285b75d2fb91464dcb03545d966b9011cc009f8a230f4ce468701

# Aliased name expected by dependent specs.
Provides:       python3-yt-dlp-get-pot-rustypipe

BuildRequires:  python3-devel

# Plugin shells out to rustypipe-botguard; Recommends only.
Recommends:     rustypipe-botguard

%description
yt-dlp-get-pot-rustypipe is a yt-dlp plugin that fetches PO tokens
via the rustypipe-botguard helper binary. Packaged for the Nexus
repository as a dependency of mixtapes.

%prep
# Unpack sdist so build-requires generation finds setup.py.
%autosetup -p1 -n yt_dlp_get_pot_rustypipe-%{version}
cp -p %{SOURCE1} LICENSE

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files yt_dlp_plugins

%files -f %{pyproject_files}
%license LICENSE

%changelog
* Tue Oct 20 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.0-5
- Ship the MIT license text: the sdist carries none, but the plugin lives in
  the rustypipe-botguard repo and its tag yt-dlp-get-pot-rustypipe/v0.2.0
  ships the LICENSE (Copyright (c) 2025 ThetaDev), so %license now has text

* Fri Oct 02 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.2.0-4
- Add Recommends: rustypipe-botguard (plugin shells out to that binary
  via PATH lookup; upstream yt_dlp_get_pot_rustypipe.py _BOTGUARD_BIN).
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.2.0-3
- Provide python3-yt-dlp-get-pot-rustypipe (name expected by mixtapes Requires;
  COPR mixtapes install failed on unresolvable python3-* names).
* Sun Sep 06 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.2.0-2
- Add missing %prep/%autosetup so %generate_buildrequires finds the
  sources (same failure as pydbus 10955044 / ytmusicapi 10955049).
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.0-1
- Initial package (dependency of mixtapes). Debuginfo disabled (pure-Python, no ELF).
