#!/usr/bin/env bash
# Build the release files into dist/ from the committed tree:
#   koma-desktop-<version>.tar.gz   the installer bundle (only what it needs, plus sources)
#   get-koma.sh                     the bootstrap, with the version filled in
#   SHA256SUMS
# The version is the Global Theme's (lookandfeel/com.columbiafoundry.koma/metadata.json).
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"

if [ -n "$(git status --porcelain)" ]; then
  echo "release: commit or stash your changes first (the bundle is built from HEAD)" >&2
  exit 1
fi
version=$(python3 -c 'import json; print(json.load(open("lookandfeel/com.columbiafoundry.koma/metadata.json"))["KPlugin"]["Version"])')
bundle="koma-desktop-$version.tar.gz"

# Runtime files, plus the sources of the packages built here (Global Theme, Colors).
paths=(install.sh uninstall.sh README.md LICENSES.md docs setup packages icons wallpapers
  plasma color-schemes decorations branding lookandfeel plasmoids/colors)

rm -rf dist
mkdir -p dist
git archive --format=tar --prefix="koma-desktop-$version/" HEAD -- "${paths[@]}" ":(exclude)docs/screenshots" |
  gzip -n -9 >"dist/$bundle"
sed "s/@VERSION@/$version/" get-koma.sh >dist/get-koma.sh
(cd dist && sha256sum "$bundle" get-koma.sh >SHA256SUMS)

echo "kOMA $version"
du -h dist/* | sed 's#dist/##; s/^/  /'
