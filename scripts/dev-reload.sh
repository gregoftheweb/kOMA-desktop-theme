#!/usr/bin/env bash
# Install/upgrade the workspaces plasmoid from source and restart plasmashell.
set -e
kpackagetool6 --type Plasma/Applet --upgrade "$(dirname "$0")/../plasmoids/workspaces" 2>/dev/null \
  || kpackagetool6 --type Plasma/Applet --install "$(dirname "$0")/../plasmoids/workspaces"
plasmashell --replace >/dev/null 2>&1 & disown
