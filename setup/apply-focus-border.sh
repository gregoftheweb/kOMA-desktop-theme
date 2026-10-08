#!/usr/bin/env bash
# Omarchy-style focus border on every window (server- and client-side decorated),
# drawn by the KDE-Rounded-Corners KWin effect (AUR: kwin-effect-rounded-corners).
#   Focused window:   3 px, color scheme Highlight (follows scheme/accent live)
#   Other windows:    3 px, rgba(89,89,89,170)  = Omarchy's 595959aa
#   Square corners, no effect shadow, no border on fullscreen windows.
# Safe to re-run. Backs up kwinrc first. Needs kwriteconfig6, qdbus6.
set -euo pipefail

effect=kwin4_effect_shapecorners
if ! ls /usr/lib/qt6/plugins/kwin/effects/plugins/$effect.so >/dev/null 2>&1; then
  echo "Missing $effect: install it first, e.g. yay -S --needed kwin-effect-rounded-corners" >&2
  exit 1
fi

cfg="${XDG_CONFIG_HOME:-$HOME/.config}/kwinrc"
[[ -f "$cfg" ]] && cp "$cfg" "$cfg.bak-$(date +%Y%m%d%H%M%S)"

w() { kwriteconfig6 --file kwinrc --group Round-Corners --key "$1" "$2"; }

# Shape: Omarchy uses rounding = 0 and no shadow
w Size 0
w InactiveCornerRadius 0
w UseNativeDecorationShadows true
w ShadowSize 0
w InactiveShadowSize 0

# Focused window: 3 px in the palette Highlight color (QPalette::Highlight = 12)
w OutlineThickness 3
w ActiveOutlineUsePalette true
w ActiveOutlineUseCustom false
w ActiveOutlinePalette 12
w ActiveOutlineAlpha 255

# Unfocused windows: 3 px dim grey
w InactiveOutlineThickness 3
w InactiveOutlineUsePalette false
w InactiveOutlineUseCustom true
w InactiveOutlineColor 89,89,89
w InactiveOutlineAlpha 170

# No second or outer outline
w SecondOutlineThickness 0
w InactiveSecondOutlineThickness 0
w OuterOutlineThickness 0
w InactiveOuterOutlineThickness 0

# Border on tiled and maximized windows too (Hyprland does); not on fullscreen
w DisableOutlineTile false
w DisableOutlineMaximize false
w DisableOutlineFullScreen true

kwriteconfig6 --file kwinrc --group Plugins --key "${effect}Enabled" true

# Load or reload the effect live. A freshly installed effect may only be picked up
# by KWin at the next login; say so rather than reporting success.
loaded() { [[ "$(qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.isEffectLoaded $effect)" == "true" ]]; }
qdbus6 org.kde.KWin /KWin reconfigure
if loaded; then
  qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.reconfigureEffect $effect
else
  echo "loadEffect $effect: $(qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.loadEffect $effect)"
fi
if loaded; then
  echo "Focus border active ($effect)"
else
  echo "Focus border enabled; KWin starts it at your next sign-in ($effect)"
fi
