# Research: fluxer desktop icon missing

Scope: why the installed fluxer package shows no icon. Primary sources fetched live 2026-10-04.
Read-only: downloaded RPM to /tmp only, repo tree untouched, nothing committed, nothing built.

## 1. update.sh version derivation and Source0

`fluxer/update.sh` lines 5, 9-32: `API_URL="https://api.fluxer.app/dl/desktop/stable/linux/x64/latest/rpm"`.
It reads the `X-Fluxer-Version` response header first, then the `Content-Disposition` filename
(`grep -oP 'Fluxer-\K[0-9.]+'`), and when they disagree it prefers the filename
(lines 13-17: "filename is authoritative when header lags"; lines 19-22 comment: "never trust it over the filename").
Spec `fluxer.spec:23` `Source0:` uses the same rolling `.../latest/rpm` URL.

Live probe today (`curl -sIL -A "Mozilla/5.0" <API_URL>`):

```
location: https://pkgs.fluxer.com/desktop/stable/linux/x64/latest/rpm
x-fluxer-version: 2026.1004.150143
HTTP/2 200
content-disposition: attachment; filename="Fluxer-2026.1004.13532-linux-x86_64.rpm"
```

Note the header (`2026.1004.150143`) leads the filename (`2026.1004.13532`) — exactly the lag/lead case
update.sh already handles. Served RPM sha256 (`curl -sL | sha256sum`) equals the pinned
`fluxer.spec:26` hash `af664e0f...822d2`, so the spec's current bits are still today's artifact.
RPM metadata (`rpm -qpi`): `Name: fluxer`, `Version: 2026.1004.13532`, `Release: 1`.

## 2. Real contents of the served RPM (extracted to /tmp)

`rpm -qlp /tmp/fluxer.rpm` filtered to desktop/icon/opt top level:

```
/opt/Fluxer/chrome-sandbox
/opt/Fluxer/fluxer
/opt/Fluxer/fluxer-launcher
/opt/Fluxer/fluxer_desktop
/usr/share/applications/app.fluxer.FluxerDesktop.desktop
/usr/share/icons/hicolor/1024x1024/apps/fluxer.png
```

Plus `/opt/Fluxer/resources/icons/{16x16,24x24,32x32,48x48,64x64,128x128,256x256,512x512,1024? ->
actually}/...` set (`16x16.png ... 512x512.png`, `icon.png`, `icon.ico`) and
`resources/badges/*.ico`. Binary: `/opt/Fluxer/fluxer` (stable name, no `fluxer-canary`), launcher
`/opt/Fluxer/fluxer-launcher`. `chrome-sandbox` present.

Two things the spec does NOT expect anymore:

1. Desktop file is **renamed**: upstream now ships `app.fluxer.FluxerDesktop.desktop`
   (was `fluxer.desktop` / `fluxer-canary.desktop`). Its content:
   `Exec=/opt/Fluxer/fluxer-launcher %U`, `Icon=fluxer`, `StartupWMClass=app.fluxer.FluxerDesktop`.
2. Icon set collapsed to **one** file: `usr/share/icons/hicolor/1024x1024/apps/fluxer.png`
   (no more per-size hicolor set under standard sizes).

## 3. Spec assumptions vs reality — the exact breaks

`fluxer.spec`:
- L51-59 normalizes `opt/Fluxer Canary`/`opt/fluxer-canary`/`opt/fluxer` → `opt/Fluxer` (fine, already `opt/Fluxer`).
- L60-62 only copies `fluxer-canary.desktop` → `fluxer.desktop`. It does NOT handle
  `app.fluxer.FluxerDesktop.desktop`. So after %prep there is **no**
  `usr/share/applications/fluxer.desktop`.
- L85 then runs `install -Dm0644 usr/share/applications/fluxer.desktop ...` → **file missing; the spec
  as written cannot install against today's artifact** (build error). Any icon regression in the
  installed package traces to the same drift era.
- Icon glob L95 `usr/share/icons/hicolor/*/apps/fluxer.png` still matches the single shipped file, and
  L98 installs it to `%{_datadir}/icons/hicolor/1024x1024/apps/%{appid}.png`. But `1024x1024` is **not a
  declared group** in hicolor's index.theme: `grep -E '^\[' /usr/share/icons/hicolor/index.theme`
  lists 16,22,24,32,36,48,64,72,96,128,192,256,512,scalable,symbolic only. Icon-theme lookup therefore
  skips that bucket, so `Icon=app.fluxer.Fluxer` (set by L91) resolves to **no icon at runtime** — the
  exact reported symptom.
- L86 installs the desktop file as `%{_datadir}/applications/app.fluxer.Fluxer.desktop` while the
  upstream `StartupWMClass=app.fluxer.FluxerDesktop` no longer matches the desktop-file basename
  (`app.fluxer.Fluxer`), so WM window↔entry matching (and thus window icon) is also broken.

Root cause: upstream renamed the desktop file (`app.fluxer.FluxerDesktop.desktop`), collapsed the
hicolor icon set to a single `1024x1024` png, and the spec still assumes `fluxer.desktop` plus a
multi-size standard hicolor set.

## 4. Upstream notes

`https://fluxer.app` returns HTTP 200 (fetched 2026-10-04); no public changelog entry found announcing
the rename, so treat the served RPM layout as the authority.

## Minimal fix (described, NOT applied)

In `%prep`, also accept the new name: `if [ -f usr/share/applications/app.fluxer.FluxerDesktop.desktop ]`,
copy it to `usr/share/applications/fluxer.desktop` (or use it directly in %install). In %install,
keep `StartupWMClass` and the desktop-file basename aligned (either name the file
`app.fluxer.FluxerDesktop.desktop` or rewrite the `StartupWMClass=` line). For the icon, ship it under
a real hicolor size dir: copy `resources/icons/icon.png` (or the 1024 png, downscaled) into
`usr/share/icons/hicolor/512x512/apps/%{appid}.png` (or several standard sizes), instead of
blindly preserving the `1024x1024` bucket that hicolor's index.theme does not declare.
