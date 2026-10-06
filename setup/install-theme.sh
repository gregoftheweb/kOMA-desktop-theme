#!/usr/bin/env bash
# Install kOMA; pass --apply to activate it without resetting the desktop layout.
set -euo pipefail
[[ $# -eq 0 || ( $# -eq 1 && $1 == --apply ) ]] || { echo 'Usage: install-theme.sh [--apply]' >&2; exit 2; }
repo="$(cd "$(dirname "$0")/.." && pwd)"
data="${XDG_DATA_HOME:-$HOME/.local/share}"
config="${XDG_CONFIG_HOME:-$HOME/.config}"
for dependency in "$data/icons/Vivid-Glassy-Dark-Icons" /usr/share/icons/Vivid-Glassy-Dark-Icons; do
  [[ ! -d "$dependency" ]] || icons_found=true
done
[[ ${icons_found:-false} == true ]] || { echo 'Install Vivid-Glassy-Dark-Icons first.' >&2; exit 1; }
backup="$config/koma/backups/$(date +%Y%m%d-%H%M%S-%N)"
mkdir -p "$backup"
for file in kdeglobals plasmarc kwinrc kcminputrc ksplashrc plasma-org.kde.plasma.desktop-appletsrc plasmashellrc kdedefaults; do
  [[ ! -e "$config/$file" ]] || cp -a "$config/$file" "$backup/"
done
echo "Appearance backup: $backup"
mkdir -p "$data/color-schemes" "$data/plasma/desktoptheme/kOMA"
mkdir -p "$data/icons/hicolor/scalable/apps"
cp "$repo/branding/koma.svg" "$data/icons/hicolor/scalable/apps/koma.svg"
cp "$repo"/color-schemes/kOMA*.colors "$data/color-schemes/"
cp -a "$repo/plasma/desktoptheme/kOMA/." "$data/plasma/desktoptheme/kOMA/"
mkdir -p "$data/wallpapers/kOMA-Tron-1/contents/images"
cp "$repo/wallpapers/tron-aqua/Tron-1.jpg" "$data/wallpapers/kOMA-Tron-1/contents/images/1280x1280.jpg"
cp "$repo/wallpapers/kOMA-Tron-1/metadata.json" "$data/wallpapers/kOMA-Tron-1/metadata.json"
if [[ -d "$data/plasma/plasmoids/com.columbiafoundry.komacolors" ]]; then
  kpackagetool6 --type Plasma/Applet --upgrade "$repo/plasmoids/colors"
else
  kpackagetool6 --type Plasma/Applet --install "$repo/plasmoids/colors"
fi
bash "$repo/setup/install-decoration.sh"
package="$repo/lookandfeel/com.columbiafoundry.koma"
if [[ -d "$data/plasma/look-and-feel/com.columbiafoundry.koma" ]]; then
  kpackagetool6 --type Plasma/LookAndFeel --upgrade "$package"
else
  kpackagetool6 --type Plasma/LookAndFeel --install "$package"
fi
if [[ ${1:-} == --apply ]]; then
  plasma-apply-lookandfeel --apply com.columbiafoundry.koma
  # Force a palette refresh even when reinstalling the same scheme name.
  kwriteconfig6 --file kdeglobals --group General --key ColorScheme --delete
  kwriteconfig6 --file kdeglobals --group General --key AccentColor --delete
  plasma-apply-colorscheme kOMATronAqua
  qdbus6 org.kde.KWin /KWin reconfigure
fi
