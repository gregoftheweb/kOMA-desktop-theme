#!/usr/bin/env bash
# kOMA bootstrap: download the kOMA desktop bundle, verify it, and start the installer.
#
#   curl -fsSL https://github.com/gregoftheweb/kOMA-desktop-theme/releases/latest/download/get-koma.sh | bash
#
# Nothing on the desktop changes until you confirm it in the installer, which backs up
# your current settings first. The release build fills in the version below.
set -euo pipefail

version="${KOMA_VERSION:-@VERSION@}"
base="${KOMA_RELEASE_URL:-https://github.com/gregoftheweb/kOMA-desktop-theme/releases/download/v$version}"
bundle="koma-desktop-$version.tar.gz"
dest="${XDG_CACHE_HOME:-$HOME/.cache}/koma/bundle-$version"

say() { printf '  %s\n' "$*"; }
fail() {
  printf '\n  kOMA: %s\n\n' "$*" >&2
  exit 1
}

# The installer is a full-screen terminal program: it needs a keyboard, which
# `curl | bash` leaves on the terminal rather than on stdin.
if [ -t 0 ]; then
  tty=/dev/stdin
elif [ -r /dev/tty ] && [ -w /dev/tty ]; then
  tty=/dev/tty
else
  fail "run this from a terminal (it opens an interactive installer)."
fi

[ "$(id -u)" -ne 0 ] || fail "run this as your normal user, not root. The installer asks for administrator rights only for the steps that need them."
case "$version" in *@*) fail "this is the unreleased template; use get-koma.sh from a release, or set KOMA_VERSION." ;; esac
for tool in curl tar sha256sum python3; do
  command -v "$tool" >/dev/null || fail "$tool is required but not installed."
done
python3 -c 'import curses' 2>/dev/null || fail "Python's curses module is required."
command -v kpackagetool6 >/dev/null || fail "KDE Plasma 6 is required (kpackagetool6 was not found)."
case "${XDG_CURRENT_DESKTOP:-}" in
  *KDE*) ;;
  *) say "Note: this does not look like a Plasma session (XDG_CURRENT_DESKTOP=${XDG_CURRENT_DESKTOP:-unset})." ;;
esac

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

echo
say "kOMA $version"
say "Downloading $bundle"
curl -fL --progress-bar "$base/$bundle" -o "$work/$bundle" || fail "download failed: $base/$bundle"
curl -fsSL "$base/SHA256SUMS" -o "$work/SHA256SUMS" || fail "could not download the checksums: $base/SHA256SUMS"
grep -E " \*?$bundle\$" "$work/SHA256SUMS" >"$work/expected" || fail "SHA256SUMS has no entry for $bundle."
(cd "$work" && sha256sum --check --quiet expected) || fail "checksum mismatch: the download is incomplete or has been altered."
say "Verified."

rm -rf "$dest"
mkdir -p "$dest"
tar -xzf "$work/$bundle" -C "$dest" --strip-components=1
[ -f "$dest/install.sh" ] || fail "the bundle has no install.sh."

say "Starting the installer"
rm -rf "$work" # exec skips the EXIT trap
exec bash "$dest/install.sh" "$@" <"$tty"
