Name:           hyprnome
Version:        0.3.1
Release:        1%{?dist}
Summary:        GNOME-like workspace switching in Hyprland

License:        GPL-3.0-or-later AND MIT AND Apache-2.0 AND Zlib AND BSD-2-Clause AND ISC
URL:            https://github.com/donovanglover/hyprnome
Source:         %{url}/archive/%{version}/%{name}-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc-c++

%description
GNOME-like workspace switching in Hyprland.

%prep
%autosetup -p1

%build
export CARGO_NET_OFFLINE=false
cargo build --release --locked

%install
install -Dpm 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}

%changelog
* Mon Aug 17 2026 Ackerman-00 <quietcraft@gmail.com> - 0.3.1-1
- Initial package