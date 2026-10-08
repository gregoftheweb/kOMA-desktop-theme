# Installer preview

Run `./install.sh` in a Plasma 6 desktop session as the desktop user.
Python 3 with curses is required; no pip bootstrap is needed.
Use arrow keys and Enter. The review screen reports missing dependencies before writing.
On Arch/EndeavourOS, missing `papirus-icon-theme` is installed automatically during
installation with an administrator prompt. The review lists this dependency installation.

Appearance installs and activates kOMA, including bundled Plasma Monochrome icons.
Full desktop components additionally installs pinned Launcher, Chet, Plugin Manager,
and Network Manager archives; Music Thing, Advanced Weather, Power Control, and Audio Control are optional.
Power Control 0.1.0 is bundled from https://store.kde.org/p/2377504 with a pinned SHA256.
The right-hand controls form one group after a separator: Audio (when selected or already installed),
optional Power Control, Network Manager, and the hidden system tray caret.
There are no separators between these system controls.
It requires dbus-python, PyGObject, UPower, and a systemd user session; power-profiles-daemon is optional.
On Arch/EndeavourOS install python-dbus and python-gobject.
PLAID remains off until explicitly enabled in the widget.
Full desktop defaults to Apply kOMA panels: replace existing panels with a compact
32 px top panel per screen, clock between expanding spacers, and known tray items
hidden behind the expand caret. Keep my panels remains available. Hotkeys and
window management are preserved; their integration and the Setup widget are pending.

`./install.sh --plan --profile full` prints a read-only plan.
Backups and shared status are stored in `$XDG_STATE_HOME/koma` (default
`~/.local/state/koma`). Failed installations retain their backup for recovery.
Restore from Welcome, or explicitly run `./uninstall.sh --restore-latest`.
Restore only overwrites files that still match the installation result. Later edits
are preserved and reported; sign out/in afterward to reload restored settings.
Restore removes installer-owned files, but may leave empty package directories.
System packages installed separately are retained.

Validation: package checksums, Python compilation, and restore behavior unit tests passed.
Fresh VM installation and actual Plasma UI behavior still require testing.

Panel center order: expanding spacer → Launcher → separator → clock/date →
optional separator + Advanced Weather → expanding spacer. The separator between
Launcher and clock is required (user clarification 2026-10-06).

Optional Audio Control installs version 0.1.0; requires pactl (libpulse) and a running
PipeWire PulseAudio-compatible service or PulseAudio. Store: https://www.opendesktop.org/p/2377512/

Applying kOMA panels also ensures at least four virtual desktops using KWin’s
virtual desktop API. Existing desktops and names are preserved; repeat installs
do not add more when four or more already exist.

Panel installation includes Spacer with Divider 1.0 by Aditya Maurya (GPL-2.0-or-later),
configured as fixed-width visible lines. Expanding spaces remain separate native spacers.

The first selection, Install Complete kOMA Theme, enables the full profile, Music Thing,
Advanced Weather, Power Control, Audio Control, kOMA hotkeys, kOMA panels with
four desktops and visible separators, and Krohnkite with colored borders.
Individual choices remain editable; Review installation still precedes Install now.

Change login & lock screen background is a combined Yes/No choice, enabled by
Install Complete kOMA Theme. It uses the kOMA Tron wallpaper, keeps the current SDDM
theme, and requests administrator access for the login screen. Lock screen settings
are included in user backups; login settings have separate root-owned backups under
/var/backups/koma-sddm and are restored through the installer with authentication.

After applying panels and finishing other changes, the installer briefly waits for
Plasma to publish the panel area, then requests a KWin reconfiguration.

On startup, live inventory detects existing widget metadata and versions, active
appearance/icons, top-panel structure, five core kOMA shortcuts, enabled Krohnkite
and borders, and login/lock backgrounds. Existing manual installations need no
installer journal. Detected choices are annotated; failed-run selections remain
available for retry. Detection of panels and hotkeys is a signature check, not a
claim that every customized setting matches the bundled defaults.
