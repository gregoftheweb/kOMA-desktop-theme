#!/usr/bin/env python3
"""Pin packages/manifest.json to the latest GitHub releases of the kOMA widgets.

    update-pins.py           download newer releases into packages/ and update the manifest
    update-pins.py --check   only report pins that are behind (exit 1 if any)

Applies to components whose source is https://github.com/gregoftheweb/<repo>. Each
.plasmoid is verified against the release's SHA256SUMS and its metadata version must
match the tag. Third-party components are left as they are. Needs the gh CLI.
"""

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "packages"
MANIFEST = PACKAGES / "manifest.json"
OWNER = "https://github.com/gregoftheweb/"


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def latest(repo):
    release = json.loads(gh("release", "view", "-R", repo, "--json", "tagName,assets"))
    assets = [a["name"] for a in release["assets"] if a["name"].endswith(".plasmoid")]
    if len(assets) != 1:
        sys.exit(f"{repo} {release['tagName']}: expected one .plasmoid asset, found {assets}")
    return release["tagName"], assets[0]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plasmoid_version(path):
    with zipfile.ZipFile(path) as z:
        return json.loads(z.read("metadata.json"))["KPlugin"]["Version"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    behind = []
    for c in manifest:
        source = c.get("source", "")
        if not source.startswith(OWNER):
            continue
        repo = source.removeprefix("https://github.com/")
        tag, asset = latest(repo)
        version = tag.removeprefix("v")
        if c["version"] == version and c["asset"] == asset and "local_patch" not in c:
            print(f"ok      {c['name']} {version}")
            continue
        behind.append(c["name"])
        print(f"{'behind' if a.check else 'update'}  {c['name']} {c['version']} -> {version}")
        if a.check:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            gh("release", "download", tag, "-R", repo, "-p", asset, "-p", "SHA256SUMS", "-D", tmp)
            got = Path(tmp) / asset
            sums = (Path(tmp) / "SHA256SUMS").read_text().split()
            expected = sums[sums.index(asset) - 1] if asset in sums else None
            if expected != sha256(got):
                sys.exit(f"{asset}: checksum does not match the release's SHA256SUMS")
            if plasmoid_version(got) != version:
                sys.exit(f"{asset}: metadata version {plasmoid_version(got)} != tag {tag}")
            old = PACKAGES / c["asset"]
            if old.exists() and old.name != asset:
                old.unlink()
            (PACKAGES / asset).write_bytes(got.read_bytes())
        c.update(
            version=version,
            asset=asset,
            sha256=sha256(PACKAGES / asset),
            commit=gh("api", f"repos/{repo}/commits/{tag}", "-q", ".sha").strip(),
        )
        c.pop("local_patch", None)
    if not a.check:
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    sys.exit(1 if a.check and behind else 0)


if __name__ == "__main__":
    main()
