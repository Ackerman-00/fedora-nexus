# RETIRED — transitional stub (2026-09-14)
# niri-git has been retired from fedora-nexus (COPR ackerman/nexus)
# because Fedora now ships official 'niri' in F43/F44/F45/Rawhide.
# This stub exists only to notify existing users via `dnf update`
# and to pull the official package. It will be removed from the
# COPR ~2 weeks after 2026-09-14 (~2026-09-28), after which
# `niri-git` will disappear from the repo entirely.
# DO NOT run update.sh on this spec — Version 99.0 is intentional
# and must sort ABOVE all previous 26.04^git snapshots (Epoch 1).

Name:           niri-git
Epoch:          1
Version:        99.0
Release:        1%{?dist}
Summary:        Transitional package — niri-git retired, use official niri
License:        MIT
URL:            https://github.com/niri-wm/niri
BuildArch:      noarch

Requires:       niri

%description
Transitional retirement package for niri-git.

niri-git from fedora-nexus (COPR ackerman/nexus) has been RETIRED.
Fedora now ships official 'niri' in every supported release:

  * Fedora 43 updates:  niri 26.04-1.fc43
  * Fedora 44 updates:  niri 26.04-1.fc44
  * Fedora 45 / Rawhide: niri 26.04-2.fc45
  Maintainer: decathorpe — https://packages.fedoraproject.org/pkgs/niri/niri
  Sources:    https://src.fedoraproject.org/rpms/niri

This empty package exists solely to make `dnf update` visible:
installing it pulls the official 'niri' and prints migration
instructions. After updating you can clean up the stub:

  sudo dnf remove niri-git          # leaves official niri installed
  # or
  sudo dnf swap niri-git niri

This stub will be removed from the COPR entirely after ~2026-09-28.
Please migrate now. Thank you for using fedora-nexus!

%prep
%build
%install

%post
cat >&2 <<'EOF'
========================================================================
  NOTICE: niri-git from COPR ackerman/nexus is RETIRED.

  Fedora now ships official 'niri' (F43/F44/F45/Rawhide):

    sudo dnf install niri
    # or if you already updated to this stub:
    sudo dnf remove niri-git   # official niri stays installed

  Details: https://packages.fedoraproject.org/pkgs/niri/niri
           https://src.fedoraproject.org/rpms/niri

  This stub (niri-git 1:99.0-1) will be deleted from the COPR
  after ~2026-09-28. Thanks for flying with fedora-nexus — ackerman
========================================================================
EOF

%files

%changelog
* Sun Sep 14 2026 Ackerman-00 <quietcraft@gmail.com> - 1:99.0-1
- RETIRED: niri-git moved to Fedora official 'niri' (F43/F44/F45/Rawhide, decathorpe). Transitional stub that Requires:niri and prints migration notice. Will be removed from COPR after ~2 weeks. Thank you!

* Mon Sep 14 2026 Ackerman-00 <quietcraft@gmail.com> - 1:26.04^20260913141508git66d04a7-3
- Add explicit cairo, libspa-0.2 and wayland-cursor BuildRequires (lock-proven, previously transitive-only)
- Run unit tests in %%check (thread-limited, same scope as Fedora official); ship %%doc docs/wiki

* Mon Sep 14 2026 Ackerman-00 <quietcraft@gmail.com> - 1:26.04^20260913141508git66d04a7-2
- Canonical upstream URL niri-wm/niri (repo moved from YaLTeR/niri); document permanent Epoch 1
- Mark niri-portals.conf %%config(noreplace)

* Sun Sep 13 2026 Ackerman-00 <quietcraft@gmail.com> - 1:26.04^20260913141508git66d04a7-1
- Nightly sync with upstream main branch (Commit: 66d04a7)
