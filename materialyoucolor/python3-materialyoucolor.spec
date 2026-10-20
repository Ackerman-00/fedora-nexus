Name:           python3-materialyoucolor
Version:        3.0.4
Release:        1%{?dist}
Summary:        Material You color generation algorithms (pure Python + C++ quantizer)

License:        MIT
URL:            https://pypi.org/project/materialyoucolor/
Source0:        https://files.pythonhosted.org/packages/eb/23/2e63e7bdfcc1aa7ba955386ad09e3bd8a535a1092d7af501659b63cb6282/materialyoucolor-%{version}.tar.gz

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

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
* Sat Aug 08 2026 Ackerman-00 <quietcraft@gmail.com> - 3.0.4-1
- Initial package (builds the C++ quantizer via pybind11)
