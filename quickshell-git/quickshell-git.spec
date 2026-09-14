# RETIRED — transitional stub (2026-09-14)
# quickshell-git has been retired from fedora-nexus (COPR ackerman/nexus)
# because Fedora now ships official 'quickshell' in F43/F44/F45/F46+.
# This stub exists only to notify existing users via `dnf update`
# and to pull the official package. It will be removed from the
# COPR ~2 weeks after 2026-09-14 (~2026-09-28), after which
# `quickshell-git` will disappear from the repo entirely.
# DO NOT run update.sh on this spec — Version 99.0 is intentional
# and must sort ABOVE all previous 0.3.1^git snapshots.

Name:           quickshell-git
Version:        99.0
Release:        1%{?dist}
Summary:        Transitional package — quickshell-git retired, use official quickshell
License:        LGPL-3.0-or-later and BSD-3-Clause and HPND-sell-variant
URL:            https://github.com/quickshell-mirror/quickshell
BuildArch:      noarch

Requires:       quickshell

%description
Transitional retirement package for quickshell-git.

quickshell-git from fedora-nexus (COPR ackerman/nexus) has been RETIRED.
Fedora now ships official 'quickshell' in every supported release:

  * Fedora 43:  quickshell 0.2.1-5.fc43
  * Fedora 44:  quickshell 0.2.1-5.fc44
  * Fedora 45:  quickshell 0.2.1-5.fc45
  * Fedora 46 / Rawhide: quickshell 0.2.1-5.fc46
  Maintainer: Fedora Qt/KDE SIG
  Sources: https://src.fedoraproject.org/rpms/quickshell

This empty package exists solely to make `dnf update` visible:
installing it pulls the official 'quickshell' and prints migration
instructions. After updating you can clean up the stub:

  sudo dnf remove quickshell-git          # leaves official quickshell installed
  # or
  sudo dnf swap quickshell-git quickshell

This stub will be removed from the COPR entirely after ~2026-09-28.
Please migrate now. Thank you for using fedora-nexus!

%prep
%build
%install

%post
cat >&2 <<'EOF'
========================================================================
  NOTICE: quickshell-git from COPR ackerman/nexus is RETIRED.

  Fedora now ships official 'quickshell' (F43/F44/F45/F46+):

    sudo dnf install quickshell
    # or if you already updated to this stub:
    sudo dnf remove quickshell-git   # official quickshell stays installed

  Details: https://src.fedoraproject.org/rpms/quickshell

  This stub (quickshell-git 99.0-1) will be deleted from the COPR
  after ~2026-09-28. Thanks for flying with fedora-nexus — ackerman
========================================================================
EOF

%files

%changelog
* Sun Sep 14 2026 Ackerman-00 <quietcraft@gmail.com> - 99.0-1
- RETIRED: quickshell-git moved to Fedora official 'quickshell' (F43/F44/F45/F46+). Transitional stub that Requires:quickshell and prints migration notice. Will be removed from COPR after ~2 weeks. Thank you!

* Mon Sep 14 2026 Ackerman-00 <quietcraft@gmail.com> - 0.3.1^20260914015902git86b4275-2
- Full SPDX License expression; ship LICENSE-GPL and contributor docs via glob
- Validate desktop file in %check; Provide notification-daemon and polkit-auth-agent

* Mon Sep 14 2026 Ackerman-00 <quietcraft@gmail.com> - 0.3.1^20260914015902git86b4275-1
- Nightly sync with upstream master branch (Commit: 86b4275)
