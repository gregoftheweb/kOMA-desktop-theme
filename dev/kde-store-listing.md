# KDE Store submission: kOMA (Global Theme)

Category: Global Themes (Plasma 6)
Name: kOMA
License: GPL-3.0-or-later (Global Theme package; other components keep their own licenses, see LICENSES.md)
Source: https://github.com/gregoftheweb/kOMA-desktop-theme
Upload: `packages/com.columbiafoundry.koma.zip` (rebuild with `make packages`)
Images: `docs/screenshots/desktop.png` (display image), `docs/screenshots/workspace-both.png`

## Description

**Omarchy's feel, still all Plasma.** kOMA (KDE + Omarchy) is inspired by Omarchy: its dark, sharp look, keyboard-driven workflow and tiling. kOMA gets KDE Plasma 6 as close to that experience as it can, without giving up what makes Plasma Plasma: its widgets, settings and endless customization. Everything is built from native Plasma parts, so you can keep tweaking it like any other Plasma desktop.

**Tiling that's still Plasma.** Krohnkite (a KWin script) tiles your windows like a tiling window manager, but it runs on top of Plasma, so you keep the best of both:

- Pop any window out of the tiling into a floating window, and back again
- Tiled windows stay resizable: drag a border to change their widths
- One workspace spans your whole screen set, so a single workspace covers both screens on a two-monitor setup

**The complete kOMA desktop installs with one command.** In a Plasma 6 session, open a terminal and run:

```
curl -fsSL https://github.com/gregoftheweb/kOMA-desktop-theme/releases/latest/download/get-koma.sh | bash
```

It downloads the kOMA installer, verifies it, and shows every change before applying anything. Your current settings are backed up first, and Restore puts your original desktop back, panels included.

What you get:

- Dark look with one bright accent, in four color schemes: Tron Aqua, McLaren, Ferrari, Lambo
- No title bars, with a colored outline on the focused window
- Compact top panel per screen: workspaces, launcher, clock, network, audio and power controls
- kOMA Launcher: Super+Space app search and the Omarchy menu tree
- Omarchy-style hotkeys and Krohnkite tiling (both optional)
- kOMA Lightcycles wallpaper, plus Powder and River; matching lock and login screens
- Plasma Monochrome icons and an animated kOMA splash

This Store item is the Global Theme on its own. Installed alone, it does not include the kOMA Plasma style, color schemes, window decoration, wallpapers or widgets; the installer above adds them.

Requirements: KDE Plasma 6, Python 3, curl. Tested on EndeavourOS with KWin 6.7.
