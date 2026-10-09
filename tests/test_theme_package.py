"""The Global Theme carries copies of a few kOMA parts so it works on its own (KDE Store);
they must stay identical to their sources."""

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
THEME = REPO / "lookandfeel/com.columbiafoundry.koma/contents"


class ThemePackageTests(unittest.TestCase):
    def test_embedded_copies_match_their_sources(self):
        copies = {
            THEME / "colors": REPO / "color-schemes/kOMATronAqua.colors",
            THEME / "wallpaper/kOMA-Lightcycles.png": REPO / "wallpapers/kOMA-Lightcycles/contents/images/2560x1440.png",
        }
        for copy, source in copies.items():
            self.assertEqual(copy.read_bytes(), source.read_bytes(), f"{copy.relative_to(REPO)} differs from {source.relative_to(REPO)}")


if __name__ == "__main__":
    unittest.main()
