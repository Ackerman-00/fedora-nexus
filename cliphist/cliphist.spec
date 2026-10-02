# Disable debuginfo extraction (Go builds don't cooperate with the debugsource capture)
%global debug_package %{nil}

Name:           cliphist
Version:        0.7.0
Release:        3%{?dist}
Summary:        Wayland clipboard manager with support for multimedia

License:        BSD-3-Clause AND GPL-3.0-only AND MIT
URL:            https://github.com/sentriz/cliphist
Source0:        %{url}/archive/v%{version}/cliphist-v%{version}.tar.gz

BuildRequires:  golang >= 1.20

Requires:       wl-clipboard
Requires:       xdg-utils

%description
cliphist is a clipboard manager for Wayland with support for multimedia.
Clipboard history is stored in an embeddable database and can be searched,
pasted, and cleared both interactively (rofi/dmenu/fuzzel) and from the
command line. It is designed to be used together with a clipboard watcher
such as wl-paste --watch cliphist store.

%prep
%autosetup -n cliphist-%{version}

%build
go build -trimpath -ldflags="-s -w" -o cliphist .

%install
install -d %{buildroot}%{_bindir}
install -m 0755 cliphist %{buildroot}%{_bindir}/cliphist

%check
# Upstream ships cliphist_test.go plus testdata/; wire the suite in so a
# regression fails the build instead of reaching users.
#
# The suite must NOT run as root. testdata/no-permission.txtar does
# "chmod 111 $HOME" and then asserts that cliphist store fails with
# "permission denied" - which can never happen for uid 0.
#
# How to get off uid 0 depends on who owns the build:
#  - A plain "rpmbuild -bb" runs as root, so we must drop privileges. The
#    Go module cache then lives under /root, which the unprivileged user
#    cannot traverse, so run the suite from a copy under /tmp.
#  - mock - which is what COPR and koji use - already runs the whole build
#    as the unprivileged "mockbuild" user, so useradd is impossible there
#    and pointless: the suite is run in place. Getting this wrong made the
#    COPR build 11065113 fail with "su: user cliphist-check does not exist
#    or the user entry does not contain all the required fields".
export GO111MODULE=on
if [ "$(id -u)" -eq 0 ]; then
  useradd -r -m -d /tmp/cliphist-check cliphist-check
  rm -rf /tmp/cliphist-src
  cp -a %{_builddir}/cliphist-%{version} /tmp/cliphist-src
  chmod -R a+rX /tmp/cliphist-src
  su cliphist-check -s /bin/sh -c \
    "cd /tmp/cliphist-src && GO111MODULE=on go test -buildmode pie -compiler gc ./..."
else
  go test -buildmode pie -compiler gc ./...
fi

%files
%license LICENSE
%doc CHANGELOG.md readme.md version.txt
%{_bindir}/cliphist

%changelog
* Fri Oct 02 2026 Ackerman-00 <quietcraft@gmail.com> - 0.7.0-3
- Fix the check section in unprivileged builds. mock, and therefore COPR
  and koji, runs rpmbuild as the unprivileged "mockbuild" user, where the
  useradd plus su dance meant to step around the root-only no-permission
  testdata case cannot work; the suite now runs in place there and only
  drops privileges when the build really is running as uid 0.
- Drop the go-rpm-macros build requirement again. It was only ever there to
  define %gotest, and the check section now invokes the go tool directly, so
  nothing in this spec references a go-rpm macro any more.
* Fri Oct 02 2026 Ackerman-00 <quietcraft@gmail.com> - 0.7.0-2
- Ship the upstream license and documentation: the LICENSE file under the
  license directory plus CHANGELOG.md, readme.md and version.txt as docs.
  The package declared "BSD-3-Clause AND GPL-3.0-only AND MIT" but shipped
  no license file, and Fedora's own cliphist ships the same doc set.
- Drop the unused make build requirement. Upstream ships no Makefile and
  the build step runs the go toolchain directly, so nothing invoked make.
- Run the upstream test suite (cliphist_test.go with its testdata
  directory) in a check section, matching what Fedora's own cliphist does.
* Sun Aug 09 2026 Ackerman-00 <quietcraft@gmail.com> - 0.7.0-1
- Initial package
