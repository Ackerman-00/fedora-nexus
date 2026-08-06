Name:           awww
Version:        0.12.1
Release:        3%{?dist}
Summary:        Efficient animated wallpaper daemon for Wayland, controlled at runtime

License:        GPL-3.0-only AND MIT AND Apache-2.0 AND MPL-2.0 AND BSD-3-Clause AND ISC
URL:            https://codeberg.org/LGFae/awww
Source0:        awww-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc-c++
BuildRequires:  pkgconf
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  libxkbcommon-devel
BuildRequires:  lz4-devel
BuildRequires:  systemd-rpm-macros

%description
awww is an efficient animated wallpaper daemon for Wayland, with a client
for controlling it at runtime. It uses far less CPU than traditional
animated wallpaper tools by rendering each frame into a single shared
buffer, and it supports a large number of image formats as well as video
files.

%prep
%autosetup -n awww-%{version}

%build
export CARGO_NET_OFFLINE=false
cargo build --release --locked

%install
install -Dpm 0755 target/release/awww %{buildroot}%{_bindir}/awww
install -Dpm 0755 target/release/awww-daemon %{buildroot}%{_bindir}/awww-daemon
install -Dpm 0644 contrib/systemd/awww-daemon.service %{buildroot}%{_userunitdir}/awww-daemon.service

%files
%{_bindir}/awww
%{_bindir}/awww-daemon
%{_userunitdir}/awww-daemon.service

%changelog
* Thu Aug 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.12.1-3
- Fix autosetup: tarball extracts to awww-0.12.1/, not awww/

* Thu Aug 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.12.1-2
- Add pkgconfig(wayland-protocols) BuildRequires: waybackend-scanner
  build-script needs pkg-config --variable=pkgdatadir wayland-protocols

* Thu Aug 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.12.1-1
- Use committed source tarball (codeberg archive endpoint down, HTTP 504/timeout)
- Initial package
