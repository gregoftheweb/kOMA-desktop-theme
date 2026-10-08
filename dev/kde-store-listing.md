# KDE Store submission: kOMA (Global Theme)

Category: Global Themes (Plasma 6)
Name: kOMA
License: GPL-3.0-or-later (Global Theme package; other components keep their own licenses, see LICENSES.md)
Source: https://github.com/gregoftheweb/kOMA-desktop-theme
Upload: `packages/com.columbiafoundry.koma.zip` (rebuild with `make packages`)
Images: `docs/screenshots/desktop.png` (display image), `docs/screenshots/workspace-both.png`

## Description

**The complete kOMA desktop installs with one command.** In a Plasma 6 session, open a terminal and run:

```
curl -fsSL https://github.com/gregoftheweb/kOMA-desktop-theme/releases/latest/download/get-koma.sh | bash
```

It downloads the kOMA installer, verifies it, and shows every change before applying anything. Your current settings are backed up and can be restored at any time.

kOMA (KDE + Omarchy) makes KDE Plasma 6 look and drive like Omarchy, built entirely from native Plasma parts:

- Dark look with one bright accent, in four color schemes: Tron Aqua, McLaren, Ferrari, Lambo
- No title bars, with a colored outline on the focused window
- Compact top panel per screen: workspaces, launcher, clock, network, audio and power controls
- kOMA Launcher: Super+Space app search and the Omarchy menu tree
- Optional Omarchy-style hotkeys and Krohnkite tiling
- kOMA Lightcycles wallpaper, plus Powder and River; matching lock and login screens
- Plasma Monochrome icons and an animated kOMA splash

This Store item is the Global Theme on its own. Installed alone, it does not include the kOMA Plasma style, color schemes, window decoration, wallpapers or widgets; the installer above adds them.

Requirements: KDE Plasma 6, Python 3, curl. Tested on EndeavourOS with KWin 6.7.
