Name:           awww
Version:        0.12.1
Release:        6%{?dist}
Summary:        Efficient animated wallpaper daemon for Wayland, controlled at runtime

License:        GPL-3.0-only AND MIT AND Apache-2.0 AND MPL-2.0 AND BSD-3-Clause AND ISC
URL:            https://codeberg.org/LGFae/awww
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
# sha256: 97b3f1c6d65d9d30e51b17092a45244f8c8549607c9207f3c98d82b28ba18fca

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc-c++
BuildRequires:  pkgconf
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  libxkbcommon-devel
# common/build.rs probes liblz4 with atleast_version("1.8") - carry the floor
BuildRequires:  pkgconfig(liblz4) >= 1.8
BuildRequires:  systemd-rpm-macros

%description
awww is an efficient animated wallpaper daemon for Wayland, with a client
for controlling it at runtime. It uses far less CPU than traditional
animated wallpaper tools by rendering each frame into a single shared
buffer, and it supports a large number of image formats as well as video
files.

%prep
%autosetup -n %{name}

%build
export CARGO_NET_OFFLINE=false
export RUSTFLAGS="%{build_rustflags}"
cargo build --release --locked

%install
install -Dpm 0755 target/release/awww %{buildroot}%{_bindir}/awww
install -Dpm 0755 target/release/awww-daemon %{buildroot}%{_bindir}/awww-daemon
install -Dpm 0644 contrib/systemd/awww-daemon.service %{buildroot}%{_userunitdir}/awww-daemon.service

%files
%license LICENSE
%doc README.md
%{_bindir}/awww
%{_bindir}/awww-daemon
%{_userunitdir}/awww-daemon.service

%changelog
* Fri Oct 23 2026 Ackerman-00 <quietcraft@gmail.com> - 0.12.1-6
- Fetch Source0 from the codeberg tag archive (HTTP 200, sha256 pinned)
  instead of shipping the tarball in git; the archive is byte-identical
  to the committed tarball (diff -rq clean) and extracts to awww/
* Mon Oct 19 2026 Ackerman-00 <quietcraft@gmail.com> - 0.12.1-5
- Ship the LICENSE and README.md the upstream tarball carries as
  %license/%doc; the package shipped binaries with no license text
* Wed Oct 14 2026 Ackerman-00 <quietcraft@gmail.com> - 0.12.1-4
- Replace lz4-devel with pkgconfig(liblz4) >= 1.8 to carry upstream's
  liblz4 1.8 minimum (common/build.rs pkg-config probe)

* Thu Aug 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.12.1-3
- Fix autosetup: tarball extracts to awww-0.12.1/, not awww/

* Thu Aug 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.12.1-2
- Add pkgconfig(wayland-protocols) BuildRequires: waybackend-scanner
  build-script needs pkg-config --variable=pkgdatadir wayland-protocols

* Thu Aug 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.12.1-1
- Use committed source tarball (codeberg archive endpoint down, HTTP 504/timeout)
- Initial package
