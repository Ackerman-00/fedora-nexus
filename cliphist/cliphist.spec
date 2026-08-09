# Disable debuginfo extraction (Go builds don't cooperate with the debugsource capture)
%global debug_package %{nil}

Name:           cliphist
Version:        0.7.0
Release:        1%{?dist}
Summary:        Wayland clipboard manager with support for multimedia

License:        BSD-3-Clause AND GPL-3.0-only AND MIT
URL:            https://github.com/sentriz/cliphist
Source0:        %{url}/archive/v%{version}/cliphist-v%{version}.tar.gz

BuildRequires:  golang >= 1.20
BuildRequires:  make

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

%files
%{_bindir}/cliphist

%changelog
* Sun Aug 09 2026 Ackerman-00 <quietcraft@gmail.com> - 0.7.0-1
- Initial package
