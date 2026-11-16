%global goipath         github.com/nwg-piotr/nwg-look

Version:        1.2.1

%gometa

Name:           nwg-look
Release:        6%{?dist}
Summary:        GTK3 settings editor for Wayland compositors

License:        MIT

URL:            https://github.com/nwg-piotr/nwg-look
Source0:        %{gosource}

BuildRequires:  golang >= 1.26
BuildRequires:  make
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  pkgconfig(gdk-3.0)
BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(cairo-gobject)

Requires:       gtk3

%description
nwg-look is a GTK3 settings editor for Wayland compositors.
Built for the Nexus repository with optimized Go macros.

%prep
%goprep
%autopatch -p1

%build
make build

%install

%make_install

# menu Icon= must resolve through an icon theme, not only the legacy pixmap path
install -Dpm0644 %{buildroot}%{_datadir}/pixmaps/nwg-look.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/nwg-look.svg

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

%files
%license LICENSE
%doc README.md
%{_bindir}/nwg-look
%{_datadir}/applications/nwg-look.desktop
%{_datadir}/nwg-look/
%{_datadir}/pixmaps/nwg-look.svg
%{_datadir}/icons/hicolor/scalable/apps/nwg-look.svg

%changelog
* Mon Nov 16 2026 Ackerman-00 <no-reply> - 1.2.1-6
- Rebuild for every chroot: the newest build targeted only fedora-43 and
  fedora-44, so fedora-45 and rawhide still served 1.2.1-3, which predates
  the hicolor icon that makes the menu entry's Icon= resolve

* Mon Nov 16 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.2.1-5
- Bring the built RPM to 0 rpmlint errors: shorten Summary, wrap
  %description to 79 columns, drop the explicit glib2 Requires
  (explicit-lib-dependency; soname Requires cover it), drop "natively"
  from the text, and keep both flagged words out of Summary and
  %description instead of filtering them

* Sun Nov 16 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.2.1-4
- Ship the app icon into hicolor/scalable/apps as well as pixmaps: the .desktop
  declares Icon=nwg-look, and panels that read only icon themes showed no icon
  (tools/desktop-sweep.sh counted 1014 theme icons and none named nwg-look)

* Sat Nov 14 2026 Ackerman-00 <no-reply> - 1.2.1-3
- Move the in-app updater strip into %install

* Thu Oct 22 2026 Ackerman-00 <no-reply> - 1.2.1-2
- Floor golang at 1.26, the version go.mod declares
* Wed Oct 14 2026 Nexus Auto-Updater <bot@github.com> - 1.2.1-1
- Update to version 1.2.1

* Mon Oct 12 2026 Nexus Auto-Updater <bot@github.com> - 1.2.0-1
- Update to version 1.2.0

* Tue Sep 29 2026 Nexus Auto-Updater <bot@github.com> - 1.1.2-1
- Update to version 1.1.2

* Tue Sep 01 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.1.1-3
- Fix build: restore %gometa macro removed in error (SRPM build failed)

* Sun Aug 02 2026 Ackerman-00 <no-reply> - 1.1.1-2
- Drop dead Recommends on xcur2png, which is not packaged in Fedora

* Sun Aug 02 2026 Ackerman-00 <no-reply> - 1.1.1-1
- Update to version 1.1.1

* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 1.0.6-1
- Initial Optimized Native Go Build
