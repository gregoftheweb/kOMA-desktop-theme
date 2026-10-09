#!/usr/bin/env python3
"""Render the Global Theme's preview images (what System Settings shows for kOMA):

    previews/preview.png             600x337    the theme's tile
    previews/fullscreenpreview.jpg   1920x1080  its full-screen preview
    previews/splash.png              300x169    the Splash Screen page

The desktop previews come from docs/screenshots/desktop.png (the primary kOMA image);
the splash one renders the real splash offscreen, as it looks after a full install.
Needs Pillow and Qt 6's qml runner.
"""

import os
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
THEME = REPO / "lookandfeel/com.columbiafoundry.koma/contents"
OUT = THEME / "previews"

GRAB = """import QtQuick
import QtQuick.Window
Window {
    width: 1920; height: 1080; visible: true
    Loader { id: l; anchors.fill: parent; source: "%s" }
    Timer { interval: 1500; running: true; onTriggered: l.item.grabToImage(function(r) { r.saveToFile("%s"); Qt.quit(); }) }
}
"""


def splash(tmp):
    # a data folder holding the kOMA icon, so the splash shows its installed look
    data = tmp / "data/icons/hicolor/scalable/apps"
    data.mkdir(parents=True)
    (data / "koma.svg").write_bytes((REPO / "branding/koma.svg").read_bytes())
    shot = tmp / "splash.png"
    (tmp / "grab.qml").write_text(GRAB % ((THEME / "splash/Splash.qml").as_uri(), shot))
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen", XDG_DATA_HOME=str(tmp / "data"))
    subprocess.run(["/usr/lib/qt6/bin/qml", str(tmp / "grab.qml")], env=env, check=True, timeout=30)
    return Image.open(shot).convert("RGB")


def main():
    OUT.mkdir(exist_ok=True)
    desktop = Image.open(REPO / "docs/screenshots/desktop.png").convert("RGB")
    desktop.resize((600, 337), Image.Resampling.LANCZOS).save(OUT / "preview.png", optimize=True)
    desktop.resize((1920, 1080), Image.Resampling.LANCZOS).save(OUT / "fullscreenpreview.jpg", quality=90, optimize=True)
    with tempfile.TemporaryDirectory() as tmp:
        splash(Path(tmp)).resize((300, 169), Image.Resampling.LANCZOS).save(OUT / "splash.png", optimize=True)
    for f in sorted(OUT.iterdir()):
        print(f.relative_to(REPO))


if __name__ == "__main__":
    main()
