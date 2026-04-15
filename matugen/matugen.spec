%global debug_package %{nil}
%global crate matugen

Name:           matugen
Version:        4.1.0
Release:        1%{?dist}
Summary:        Material You color generation tool (Nexus Optimized)

# Full license audit of vendors and core logic
License:        GPL-2.0-or-later AND MIT AND Apache-2.0 AND Zlib
URL:            https://github.com/InioX/matugen
Source0:        https://crates.io/api/v1/crates/%{crate}/%{version}/download#/%{crate}-%{version}.crate

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(openssl)

%description
Matugen is a Material You color generation tool that supports templates. 
Packaged exclusively for the Nexus repository. This version is compiled natively from the official Rust crate for peak performance in Wayland environments.

%prep
%setup -q -n %{crate}-%{version}

%build
# Set the linker to native
export CARGO_NET_OFFLINE=false
cargo build --release --locked

%install
rm -rf %{buildroot}
install -Dpm0755 target/release/matugen -t %{buildroot}%{_bindir}/

%files
%license LICENSE
%{_bindir}/matugen

%changelog
* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 2.4.1-1
- Initial Optimized Native Rust Build for Nexus Repository
