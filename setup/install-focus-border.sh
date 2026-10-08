#!/usr/bin/env bash
# Runs in a separate terminal so sudo and compiler progress remain visible.
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
state="${XDG_STATE_HOME:-$HOME/.local/state}/koma/focus-border-build"
mkdir -p "$state"
cp "$repo/packages/focus-border-PKGBUILD" "$state/PKGBUILD"
cp "$repo/packages/kwin-effect-rounded-corners-0.10.0.tar.gz" "$state/"
cd "$state"
# Use the bundled, checksum-verified source rather than downloading latest.
# shellcheck disable=SC2016 # ${pkgver} is the PKGBUILD's own variable, matched literally
sed -i 's|::https://github.com/matinlotfali/KDE-Rounded-Corners/archive/v${pkgver}.tar.gz||' PKGBUILD
printf '\nBuilding kOMA colored borders for your installed KWin.\n'
sudo pacman -S --needed base-devel cmake extra-cmake-modules ninja vulkan-headers
makepkg --force --cleanbuild --noconfirm
sudo pacman -U --needed --noconfirm kwin-effect-rounded-corners-0.10.0-1-x86_64.pkg.tar.zst
printf '\nBorder effect installed. Return to the kOMA installer.\n'
