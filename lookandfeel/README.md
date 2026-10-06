# kOMA Global Theme

Global Theme ID: `com.columbiafoundry.koma`, version 0.1.0.
Color scheme: **kOMA Tron Aqua** (`kOMATronAqua`). Plasma style: **kOMA**.

Install and activate from the repository root:

```sh
bash setup/install-theme.sh --apply
```

Omit `--apply` to install only. The script snapshots appearance configuration
under `~/.config/koma/backups/` before installation. It does not reset panels,
shortcuts, or Krohnkite settings. Tiling remains independent and optional.
This is the appearance package, not yet the complete fresh-machine installer.

The theme selects Breeze application styling, Vivid-Glassy-Dark-Icons (install
separately), Breeze cursors, and the bundled kOMA Border decoration. Existing
focus-border effect settings are retained; the compositor effect is a separate
dependency managed by `setup/apply-focus-border.sh`.

The Plasma style derives from Gradient-Dark-Plasma 12.6 by l4k1, with upstream
AUTHORS and LICENSE preserved. Its fixed palette is omitted to follow the system
scheme. The color scheme retains Breeze's license/credits and semantic status
colors, with kOMA's five-color core palette and dark text on aqua selections.
Four schemes are installed: Tron Aqua, McLaren, Ferrari, and Lambo.
The kOMA Colors widget switches between them without applying the Global Theme.

To switch back, select another Global Theme and color scheme in System Settings.
The timestamped backup holds the previous configuration for exact recovery.

## Default panel layout

Captured 2026-10-04: one non-floating, full-width top panel per screen, 32 logical px
high, zero offset, always visible. Width follows each screen. Current widget order and workspace appearance are included
in `contents/layouts/org.kde.plasma.desktop-layout.js`; the reference snapshot is
`design/panel-defaults.json`. Install the listed custom widgets before resetting
the layout (Workspaces, kOMA Plugins, kOMA Network Manager, kOMA Music Thing).

Normal theme installation/application preserves existing panels. The layout is
used when explicitly choosing the theme's desktop layout/reset option in Plasma.

Updated panel template (2026-10-04): Workspaces → spacer → kOMA Launcher →
Digital Clock → kOMA Random Image → spacer → kOMA Plugins → kOMA Music Thing →
kOMA Network Manager → kOMA Audio Control → kOMA Colors → System Tray → margins separator.
Clock: custom date `ddd, MMM d, ` beside the time. Random Image uses
`/mnt/datapond/gonzo/archive/data/zdxj/RandomMag` on this machine; select an existing
image folder when installing on another machine.
Workspace elements: 24 px; icons: 22 px; highlight separators.
Panels are shared across virtual desktops; task/workspace indicators still
reflect the current desktop. Transient network readings, launcher requests, and
config-dialog sizes are excluded from packaged defaults.

Default wallpaper: `Tron-1.jpg`, installed as the `kOMA-Tron-1` wallpaper
package from `wallpapers/tron-aqua/Tron-1.jpg`. Selected by the Global Theme
Wallpaper default.

Audio Control: install the separate `/mnt/devplex/kOMA-AudioControl` project
with `bin/install` (or `--no-place` before applying a fresh layout). Its widget,
`com.columbiafoundry.komaaudiocontrol`, is included before Music Thing in the
default panel. It uses native Plasma styling and follows the active palette.

## Splash

Approved default splash for the kOMA Global Theme (2026-10-04).
The package selects `KSplashQML` and `com.columbiafoundry.koma`; installation
bundles the background, logo, and animated butterfly together.

The kOMA splash uses `tron-flower.jpg` with a small McLaren orange (`#FF8700`)
butterfly. Its wings flutter while it follows randomized curved paths within
the screen. The aqua-and-orange kOMA logo sits near the bottom with the kOMA
wordmark underneath. Startup completion stops the animation; it does not delay login.
The butterfly artwork is vector SVG with QML animation, authored for kOMA.

Preview: `qml6 dev/splash/preview.qml` from the repository root (Escape closes).
The background image is bundled inside the theme so the splash needs no
workspace paths or external commands. The source wallpaper remains in
`wallpapers/tron-aqua/tron-flower.jpg`.

## Login screen

Install the bundled `Tron-1.jpg` as the SDDM login background, matching the
default kOMA lock-screen wallpaper:

```sh
sudo python3 setup/install-login-background.py
```

This preserves the active SDDM theme, copies the image into a system-readable
location, and updates its `theme.conf.user` background setting. Previous settings
are saved under `/var/backups/koma-sddm/`. It takes effect at the next login screen
without restarting SDDM or ending the current session. This is a separate system
installation step; installing a Plasma Global Theme alone does not configure SDDM.

Use `--wallpaper /absolute/path/to/image` to match a different lock-screen image,
or `--theme breeze` to configure a specific installed SDDM theme.
