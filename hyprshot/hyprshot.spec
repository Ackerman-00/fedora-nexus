Name:           hyprshot
Version:        1.3.0
Release:        2%{?dist}
Summary:        Utility to easily take screenshots in Hyprland using your mouse
BuildArch:      noarch

License:        GPL-3.0-only
URL:            https://github.com/Gustash/Hyprshot
Source0:        %{url}/archive/%{version}/%{name}-%{version}.tar.gz

Requires:       jq grim slurp wl-clipboard /usr/bin/notify-send /usr/bin/getopt
Recommends:     hyprpicker

%description
Hyprshot is an utility to easily take screenshot in Hyprland using your mouse.
It allows taking screenshots of windows, regions and monitors which are saved
to a folder of your choosing and copied to your clipboard.

%prep
%autosetup -n Hyprshot-%{version}

%build

%install
install -Dpm0755 %{name} -t %{buildroot}/%{_bindir}

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}

%changelog
* Thu Aug 20 2026 Ackerman-00 <quietcraft@gmail.com> - 1.3.0-2
- Add Requires /usr/bin/getopt (util-linux): the hyprshot script invokes getopt
  at runtime for argument parsing; without it the smoke test fails with
  "getopt: command not found". Release bumped 1 -> 2.

* Mon Aug 17 2026 Ackerman-00 <quietcraft@gmail.com> - 1.3.0-1
- Initial package