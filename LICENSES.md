# Component licenses and provenance

Do not treat this repository as uniformly licensed. Existing per-file and
component declarations take precedence.

| Component | License / notice |
| --- | --- |
| Global Theme | GPL-3.0-or-later; lookandfeel/com.columbiafoundry.koma/LICENSE and metadata.json |
| Plasma style | Derived from Gradient-Dark-Plasma 12.6 by l4k1; original AUTHORS and LICENSE retained in plasma/desktoptheme/kOMA |
| Color schemes | LGPL-2.0-or-later, derived from Breeze; copyright and SPDX notices retained in each .colors file |
| Colors widget | MIT; plasmoids/colors/LICENSE |
| Legacy Workspace Indicator source | GPL-2.0-or-later, derived from Desktop Switcher by Sm1Tee; plasmoids/workspaces/LICENSE and NOTICE.md |

Workspace Indicator is now maintained at https://github.com/gregoftheweb/kOMA-Workspace-Indicator.
The theme's existing workspace copy is retained for development compatibility
until the bundle uses the standalone release. It should not be developed as a
second independent source.

The theme project is inspired by Omarchy: https://github.com/basecamp/omarchy.
Downloaded reference sources are excluded from this repository.

Licensing/provenance review for the wallpaper assets, decoration, and other
artwork must be completed before the desktop release. No blanket license for
those assets is asserted by this document.

## Plasma Monochrome Icons

Bundled release 1.6.5 by Dirn, based on Orion by Seth Storm Rosenaa.
GPLv3 per upstream Store metadata. Unchanged SVG source archive, license text,
checksum, and attribution are included under `icons/`.
Source: https://store.kde.org/p/2298611

## Window management

Krohnkite 0.9.9.2 is MIT; its matching source and license are bundled.
KDE-Rounded-Corners 0.10.0 is GPL-3.0-only; its matching source archive
and GPL license text (icons/GPL-3.0.txt) accompany the Arch package.
Source: https://github.com/matinlotfali/KDE-Rounded-Corners/tree/v0.10.0
The compiled effect package targets x86_64 Arch KWin 6.7.2-1.

## Advanced Weather

Optional bundled Advanced Weather 1.8.0 by pnedyalkov91, GPL-2.0-or-later.
Upstream QML/JS/HTML source and license are preserved in the plasmoid.
Source: https://github.com/pnedyalkov91/advanced-weather-widget
