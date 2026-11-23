Name:           python3-materialyoucolor
Version:        3.1.0
Release:        1%{?dist}
Summary:        Material You color generation algorithms (pure Python + C++ quantizer)

License:        MIT
URL:            https://pypi.org/project/materialyoucolor/
# sha256: da40c508080460a26a591ad814692c8f862e2971c9216a1feadae73d8ca258c4
Source0:        https://files.pythonhosted.org/packages/59/8e/9f4cba4a77c7ffb50c6af8b618fcf1a7a300e3b3c7500d9b74025ebdee48/materialyoucolor-3.1.0.tar.gz

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  gcc-c++
BuildRequires:  python3-pybind11
BuildRequires:  pybind11-devel
BuildRequires:  python3-build
BuildRequires:  python3-pip
BuildRequires:  python3-installer
BuildRequires:  python3-wheel
BuildRequires:  python3-setuptools

Requires:       python3-pillow

%description
Material You color generation algorithms in Python. Used by caelestia-cli-mango
for generating dynamic color schemes from wallpapers. The quantizer is a C++
pybind11 extension for speed, with a pure-Python fallback.

%prep
%autosetup -n materialyoucolor-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files materialyoucolor

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
* Mon Nov 23 2026 Ackerman-00 <no-reply> - 3.1.0-1
- Auto-update to upstream PyPI release 3.1.0
