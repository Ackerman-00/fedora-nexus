%global crate zed
%global appid dev.zed.Zed

Name:           zed
Version:        1.19.1
Release:        1%{?dist}
Summary:        Zed is a high-performance, multiplayer code editor
SourceLicense:  Apache-2.0 AND GPL-3.0-or-later
License:        ((Apache-2.0 OR MIT) AND BSD-3-Clause) AND ((MIT OR Apache-2.0) AND Unicode-3.0) AND (0BSD OR MIT OR Apache-2.0) AND (Apache-2.0 AND ISC) AND AGPL-3.0-only AND AGPL-3.0-or-later AND (Apache-2.0 OR BSL-1.0 OR MIT) AND (Apache-2.0 OR BSL-1.0) AND (Apache-2.0 OR ISC OR MIT) AND (Apache-2.0 OR MIT) AND (Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT) AND (Apache-2.0 WITH LLVM-exception) AND Apache-2.0 AND (BSD-2-Clause OR Apache-2.0 OR MIT) AND (BSD-2-Clause OR MIT OR Apache-2.0) AND BSD-2-Clause AND (CC0-1.0 OR Apache-2.0 OR Apache-2.0 WITH LLVM-exception) AND (CC0-1.0 OR Apache-2.0) AND (CC0-1.0 OR MIT-0 OR Apache-2.0) AND CC0-1.0 AND GPL-3.0-or-later AND (ISC AND (Apache-2.0 OR ISC) AND OpenSSL) AND (ISC AND (Apache-2.0 OR ISC)) AND ISC AND (MIT AND (MIT OR Apache-2.0)) AND (MIT AND BSD-3-Clause) AND (MIT OR Apache-2.0 OR CC0-1.0) AND (MIT OR Apache-2.0 OR NCSA) AND (MIT OR Apache-2.0 OR Zlib) AND (MIT OR Apache-2.0) AND (MIT OR Zlib OR Apache-2.0) AND MIT AND MPL-2.0 AND Unicode-3.0 AND (Unlicense OR MIT) AND (Zlib OR Apache-2.0 OR MIT) AND Zlib
# Dep-license audit: Terra zed.spec verbatim, except their "AGPL.3.0-only"
# typo corrected to AGPL-3.0-only.
# License audit adapted from Terra's zed.spec (same upstream sources).
URL:            https://zed.dev/
Source0:        https://github.com/zed-industries/zed/archive/refs/tags/v%{version}.tar.gz

ExclusiveArch:  x86_64
# aarch64 needs lld for the vendored WebRTC link (upstream .cargo/config);
# unverified on COPR, so x86_64 only for now.

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  clang
BuildRequires:  mold
BuildRequires:  cmake
BuildRequires:  gettext-envsubst
BuildRequires:  perl-FindBin
BuildRequires:  perl-IPC-Cmd
BuildRequires:  perl-File-Compare
BuildRequires:  perl-File-Copy
BuildRequires:  perl-lib
BuildRequires:  alsa-lib-devel
BuildRequires:  fontconfig-devel
BuildRequires:  wayland-devel
BuildRequires:  libxkbcommon-x11-devel
BuildRequires:  openssl-devel
BuildRequires:  libzstd-devel
BuildRequires:  vulkan-loader
BuildRequires:  libcurl-devel

Requires:       hicolor-icon-theme

%description
Code at the speed of thought - Zed is a high-performance, multiplayer code
editor from the creators of Atom and Tree-sitter.

%prep
%autosetup -n %{crate}-%{version} -p1

export DO_STARTUP_NOTIFY="true"
export APP_ID="%appid"
export APP_ICON="%appid"
export APP_NAME="Zed"
export APP_CLI="zed"
export APP="%{_libexecdir}/zed-editor"
export APP_ARGS="%U"
export ZED_UPDATE_EXPLANATION="Run dnf upgrade to update Zed from fedora-nexus."
export ZED_RELEASE_CHANNEL=stable
export BRANDING_LIGHT="#e9aa6a"
export BRANDING_DARK="#1a5fb4"

envsubst < "crates/zed/resources/zed.desktop.in" > %{appid}.desktop
sed -i "s|@release_info@||g" "crates/zed/resources/flatpak/zed.metainfo.xml.in"
envsubst < "crates/zed/resources/flatpak/zed.metainfo.xml.in" > %{appid}.metainfo.xml

%build
export ZED_UPDATE_EXPLANATION="Run dnf upgrade to update Zed from fedora-nexus."
echo "stable" > crates/zed/RELEASE_CHANNEL

# Upstream pins Rust 1.97.1; Fedora 44 ships newer (verified at packaging).
# Upstream + Terra build with clang/mold; mirror that here.
export CC=clang
export CXX=clang++
# Fedora-tuned Rust flags. NOTE: debuginfo deliberately off (like Terra):
# a full-debug Zed binary is enormous and COPR-unfriendly.
export RUSTFLAGS="%{build_rustflags} -Cdebuginfo=0 -Clink-arg=-fuse-ld=mold"
cargo build --release --locked --package zed --package cli
ALLOW_MISSING_LICENSES=1 script/generate-licenses
# RUSTC_BOOTSTRAP unlocks the -Z flag below on stable cargo (Terra does the
# same via its macros); the build itself needs no nightly features.
RUSTC_BOOTSTRAP=1 cargo tree \
    -Z avoid-dev-deps \
    --workspace \
    --edges no-build,no-dev,no-proc-macro \
    --target all \
    --prefix none \
    --format "{l}: {p}" \
    | sed -e "s: ($(pwd)[^)]*)::g" -e "s: / :/:g" -e "/\/.*:/{s/\// OR /}" \
    | sed -e '/.*(\*).*/d' -e '/^: pet/ s/./MIT&/' \
    | sort -u \
> LICENSE.dependencies

%install
install -Dm755 target/release/zed %{buildroot}%{_libexecdir}/zed-editor
install -Dm755 target/release/cli %{buildroot}%{_bindir}/zed

install -Dm644 %appid.desktop %{buildroot}%{_datadir}/applications/%appid.desktop
install -Dm644 crates/zed/resources/app-icon.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/%appid.png
install -Dm644 %appid.metainfo.xml %{buildroot}%{_metainfodir}/%appid.metainfo.xml

mv assets/icons/LICENSES LICENSE.icons
mv assets/themes/LICENSES LICENSE.themes
mv assets/fonts/ibm-plex-sans/license.txt LICENSE.fonts

%files
%doc CODE_OF_CONDUCT.md
%doc README.md
%license LICENSE-APACHE
%license LICENSE-GPL
%license LICENSE.dependencies
%license assets/licenses.md
%license LICENSE.fonts
%license LICENSE.icons
%license LICENSE.themes
%{_libexecdir}/zed-editor
%{_bindir}/zed
%{_datadir}/icons/hicolor/512x512/apps/%appid.png
%{_datadir}/applications/%appid.desktop
%{_metainfodir}/%appid.metainfo.xml

%changelog
* Wed Sep 09 2026 Ackerman-00 <quietcraft@gmail.com> - 1.19.1-1
- Auto-update to upstream stable release v1.19.1
