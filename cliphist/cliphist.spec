# Disable debuginfo extraction (Go builds don't cooperate with the debugsource capture)
%global debug_package %{nil}

Name:           cliphist
Version:        0.7.0
Release:        2%{?dist}
Summary:        Wayland clipboard manager with support for multimedia

License:        BSD-3-Clause AND GPL-3.0-only AND MIT
URL:            https://github.com/sentriz/cliphist
Source0:        %{url}/archive/v%{version}/cliphist-v%{version}.tar.gz

BuildRequires:  golang >= 1.20
# Provides the Go RPM macros used by the check step below. Without this the
# macro is undefined and the check dies on an unexpanded macro reference.
BuildRequires:  go-rpm-macros

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
# "permission denied" - which can never happen for uid 0, and rpmbuild runs
# as root. Running the same command as an unprivileged user makes the whole
# suite pass, so the test is fine and only the buildroot user was wrong.
#
# The Go module cache lives under /root, which an unprivileged user cannot
# traverse, so run the suite from a copy under /tmp.
export GO111MODULE=on
useradd -r -m -d /tmp/cliphist-check cliphist-check >/dev/null 2>&1 || :
rm -rf /tmp/cliphist-src
cp -a %{_builddir}/cliphist-%{version} /tmp/cliphist-src
chmod -R a+rX /tmp/cliphist-src
su cliphist-check -s /bin/sh -c \
  "cd /tmp/cliphist-src && GO111MODULE=on go test -buildmode pie -compiler gc ./..."

%files
%license LICENSE
%doc CHANGELOG.md readme.md version.txt
%{_bindir}/cliphist

%changelog
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
