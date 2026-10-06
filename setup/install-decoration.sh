#!/usr/bin/env bash
# Install (or upgrade) the kOMA Border window decoration and optionally make it active.
#   install-decoration.sh           install/upgrade only (the Global Theme selects it)
#   install-decoration.sh --apply   also set it as the decoration now (backs up kwinrc)
# Safe to re-run. Needs kpackagetool6, kwriteconfig6, qdbus6 (Plasma 6).
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
pkg="$repo/decorations/komaborder"
id="com.columbiafoundry.komaborder"

kpackagetool6 --type KWin/Decoration --upgrade "$pkg" >/dev/null 2>&1 \
  || kpackagetool6 --type KWin/Decoration --install "$pkg"
echo "kOMA Border installed ($id)"

if [[ "${1:-}" == "--apply" ]]; then
  cfg="${XDG_CONFIG_HOME:-$HOME/.config}/kwinrc"
  [[ -f "$cfg" ]] && cp "$cfg" "$cfg.bak-$(date +%Y%m%d%H%M%S)"
  kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae
  kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme "$id"
  qdbus6 org.kde.KWin /KWin reconfigure
  echo "kOMA Border is now the window decoration"
fi
