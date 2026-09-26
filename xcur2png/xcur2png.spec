Name:           xcur2png
Version:        0.7.1
Release:        1%{?dist}
Summary:        Convert X cursor files into PNG images
License:        GPL-3.0-or-later
URL:            https://github.com/eworm-de/xcur2png
Source:         %{url}/releases/download/%{version}/%{name}-%{version}.tar.gz
# sha256: bc6a062fdb48615a7159ed56ef3d2011168cd8a9decaf1d8a4e316d3064132c9
Packager:       Ackerman-00 <quietcraft@gmail.com>

# C23 (GCC 15+, Fedora 44+) rejects the K&R-style "extern dry_run;" - implicit
# int is a hard error, upstream last touched this file in 2017.
Patch:          c23-extern-int.patch

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(xcursor)

%description
xcur2png converts X cursor files (.cur) into PNG images and writes the
xcursorgen-style configuration file needed to reassemble them.

It is the runtime helper that hyprcursor-util --extract shells out to: without
it, "hyprcursor-util -x" reports "missing dependency: -x requires xcur2png".
Not packaged in Fedora before this (packages.fedoraproject.org 404).

%prep
%autosetup

%build
%configure
%make_build

%install
%make_install

%check
# No upstream test suite. Smoke-test the exact probe hyprcursor-util performs:
# it spawns "xcur2png --help 2>&1" and requires the output to contain
# "xcursor" before it will run the -x extraction path.
./xcur2png --help 2>&1 | grep -qi xcursor

%files
%license COPYING
%doc README AUTHORS ChangeLog NEWS
%{_bindir}/xcur2png
%{_mandir}/man1/xcur2png.1*

%changelog
* Sat Sep 26 2026 Ackerman-00 <quietcraft@gmail.com> - 0.7.1-1
- Initial packaging for Fedora Nexus (Nexus Optimized)
- Runtime helper for hyprcursor-util -x, which greps "xcur2png --help" for
  "xcursor" and refuses to extract XCursor themes when it is absent
- Source is the re-hosted original upstream tarball (tag 0.7.1) from
  eworm-de/xcur2png, sha256 pinned above
- c23-extern-int.patch: declare "extern int dry_run" explicitly - C23 makes
  implicit int a hard error, so unpatched 0.7.1 does not compile on
  GCC 15+ (Fedora 44/45/rawhide)
