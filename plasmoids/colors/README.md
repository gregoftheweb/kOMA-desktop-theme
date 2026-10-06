# kOMA Colors

Plasma 6 panel widget for switching the desktop between Tron Aqua, McLaren,
Ferrari, and Lambo. Click the four-color icon and choose a named swatch.
The check mark reflects KDE's current color scheme. Errors stay visible in the popup.

Install together with the schemes using `bash setup/install-theme.sh` from the
repository root, then add **kOMA Colors** to a panel. The kOMA default layout
includes it before kOMA Plugins. Requires Python 3, Plasma's executable data
engine, `kreadconfig6`, `kwriteconfig6`, and `plasma-apply-colorscheme`.

For existing panels, run `python3 setup/place-colors.py` from the repository root.
It backs up the panel config, adds the widget once per panel, and briefly restarts
Plasma to persist its position. It is safe to re-run.

Checks: `python3 -m unittest discover -s plasmoids/colors/tests -v` from the
repository root, plus `qmllint plasmoids/colors/contents/ui/main.qml`.

The helper applies only the color scheme, clearing a custom KDE accent override
so the named palette's exact colors are used. Global Theme, wallpaper, panels,
fonts, icons, and app-specific preferences are untouched. Switching applies to
the entire KDE session, including all monitors. Concurrent switches are locked.

CLI: `python3 contents/code/koma-colors tron|mclaren|ferrari|lambo|status|list`.

Copyright 2026 Columbia Foundry. Widget and helper: MIT (see LICENSE).
The separately installed color schemes retain their Breeze-derived LGPL notices.
