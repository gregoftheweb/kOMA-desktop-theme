"""The login background script writes Plasma Login Manager's nested KConfig groups."""

import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("login_background", Path(__file__).resolve().parents[1] / "setup/install-login-background.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

URI = "file:///usr/share/backgrounds/koma/login.jpg"


class PlasmaLoginConfigTests(unittest.TestCase):
    def write(self, existing):
        path = Path(self.enterContext(tempfile.TemporaryDirectory())) / "plasmalogin.conf"
        if existing is not None:
            path.write_text(existing)
        module.write_config(path, {"Greeter": {"WallpaperPluginId": "org.kde.image"},
                                   module.PLASMALOGIN_WALLPAPER: {"Image": URI, "PreviewImage": URI}})
        return path

    def test_creates_the_wallpaper_groups(self):
        text = self.write(None).read_text()
        self.assertIn("[Greeter]\nWallpaperPluginId=org.kde.image\n", text)
        self.assertIn(f"[Greeter][Wallpaper][org.kde.image][General]\nImage={URI}\nPreviewImage={URI}\n", text)

    def test_keeps_other_settings(self):
        text = self.write("[Autologin]\nUser=someone\n\n[Greeter]\nTheme=other\n").read_text()
        self.assertIn("[Autologin]\nUser=someone\n", text)
        self.assertIn("Theme=other\n", text)

    @unittest.skipUnless(shutil.which("kreadconfig6"), "needs kreadconfig6")
    def test_kde_reads_the_image_back(self):
        path = self.write(None)
        read = subprocess.run(["kreadconfig6", "--file", str(path), "--group", "Greeter", "--group", "Wallpaper",
                               "--group", "org.kde.image", "--group", "General", "--key", "Image"],
                              capture_output=True, text=True).stdout.strip()
        self.assertEqual(read, URI)


if __name__ == "__main__":
    unittest.main()
