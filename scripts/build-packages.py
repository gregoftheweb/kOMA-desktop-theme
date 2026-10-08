#!/usr/bin/env python3
"""Rebuild the packages this repository makes from its own sources:

    packages/com.columbiafoundry.koma.zip            Global Theme (lookandfeel/com.columbiafoundry.koma)
    packages/com.columbiafoundry.komacolors.plasmoid Colors widget (plasmoids/colors)

Only git-tracked files go in, with fixed timestamps, so the same sources always give
the same bytes. Run after changing either source; `make check` fails if they are stale.

    build-packages.py           rebuild
    build-packages.py --check   exit 1 if a package differs from its sources
"""

import argparse
import io
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    "packages/com.columbiafoundry.koma.zip": ("lookandfeel/com.columbiafoundry.koma", ["metadata.json", "LICENSE", "contents"]),
    "packages/com.columbiafoundry.komacolors.plasmoid": ("plasmoids/colors", ["metadata.json", "LICENSE", "README.md", "contents"]),
}
EPOCH = (2026, 1, 1, 0, 0, 0)


def tracked(base, parts):
    out = subprocess.run(["git", "ls-files", "-z", "--", *parts], cwd=ROOT / base, check=True, capture_output=True).stdout
    return sorted(p for p in out.decode().split("\0") if p)


def build(base, parts):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name in tracked(base, parts):
            path = ROOT / base / name
            info = zipfile.ZipInfo(name, EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if path.stat().st_mode & 0o111 else 0o644) << 16
            z.writestr(info, path.read_bytes())
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    stale = []
    for out, (base, parts) in PACKAGES.items():
        data = build(base, parts)
        target = ROOT / out
        if target.exists() and target.read_bytes() == data:
            continue
        stale.append(out)
        if not a.check:
            target.write_bytes(data)
            print(f"built {out}")
    if a.check and stale:
        print("stale (run scripts/build-packages.py): " + ", ".join(stale), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
