%global debug_package %{nil}
%global crate matugen

Name:           matugen
Version:        4.2.0
Release:        3%{?dist}
Summary:        Material You color generation tool (Nexus Optimized)

# Full license audit of vendors and core logic
License:        GPL-2.0-or-later AND MIT AND Apache-2.0 AND Zlib
URL:            https://github.com/InioX/matugen
Source0:        https://crates.io/api/v1/crates/%{crate}/%{version}/download#/%{crate}-%{version}.crate

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc-c++

%description
Matugen is a Material You color generation tool that supports templates.
Packaged exclusively for the Nexus repository. This version is compiled
natively from the official Rust crate for peak performance in Wayland
environments.

%prep
%setup -q -n %{crate}-%{version}

%build
# Set the linker to native
export CARGO_NET_OFFLINE=false
export RUSTFLAGS="%{build_rustflags}"
cargo build --release --locked

%install
install -Dpm0755 target/release/matugen -t %{buildroot}%{_bindir}/

%files
%license LICENSE
%{_bindir}/matugen

%changelog
* Tue Sep 08 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 4.2.0-3
- Wrap the package description to 80 columns (fixes rpmlint description-line-too-long)

* Tue Sep 08 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 4.2.0-2
- Add missing changelog entry for the 4.2.0 version bump (NVR unchanged,
  already built in COPR; spec-metadata fix only)

* Sun Aug 02 2026 Ackerman-00 <quietcraft@gmail.com> - 4.1.0-2
- Drop dead BuildRequires pkgconfig(openssl) (no openssl crate in Cargo.lock;
  matugen uses rustls for TLS)

* Sun Aug 02 2026 Ackerman-00 <quietcraft@gmail.com> - 4.1.0-1
- Update to version 4.1.0

* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 2.4.1-1
- Initial Optimized Native Rust Build for Nexus Repository
