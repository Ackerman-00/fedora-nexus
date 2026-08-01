# ⚡ Nexus

[![COPR](https://img.shields.io/badge/COPR-ackerman/nexus-0055CC?style=for-the-badge&logo=fedora)](https://copr.fedorainfracloud.org/coprs/ackerman/nexus/)
[![Last build](https://copr.fedorainfracloud.org/coprs/ackerman/nexus/package/zen-browser/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/ackerman/nexus/package/zen-browser/)

**Bleeding-edge Wayland & gaming packages for Fedora 44+**

Curated packages optimized for minimal Wayland compositors (Niri, Mangowm) and high-performance gaming. Recipes live in [fedora-nexus](https://github.com/Ackerman-00/fedora-nexus).

> [!TIP]
> Enabled packages update automatically — just run `sudo dnf upgrade` as usual.

---

## Installation

```bash
# 1. Enable the repository
sudo dnf copr enable ackerman/nexus

# 2. Install a package (example)
sudo dnf install zen-browser
```

### List available packages

```bash
dnf repoquery --repoid=copr:copr.fedorainfracloud.org:ackerman:nexus
```

Or **[browse all packages online](https://copr.fedorainfracloud.org/coprs/ackerman/nexus/packages/)**.

---

## Packages

| Package | Description | Install |
|---|---|---|
| **app2unit** | Convert `.desktop` files to systemd user services | `sudo dnf install app2unit` |
| **bibata-cursor-theme** | Modern cursor theme | `sudo dnf install bibata-cursor-theme` |
| **caelestia-shell-mango** | Niri/Mangowm shell config | `sudo dnf install caelestia-shell-mango` |
| **cascadia-code-nerd-fonts** | Cascadia Code with Nerd Fonts patches | `sudo dnf install cascadia-code-nerd-fonts` |
| **extension-manager** | Manage GNOME Shell extensions | `sudo dnf install extension-manager` |
| **fluxer** | Free & open-source instant messaging and VoIP | `sudo dnf install fluxer` |
| **heroic-games-launcher** | Open-source game launcher (Epic/GOG/Amazon) | `sudo dnf install heroic-games-launcher` |
| **libcava** | Audio visualizer library | `sudo dnf install libcava` |
| **mangowm** | Tiling Wayland compositor | `sudo dnf install mangowm` |
| **material-symbols-fonts** | Material Symbols icon font | `sudo dnf install material-symbols-fonts` |
| **matugen** | Material You color generator | `sudo dnf install matugen` |
| **niri-git** | Scrollable-tiling Wayland compositor | `sudo dnf install niri-git` |
| **nwg-look** | GTK settings editor for Wayland | `sudo dnf install nwg-look` |
| **obsidian** | Knowledge base / note-taking app | `sudo dnf install obsidian` |
| **opencode-desktop** | AI coding agent | `sudo dnf install opencode-desktop` |
| **protonplus** | Proton-GE manager | `sudo dnf install protonplus` |
| **quickshell-git** | Qt-based Wayland shell | `sudo dnf install quickshell-git` |
| **rootapp** | Run GUI apps as root via Polkit | `sudo dnf install rootapp` |
| **scenefx** | Eye-candy effects for wlroots | `sudo dnf install scenefx` |
| **starship** | Minimal, fast shell prompt | `sudo dnf install starship` |
| **vesktop** | Custom Discord client with Vencord | `sudo dnf install vesktop` |
| **wlroots** | Modular Wayland compositor library | `sudo dnf install wlroots` |
| **xwayland-satellite-git** | XWayland launcher with grantlee | `sudo dnf install xwayland-satellite-git` |
| **zen-browser** | Privacy-focused Firefox fork | `sudo dnf install zen-browser` |

---

## Build status

Automated COPR builds triggered on every push to `main`.

| Branch | Build |
|---|---|
| `main` | [![Build status](https://copr.fedorainfracloud.org/coprs/ackerman/nexus/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/ackerman/nexus/) |
