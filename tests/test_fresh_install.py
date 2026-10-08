"""Run the appearance install against an empty home, as on a freshly installed machine.

Plasma's tools are replaced by stubs that log their arguments, so this checks the
files the script writes and the packages it hands to Plasma, not Plasma itself.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STUBS = ("kpackagetool6", "kwriteconfig6", "qdbus6", "plasma-apply-lookandfeel", "plasma-apply-colorscheme")


class FreshHomeTests(unittest.TestCase):
    def setUp(self):
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.home, bin_dir, self.log = tmp / "home", tmp / "bin", tmp / "calls.log"
        self.home.mkdir()
        bin_dir.mkdir()
        for name in STUBS:
            stub = bin_dir / name
            stub.write_text(f'#!/bin/sh\necho "{name} $*" >>"{self.log}"\n')
            stub.chmod(0o755)
        # Papirus-Dark is the icon fallback the script requires
        papirus = self.home / ".local/share/icons/Papirus-Dark"
        papirus.mkdir(parents=True)
        (papirus / "index.theme").write_text("[Icon Theme]\n")
        self.path = f"{bin_dir}:{os.environ['PATH']}"

    def run_install(self, *args):
        home, log = self.home, self.log
        env = {
            "HOME": str(home),
            "PATH": self.path,
            "LANG": "C.UTF-8",
        }
        result = subprocess.run(
            ["bash", str(REPO / "setup/install-theme.sh"), *args],
            env=env, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return home / ".local/share", log.read_text()

    def test_installs_appearance_files_into_an_empty_home(self):
        data, _ = self.run_install()
        for wallpaper in ("kOMA-Lightcycles", "kOMA-Powder", "kOMA-River"):
            package = data / "wallpapers" / wallpaper
            self.assertTrue((package / "metadata.json").is_file(), wallpaper)
            self.assertTrue(any((package / "contents/images").iterdir()), wallpaper)
        self.assertTrue((data / "plasma/desktoptheme/kOMA/metadata.desktop").is_file())
        self.assertTrue((data / "color-schemes/kOMATronAqua.colors").is_file())
        self.assertTrue((data / "icons/plasma-monochrome-icons").is_dir())
        self.assertTrue((data / "icons/hicolor/scalable/apps/koma.svg").is_file())

    def test_hands_the_theme_packages_to_plasma(self):
        _, calls = self.run_install()
        self.assertIn("com.columbiafoundry.komacolors.plasmoid", calls)
        self.assertIn("com.columbiafoundry.koma.zip", calls)
        self.assertIn("KWin/Decoration", calls)

    def test_apply_selects_the_theme_and_color_scheme(self):
        _, calls = self.run_install("--apply")
        self.assertIn("plasma-apply-lookandfeel --apply com.columbiafoundry.koma", calls)
        self.assertIn("plasma-apply-colorscheme kOMATronAqua", calls)

    def test_running_twice_in_the_same_home_works(self):
        self.run_install("--apply")
        data, _ = self.run_install("--apply")
        self.assertTrue((data / "wallpapers/kOMA-Lightcycles/metadata.json").is_file())


if __name__ == "__main__":
    unittest.main()
