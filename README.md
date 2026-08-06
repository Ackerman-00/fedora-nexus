<div align="center">

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Fedora_logo.svg/330px-Fedora_logo.svg.png?_=20091128031656" width="80" />

<h1>fedora-nexus</h1>

<p>A self-updating RPM repository for Fedora, powered by COPR.</p>

[![Build](https://img.shields.io/github/actions/workflow/status/Ackerman-00/fedora-nexus/update-engine.yml?style=for-the-badge&label=AUTO-UPDATE&logo=github&logoColor=white)](https://github.com/Ackerman-00/fedora-nexus/actions)
&nbsp;
[![COPR](https://img.shields.io/badge/COPR-ackerman/nexus-0055CC?style=for-the-badge&logo=fedora)](https://copr.fedorainfracloud.org/coprs/ackerman/nexus/)

<p><sup>Recipes live in this repo · Built on COPR · Drop-in native RPM repo</sup></p>

</div>

---

## ⚡ Quick Setup

**① Enable the repository**

```bash
sudo dnf copr enable ackerman/nexus
```

**② Install a package**

```bash
sudo dnf install <package-name>
```

---

## 📦 Packages

<details>
<summary>Click to expand — 54 packages</summary>

<br />

| Package | Description | Type |
|---------|-------------|:----:|
| `app2unit` | Launch desktop entries or commands as systemd user units | Stable |
| `aquamarine` | Light-weight rendering backend library for Hyprland | Stable |
| `awww` | Efficient animated wallpaper daemon for Wayland, controlled at runtime | Stable |
| `bibata-cursor-theme` | Open source, compact, and material designed cursor set | Stable |
| `caelestia-shell-mango` | Desktop shell for MangoWM | Stable |
| `cascadia-code-nerd-fonts` | Cascadia Code patched with Nerd Fonts icons | Stable |
| `extension-manager` | Native tool for browsing and managing GNOME Shell Extensions | Stable |
| `fluxer` | Free and open source instant messaging and VoIP platform | Stable |
| `glaze` | Extremely fast, in memory, JSON and interface library | Stable |
| `gpu-screen-recorder` | Shadowplay-like screen recorder for Linux (NVIDIA/AMD/Intel) | Stable |
| `heroic-games-launcher` | Open source launcher for GOG, Epic, and Amazon Games | Stable |
| `hyprcursor` | The hyprland cursor format, library and utilities | Stable |
| `hyprgraphics` | Hyprland graphics / resource utilities | Stable |
| `hypridle` | Hyprland's idle daemon | Stable |
| `hyprlang` | The official implementation library for the hypr config language | Stable |
| `hyprland` | Dynamic tiling Wayland compositor that doesn't sacrifice on its looks | Stable |
| `hyprland-contrib` | Community scripts and utilities for Hypr projects | Git |
| `hyprland-guiutils` | Hyprland GUI utilities (welcome, run, dialog, update screens) | Stable |
| `hyprland-plugins` | Official plugins for Hyprland | Git |
| `hyprland-protocols` | Wayland protocol extensions for Hyprland | Stable |
| `hyprland-qt-support` | Qt6 QML style provider for hypr* apps | Stable |
| `hyprlock` | Hyprland's GPU-accelerated screen locking utility | Stable |
| `hyprpaper` | Blazing fast wayland wallpaper utility with IPC controls | Stable |
| `hyprpicker` | A wlroots-compatible Wayland color picker | Stable |
| `hyprpolkitagent` | A simple polkit authentication agent for Hyprland | Stable |
| `hyprqt6engine` | Qt6 Theme Provider for Hyprland | Stable |
| `hyprsunset` | An application to enable a blue-light filter on Hyprland | Stable |
| `hyprsysteminfo` | An application to display information about the running system | Stable |
| `hyprtoolkit` | A modern C++ Wayland-native GUI toolkit | Stable |
| `hyprutils` | Hyprland utilities library used across the ecosystem | Stable |
| `hyprwayland-scanner` | A Hyprland implementation of wayland-scanner, in and for C++ | Stable |
| `hyprwire` | A fast and consistent wire protocol for IPC | Stable |
| `libcava` | Fork of CAVA built as a shared library | Stable |
| `localsend` | Open source cross-platform AirDrop alternative | Stable |
| `logseq` | Privacy-first, local-first knowledge management and collaboration platform | Stable |
| `mangowm` | Modern, lightweight, high-performance Wayland compositor built on dwl | Stable |
| `material-symbols-fonts` | Material Symbols variable icon font by Google | Stable |
| `matugen` | Material You color generation tool | Stable |
| `mpvpaper` | Video wallpaper program for wlroots based Wayland compositors | Stable |
| `niri-git` | Scrollable-tiling Wayland compositor (Git Snapshot) | Git |
| `nwg-look` | GTK3 settings editor adapted for the wlroots environment | Stable |
| `obsidian` | Knowledge base over a local folder of plain-text Markdown files | Stable |
| `opencode-desktop` | Open source AI coding agent | Stable |
| `protonplus` | Modern compatibility tools manager | Stable |
| `quickshell-git` | Flexible toolkit for desktop shells with QtQuick (Git Snapshot) | Git |
| `rootapp` | Discord alternative for gaming communities and large online groups | Stable |
| `scenefx` | Drop-in wlroots scene API replacement with eye-candy effects | Stable |
| `starship` | Minimal, blazing-fast, customizable prompt for any shell | Stable |
| `vesktop` | Custom Discord client with Vencord preinstalled | Stable |
| `waypaper` | GUI wallpaper manager for Wayland and Xorg Linux systems | Stable |
| `wlroots` | Modular Wayland compositor library | Stable |
| `xdg-desktop-portal-hyprland` | xdg-desktop-portal backend for hyprland | Stable |
| `xwayland-satellite-git` | Rootless Xwayland integration for Wayland compositors (Git Snapshot) | Git |
| `zen-browser` | Privacy-focused Firefox fork | Stable |

> `Git` packages track upstream HEAD and rebuild on every new commit.

</details>

---

## 🔄 Staying Updated

No extra steps — packages update with your system:

```bash
sudo dnf upgrade
```

---

## 🛠 Troubleshooting

<details>
<summary><b>Repository not found</b></summary>
<br />
Verify the COPR is enabled:
<br /><br />
<pre>sudo dnf copr enable ackerman/nexus</pre>
</details>

<details>
<summary><b>Package not found</b></summary>
<br />
Only <code>x86_64</code> is currently supported. If a package is missing, it may be failing to build — check the
<a href="https://copr.fedorainfracloud.org/coprs/ackerman/nexus/">COPR project page</a>.
</details>

---

## 🤝 Contributing

Want a package added, or spotted something broken?

- **[Open an issue](https://github.com/Ackerman-00/fedora-nexus/issues/new)** — request a new package or report a build failure
- **[Submit a PR](https://github.com/Ackerman-00/fedora-nexus/pulls)** — add your own spec under `<package>/<package>.spec`
- **Package updates** are handled automatically by the workflow — no need to bump versions manually

---

<div align="center">

Made with 🖤 by [Ackerman-00](https://github.com/Ackerman-00) &nbsp;·&nbsp; Powered by [Fedora](https://fedoraproject.org)

</div>
