%global commit          60c51152e040303d6429b13cd22b5d2528098dba
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261030124748
%global base_version    0.2.6

Name:           otr-git
Version:        %{base_version}+git%{gitdate}.%{shortcommit}
Release:        1%{?dist}
Summary:        The Otr programming language toolchain

License:        MIT
URL:            https://git.pika-os.com/general-packages/otr
Source0:        https://git.pika-os.com/api/v1/repos/general-packages/otr/archive/%{commit}.tar.gz#/%{commit}.tar.gz
# sha256: a1e227aa3e576b5fa1ef9cf372cc87b569501ddf6914f0ffd43399f62fa6c67a

ExclusiveArch:  x86_64

BuildRequires:  curl
BuildRequires:  ca-certificates
BuildRequires:  xz
BuildRequires:  python3
BuildRequires:  tar

%description
Self-contained toolchain for the Otr language: the compiler and language
server, the standard library, a bundled clang toolchain, the TPDE fast
backend and the mold linker. Compiled from the git snapshot for the
Nexus repository.

%prep
tar -xzf %{SOURCE0}
%build
sh tools/bootstrap.sh > /tmp/otr-boot-path
OTR_BOOT=$(cat /tmp/otr-boot-path)
"$OTR_BOOT" run build.otr -- install --out out --boot "$OTR_BOOT"
out/bin/otr version | grep -qx "otr %{base_version}"

%install
install -d -m 0755 %{buildroot}%{_libdir}/otr/bin %{buildroot}%{_libdir}/otr/lib %{buildroot}%{_libdir}/otr/libexec/otr %{buildroot}%{_bindir}
cp -a out/bin/otr %{buildroot}%{_libdir}/otr/bin/
cp -a out/lib/libotr-tpde.so out/lib/otr %{buildroot}%{_libdir}/otr/lib/
cp -a out/libexec/otr/mold %{buildroot}%{_libdir}/otr/libexec/otr/
echo "otr v%{base_version}" > %{buildroot}%{_libdir}/otr/COMMIT
mkdir -p %{buildroot}%{_bindir}
ln -s $(realpath --relative-to=%{buildroot}%{_bindir} %{buildroot}%{_libdir}/otr/bin/otr) %{buildroot}%{_bindir}/otr

%files
%license LICENSE
%doc README.md
%{_bindir}/otr
%{_libdir}/otr/

%changelog
* Mon Nov 16 2026 Ackerman-00 <no-reply> - 0.2.6+git20261030124748.60c5115-1
- Initial package, built from git snapshot
