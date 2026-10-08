# kOMA Desktop Theme

Custom KDE Plasma 6 (Wayland) desktop inspired by Omarchy, maintained by Columbia Foundry.

**Installer preview available:** run `./install.sh` for appearance or pinned desktop
components, with progress and restore. See [installer guide](docs/installer.md).
Panel setup, hotkey switching, tiling, and the Setup widget remain in development.
The local preparation plan lives outside this repository at
`../Docs/theme-preparation-plan.md` in the kOMATheme workspace.

Source: https://github.com/gregoftheweb/kOMA-desktop-theme

- `scripts/`     – helper scripts (e.g. `clone-panel.sh`: rebuild every panel as a copy of the template panel)
- `plasmoids/`   – internal Colors widget and legacy workspace source
- `lookandfeel/` – Global Theme package, panel defaults, and splash
- `setup/`       – appearance installation, shortcuts, and login background
- Planning documents and raw assets live in the parent workspace, outside Git.

Installation: see [the appearance guide](lookandfeel/README.md). The theme does
not yet install every panel dependency. Do not apply the full layout before its
required widgets are installed. Shortcut switching is an explicit separate step.

## Component licenses and attribution

This repository contains components with different licenses; it has no single
license that replaces those component licenses. See [LICENSES.md](LICENSES.md).
Original notices are retained. The wallpaper/artwork redistribution audit remains
a release task, as described in the preparation plan.

Workflow for panels: edit only the template panel (id 28, right screen), then run
`scripts/clone-panel.sh` to copy it onto every other panel.
