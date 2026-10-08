#!/usr/bin/env bash
# Install kOMA; pass --apply to activate it without resetting the desktop layout.
set -euo pipefail
[[ $# -eq 0 || ( $# -eq 1 && $1 == --apply ) ]] || { echo 'Usage: install-theme.sh [--apply]' >&2; exit 2; }
repo="$(cd "$(dirname "$0")/.." && pwd)"
data="${XDG_DATA_HOME:-$HOME/.local/share}"
config="${XDG_CONFIG_HOME:-$HOME/.config}"
icons_found=false
for dependency in "$data/icons/Papirus-Dark/index.theme" /usr/local/share/icons/Papirus-Dark/index.theme /usr/share/icons/Papirus-Dark/index.theme; do
  [[ ! -f "$dependency" ]] || icons_found=true
done
[[ $icons_found == true ]] || { echo 'Install papirus-icon-theme first (Papirus-Dark fallback).' >&2; exit 1; }
(cd "$repo/icons" && sha256sum --check plasma-monochrome-icons.tar.gz.sha256)
backup="$config/koma/backups/$(date +%Y%m%d-%H%M%S-%N)"
mkdir -p "$backup"
for file in kdeglobals plasmarc kwinrc kcminputrc ksplashrc plasma-org.kde.plasma.desktop-appletsrc plasmashellrc kdedefaults; do
  [[ ! -e "$config/$file" ]] || cp -a "$config/$file" "$backup/"
done
echo "Appearance backup: $backup"
mkdir -p "$data/icons"
if [[ -e "$data/icons/plasma-monochrome-icons" ]]; then
  mv "$data/icons/plasma-monochrome-icons" "$backup/"
fi
tar -xzf "$repo/icons/plasma-monochrome-icons.tar.gz" -C "$data/icons"
cp "$repo/icons/GPL-3.0.txt" "$data/icons/plasma-monochrome-icons/COPYING"
cp "$repo/icons/README.md" "$data/icons/plasma-monochrome-icons/KOMA-PROVENANCE.md"
mkdir -p "$data/color-schemes" "$data/plasma/desktoptheme/kOMA"
mkdir -p "$data/icons/hicolor/scalable/apps"
cp "$repo/branding/koma.svg" "$data/icons/hicolor/scalable/apps/koma.svg"
cp "$repo"/color-schemes/kOMA*.colors "$data/color-schemes/"
cp -a "$repo/plasma/desktoptheme/kOMA/." "$data/plasma/desktoptheme/kOMA/"
mkdir -p "$data/wallpapers/kOMA-Tron-1/contents/images"
cp "$repo/wallpapers/tron-aqua/Tron-1.jpg" "$data/wallpapers/kOMA-Tron-1/contents/images/1280x1280.jpg"
cp "$repo/wallpapers/kOMA-Tron-1/metadata.json" "$data/wallpapers/kOMA-Tron-1/metadata.json"
# Ready-made wallpaper packages (the default is kOMA Lightcycles)
for wallpaper in kOMA-Lightcycles; do
  rm -rf "${data:?}/wallpapers/$wallpaper"
  cp -a "$repo/wallpapers/$wallpaper" "$data/wallpapers/$wallpaper"
done
# Replace only kOMA-owned packages; retain old copies in the appearance backup.
for relative in plasma/plasmoids/com.columbiafoundry.komacolors plasma/look-and-feel/com.columbiafoundry.koma aurorae/themes/com.columbiafoundry.komaborder; do
  target="$data/$relative"
  if [[ -e "$target" ]]; then
    mkdir -p "$backup/packages/$(dirname "$relative")"
    mv "$target" "$backup/packages/$relative"
  fi
done
kpackagetool6 --type Plasma/Applet --install "$repo/packages/com.columbiafoundry.komacolors.plasmoid"
bash "$repo/setup/install-decoration.sh"
kpackagetool6 --type Plasma/LookAndFeel --install "$repo/packages/com.columbiafoundry.koma.zip"
if [[ ${1:-} == --apply ]]; then
  plasma-apply-lookandfeel --apply com.columbiafoundry.koma
  # Force a palette refresh even when reinstalling the same scheme name.
  kwriteconfig6 --file kdeglobals --group General --key ColorScheme --delete
  kwriteconfig6 --file kdeglobals --group General --key AccentColor --delete
  plasma-apply-colorscheme kOMATronAqua
  qdbus6 org.kde.KWin /KWin reconfigure
fi
