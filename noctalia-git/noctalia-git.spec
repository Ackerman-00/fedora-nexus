# RETIRED — transitional stub (2026-09-14)
# noctalia-git has been retired from fedora-nexus (COPR ackerman/nexus)
# because Fedora now ships official 'noctalia' (F44+).
# This stub exists only to notify existing users via `dnf update`
# and to pull the official package. It will be removed from the
# COPR ~2 weeks after 2026-09-14 (~2026-09-28), after which
# `noctalia-git` will disappear from the repo entirely.
# DO NOT run update.sh on this spec — Version 99.0 is intentional
# and must sort ABOVE all previous 5.1.0^git snapshots.

Name:           noctalia-git
Version:        99.0
Release:        1%{?dist}
Summary:        Transitional package — noctalia-git retired, use official noctalia
License:        MIT
URL:            https://github.com/noctalia-dev/noctalia
BuildArch:      noarch

Requires:       noctalia

%description
Transitional retirement package for noctalia-git.

noctalia-git from fedora-nexus (COPR ackerman/nexus) has been RETIRED.
Fedora now ships official 'noctalia' from the default repositories
(Fedora 44 and newer):

  * Fedora 44 updates: noctalia 5.0.0~beta.10-1.fc44
  * Fedora 45 base:    noctalia 5.0.0~beta.9-1.fc45
  Docs: https://docs.noctalia.dev/noctalia/getting-started/installation?section=fedora
  Sources: https://src.fedoraproject.org/rpms/noctalia

This empty package exists solely to make `dnf update` visible:
installing it pulls the official 'noctalia' and prints migration
instructions. After updating you can clean up the stub:

  sudo dnf remove noctalia-git          # leaves official noctalia installed
  # or
  sudo dnf swap noctalia-git noctalia

NOTE for Fedora 43 users: official 'noctalia' is only in F44+.
Please upgrade to F44 or newer (`sudo dnf system-upgrade`) to use
the official package, or temporarily keep the last noctalia-git build
until you upgrade. This stub will still print the notice on F43 but
its Requires: noctalia will not resolve until you are on F44+.

This stub will be removed from the COPR entirely after ~2026-09-28.
Please migrate now. Thank you for using fedora-nexus!

%prep
%build
%install

%post
cat >&2 <<'EOF'
========================================================================
  NOTICE: noctalia-git from COPR ackerman/nexus is RETIRED.

  Fedora now ships official 'noctalia' (F44+):

    sudo dnf install noctalia
    # or if you already updated to this stub:
    sudo dnf remove noctalia-git   # official noctalia stays installed

  F43 users: official noctalia needs F44+. Please upgrade your
  Fedora release to get it.

  Details: https://docs.noctalia.dev/noctalia/getting-started/installation?section=fedora
           https://src.fedoraproject.org/rpms/noctalia

  This stub (noctalia-git 99.0-1) will be deleted from the COPR
  after ~2026-09-28. Thanks for flying with fedora-nexus — ackerman
========================================================================
EOF

%files

%changelog
* Sun Sep 14 2026 Ackerman-00 <quietcraft@gmail.com> - 99.0-1
- RETIRED: noctalia-git moved to Fedora official 'noctalia' (F44+, docs.noctalia.dev). Transitional stub that Requires:noctalia and prints migration notice. Will be removed from COPR after ~2 weeks. Thank you!

* Mon Sep 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.1.0^20260914000849git5d66d11-3
- Drop dbus-daemon BR: the dbus-gated upower integration test segfaults in mock (COPR 10982843); 118/118 remaining tests green
- Add Requires pipewire (segfault at startup without daemon, per official spec)

* Mon Sep 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.1.0^20260914000849git5d66d11-2
- Add upstream-required cairo-ft, pangocairo, pangoft2, gobject-2.0 and gio-2.0 BuildRequires
- Run the headless-safe test suite (%%meson -Dtests=enabled + %%meson_test); add dbus-daemon so the upower test runs
- Ship shell completions; scrub template script shebangs; full SPDX License; bundled() Provides
- Requires git-core (plugins spawn git); Recommends upower (UPower bus) alongside power-profiles-daemon

* Mon Sep 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.1.0^20260914000849git5d66d11-1
- Nightly sync with upstream main branch (Commit: 5d66d11)
