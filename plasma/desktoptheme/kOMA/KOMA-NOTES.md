# kOMA notes

kOMA (**K**DE + **OMA**rchy) makes KDE Plasma 6 on Wayland look and drive like
[Omarchy](https://omarchy.org), the keyboard-first Arch Linux setup by David
Heinemeier Hansson (MIT). It is maintained by Columbia Foundry.

kOMA is not a port of Omarchy. Omarchy is built on Hyprland and its own tooling;
kOMA keeps Plasma underneath and rebuilds the Omarchy experience out of native
Plasma parts: a Global Theme, a Plasma style, color schemes, a window decoration,
panel widgets, KWin scripts and global shortcuts. Everything uses KDE's own
components, settings and KDE Store, so a kOMA desktop stays an ordinary Plasma
desktop that can be changed or reverted with System Settings.

This file lives in the kOMA Plasma style package, which is one piece of the
whole. The first section covers this package; the rest covers the project.

---

## This package: the kOMA Plasma style

Derived from the locally installed **Gradient-Dark-Plasma 12.6 by l4k1**.
Upstream: https://github.com/L4ki/Gradient-Plasma-Themes. The original `AUTHORS`
and `LICENSE` (GPLv3) are retained, and assets keep their original licenses.

kOMA changes:

- **Package name and id** changed to `kOMA`, version 0.1.0.
- **Adaptive color:** the fixed `colors` file is omitted, so the style follows
  the active color scheme. Switching between the four kOMA schemes (or any other
  scheme) recolors panels, popups and widgets without a separate style per color.
- **Panel:** 40% background opacity (60% transparent). The existing 1 px edge
  geometry is drawn in `ColorScheme-Highlight`, so the panel's edge line takes
  the accent of the active scheme. Applied to the standard, solid, opaque and
  translucent assets; rounded corners and masks are preserved.
- Geometry, transparency, adaptive transparency and blur-behind are otherwise
  unchanged from Gradient Dark.

---

## What kOMA takes from Omarchy

| Omarchy | kOMA on Plasma |
| --- | --- |
| Dark, flat look with one bright accent | kOMA color schemes, Plasma style following the scheme, Plasma Monochrome icons |
| Windows without title bars, a colored border on the focused window | **kOMA Border** window decoration (no title bar) plus the rounded-corners focus border effect |
| Compact top bar: workspaces left, clock center, controls right | **kOMA panels**: one 32 px top panel per screen with the same layout |
| Numbered workspaces showing their apps | **kOMA Workspace Indicator** |
| Super+Space launcher and the Omarchy menu tree | **kOMA Launcher** |
| Super-key hotkeys for everything | **kOMA hotkeys** profile (optional, restorable) |
| Tiling window management | **Krohnkite** KWin script (optional) |
| Network, audio and power panels | **kOMA Network Manager, Audio Control, Power Control** |
| Plugin/extension management | **kOMA Plugins**, built on the KDE Store |
| One-command install | `get-koma.sh` bootstrap and the kOMA installer |

What kOMA deliberately does differently:

- **Native Plasma, not a skin.** Widgets use Plasma components, the active
  Plasma style, fonts and color scheme. No Omarchy-specific styling is imposed
  on popups or controls.
- **Opt-in, reversible changes.** Hotkeys, panels, tiling and login backgrounds
  are separate choices. The installer backs up what it changes and can restore
  it, keeping any later edits the user made.
- **KDE's ecosystem.** Add-ons come from the KDE Store and KDE's package types
  (Plasma widgets, KWin scripts and effects, decorations) rather than a separate
  plugin system.

---

## Appearance

### Global Theme: `com.columbiafoundry.koma`

Ties the look together: the kOMA Plasma style, the kOMA Tron Aqua color scheme,
Breeze application style and cursors, Plasma Monochrome icons, the kOMA Border
decoration, the kOMA splash and the kOMA Lightcycles wallpaper. Applying it does
not reset panels, shortcuts or tiling. GPL-3.0-or-later.

### Color schemes

Four schemes, each derived from Breeze (LGPL-2.0-or-later, notices retained).
They share a dark neutral base and differ only in the accent, which drives
selections, focus, the panel edge line and the focus border.

| Scheme | Accent | Note |
| --- | --- | --- |
| kOMA Tron Aqua | `#23C8FF` | Default. Dark (Midnight) text on aqua selections |
| kOMA McLaren | `#FF8700` | Also the color of the "K" in the kOMA mark |
| kOMA Ferrari | `#FF3245` | |
| kOMA Lambo | `#68DC45` | |

Supporting palette: Midnight `#0A0D12` (background), Blue Graphite `#151B25`
(surfaces), Steel Blue `#8692A3` (secondary text), Ice White `#E9EEF5` (text).
Status colors (positive, neutral, negative) stay Breeze's.

The **kOMA Colors** panel widget switches between the four schemes in one click
without reapplying the Global Theme.

### Window decoration: kOMA Border

`com.columbiafoundry.komaborder`, an Aurorae decoration with no title bar, as in
Omarchy. It pairs with **KDE-Rounded-Corners** (GPL-3.0-only), a compiled KWin
effect that draws the colored outline around the focused window. The effect is
optional; the decoration works without it.

### Icons

**Plasma Monochrome Icons 1.6.5** by Dirn, based on Orion by Seth Storm Rosenaa
(GPLv3), bundled unchanged with its license and provenance. Papirus-Dark is its
fallback.

### Splash screen

A `KSplashQML` splash on the `tron-flower` image: a small McLaren-orange vector
butterfly flutters along random curved paths while the aqua-and-orange kOMA mark
and wordmark sit near the bottom. It stops when startup completes and never
delays login. Authored for kOMA in SVG and QML.

### Wallpapers

| Wallpaper | Role |
| --- | --- |
| **kOMA Lightcycles** | Default desktop wallpaper |
| **kOMA Powder** | Neon line drawing of a skier on a mountain |
| **kOMA River** | Misty magenta canyon with an aqua river; default lock and login background |

kOMA Lightcycles is generated by `design/wallpaper/lightcycles.py`: the kOMA mark
centered on a dark blue grid, one light-cycle trail per color scheme turning at
right angles and ending in a bright bike, and a small `kOMA` wordmark drawn in
the mark's own stroke style. It renders 1920x1080, 2560x1440 and 3840x2160 from
one drawing. All three are wallpaper packages, so they appear by name in
Plasma's wallpaper settings and in the kOMA Launcher's Style › Wallpaper menu.

### The kOMA mark

`branding/koma.svg`: three open, interconnected circular strokes in Tron Aqua
with an uppercase K in McLaren orange. An original vector drawing inspired by
Omarchy's line treatment, not traced from it, and font-free.

### Lock and login screens

The lock screen uses kOMA River. The installer can also set it as the SDDM login
background: it keeps the active SDDM theme, copies the image to a system-readable
location, edits only the theme's background setting, and keeps a root-owned
backup for restore. This step asks for administrator rights; nothing restarts
SDDM or ends the session.

---

## The kOMA panel

One non-floating, full-width, 32 px top panel per screen, shared across virtual
desktops. Left to right:

1. **Workspace Indicator**, then a separator
2. Expanding space
3. **kOMA Launcher**, separator, **Digital Clock** (`ddd, MMM d,` beside the time)
4. Optional separator and **Advanced Weather**
5. Expanding space, separator
6. **kOMA Plugins**, optional **Music Thing**, optional **Audio Control**,
   optional **Power Control**, **Network Manager**
7. **System Tray**, with known tray items hidden behind the expand arrow
8. Separator, **kOMA Colors**

Separators are fixed-width lines from **Spacer with Divider 1.0** by Aditya
Maurya (GPL-2.0-or-later). Applying kOMA panels also ensures at least four
virtual desktops; existing desktops and names are kept.

---

## kOMA widgets and tools

Each widget is its own project with tests, lint and format gates and a
changelog. The first seven below are published on GitHub and the KDE Store, and
the installer bundles their pinned, checksum-verified releases.

| Component | Version | What it does | Omarchy counterpart |
| --- | --- | --- | --- |
| [kOMA Launcher](https://github.com/gregoftheweb/kOMA-Launcher) | 0.2.2 | Keyboard-driven launcher card on the active screen with type-to-search across apps and the whole Omarchy menu tree (Apps, Learn, Trigger, Style, Setup, About, System), KDE-native actions, live keybinding reference, wallpaper picker, `komalauncher open <menu>` for hotkeys | Launcher and Omarchy menu |
| [kOMA Workspace Indicator](https://github.com/gregoftheweb/kOMA-Workspace-Indicator) | 0.2.3 | Numbered workspaces with app icons ordered by window position across all screens; derived from Desktop Switcher 1.0 by Sm1Tee (GPL-2.0-or-later) | Waybar workspaces |
| [kOMA Plugins](https://github.com/gregoftheweb/kOMA-Plugins) | 0.4.2 | Lists installed widgets, KWin scripts, effects and decorations; enable, disable, remove; install from the KDE Store or git; hourly update checks with in-widget updates | Plugin manager |
| [kOMA Network Manager](https://github.com/gregoftheweb/kOMA-NetworkManager) | 0.1.1 | Live ping, packet loss and traffic, IP and gateway, Wi-Fi networks, speed samples, one-click DNS (DHCP, Cloudflare, Google, custom) | Network panel |
| [kOMA Audio Control](https://github.com/gregoftheweb/kOMA-AudioControl) | 0.1.0 | Output and microphone volume and mute, device lists, moves streams when switching devices | Audio panel |
| [kOMA Power Control](https://github.com/gregoftheweb/kOMA-PowerControl) | 0.1.0 | Battery charge and health, power profiles, and PLAID Power, which holds off suspend, dimming and locking until turned off | Power menu |
| [kOMA Music Thing](https://github.com/gregoftheweb/kOMA-MusicThing) | 0.3.0 | Compact MPD player; expands to run rmpc inside the popup, with an optional cava visualizer; guided MPD setup | Music |
| kOMA Colors | 0.1.0 | Switches between the four kOMA color schemes (part of this theme) | Theme switcher |
| kOMA Systray | script | Keeps tray entries in the tray popup so only the arrow shows on the panel (not yet published) | |

Third-party components the installer can add, unchanged and with their licenses:
**Krohnkite 0.9.9.2** (MIT; tiling), **KDE-Rounded-Corners 0.10.0** (GPL-3.0-only;
focus border), **Advanced Weather 1.8.0** by pnedyalkov91 (GPL-2.0-or-later) and
**Spacer with Divider 1.0** (GPL-2.0-or-later).

### Engineering notes

- **Plasma stays fast.** Widgets that run commands use one fixed source name per
  command through a shared `CommandQueue` component. Plasma's command engine
  keeps a property for every source name it has ever seen, so unique per-call
  names made plasmashell slower over the day until it pinned a CPU core.
- **Polling only when needed.** Music Thing waits for MPD to report a change
  instead of polling while closed; Network Manager skips a poll while the
  previous one runs.
- **Installs carry only the package.** Development installs copy only what the
  store package ships, never repository tooling.

---

## Hotkeys

An optional Omarchy-style profile (`setup/keybindings/keybindings.tsv`). It is a
visible choice in the installer: **Use kOMA hotkeys** or **Keep my hotkeys**.
Every replaced assignment is saved and can be restored.

| Group | Examples |
| --- | --- |
| Launcher menus | Super+Space launcher, Super+Alt+Space apps, Super+Esc system menu, Super+K keybindings, Super+Ctrl+C capture, Super+Ctrl+O toggles |
| Windows | Super+W close, Super+F fullscreen, Super+arrows focus, Super+Shift+arrows tile, Super+O keep above |
| Workspaces | Super+1…0 switch, Super+Shift+1…0 move window, Super+Tab next workspace |
| Monitors | Super+Ctrl+Shift+arrows move window, Ctrl+Alt+Tab focus next monitor |
| System and toggles | Super+Ctrl+L lock, Super+Ctrl+N night light, Super+Ctrl+I stay awake, Super+Shift+Space panel autohide |
| Capture | Print region screenshot, Alt+Print region recording, Super+Print color picker, Super+Ctrl+Print text from screen (OCR) |
| Apps | Super+Return terminal, Super+Shift+F file manager, Super+Shift+B browser |

Applied hotkeys only target installed actions; conflicting assignments are
listed before anything changes.

---

## Installing

```sh
curl -fsSL https://github.com/gregoftheweb/kOMA-desktop-theme/releases/latest/download/get-koma.sh | bash
```

`get-koma.sh` checks for Plasma 6 and Python, downloads the versioned bundle,
verifies it against the release's `SHA256SUMS`, and opens the kOMA installer: a
full-screen terminal program with a review screen before anything is written.

- **Install Complete kOMA Theme** selects everything: appearance, widgets,
  panels, hotkeys, Krohnkite with focus borders, and lock and login backgrounds.
  Each choice can still be changed before **Install now**.
- **Appearance** installs and applies only the look.
- Settings are backed up first under `~/.local/state/koma`. **Restore** puts back
  only files that still match what the installer wrote; later edits are kept and
  reported.
- Afterwards the installer is available from the kOMA Launcher under
  **Setup › kOMA Installer**. On a machine without it, the Launcher's
  **Get the Complete kOMA Theme** runs the same bootstrap.

The KDE Store carries the Global Theme as a showcase, with the command above.
Store installs of the Global Theme alone do not include the Plasma style, color
schemes, decoration or wallpapers; the installer provides those.

---

## Licenses and attribution

kOMA is not uniformly licensed; each component keeps its own license. See
`LICENSES.md` in the repository.

- Inspired by **Omarchy** by David Heinemeier Hansson (MIT). The kOMA Launcher's
  menu model, look and behavior are ported from Omarchy with attribution.
- Plasma style: **Gradient Dark** by l4k1 (GPLv3).
- Color schemes: derived from **Breeze** (LGPL-2.0-or-later).
- Workspace Indicator: derived from **Desktop Switcher** by Sm1Tee (GPL-2.0-or-later).
- Icons: **Plasma Monochrome** by Dirn, based on **Orion** by Seth Storm Rosenaa (GPLv3).
- Third-party KWin and widget components keep their upstream licenses and sources.

Source: https://github.com/gregoftheweb/kOMA-desktop-theme
