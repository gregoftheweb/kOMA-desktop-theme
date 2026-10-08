"""apply-no-titlebars.sh adds kOMA's window rule beside the user's own rules.

Uses the real kreadconfig6/kwriteconfig6 against a temporary config folder; skipped
where they are not installed.
"""

import configparser
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "setup/apply-no-titlebars.sh"


@unittest.skipUnless(shutil.which("kwriteconfig6") and shutil.which("kreadconfig6"), "needs KDE Frameworks 6 config tools")
class NoTitlebarRuleTests(unittest.TestCase):
    def setUp(self):
        self.config = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.rules = self.config / "kwinrulesrc"

    def apply(self):
        # PATH holds only the two config tools, so qdbus6 is absent and the running
        # KWin is never touched
        tools = self.config / "bin"
        tools.mkdir(exist_ok=True)
        for tool in ("kwriteconfig6", "kreadconfig6"):
            target = tools / tool
            if not target.exists():
                target.symlink_to(shutil.which(tool))
        env = {"XDG_CONFIG_HOME": str(self.config), "HOME": str(self.config), "PATH": str(tools)}
        result = subprocess.run([shutil.which("bash"), str(SCRIPT)], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def read(self):
        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = str
        parser.read(self.rules)
        return parser

    def test_creates_the_rule_when_there_are_none(self):
        self.apply()
        rc = self.read()
        self.assertEqual(rc["General"]["rules"], "koma-no-titlebar")
        self.assertEqual(rc["General"]["count"], "1")
        self.assertEqual(rc["koma-no-titlebar"]["noborder"], "true")
        self.assertEqual(rc["koma-no-titlebar"]["noborderrule"], "2")
        self.assertEqual(rc["koma-no-titlebar"]["types"], "1")

    def test_keeps_the_users_rules(self):
        self.rules.write_text("[General]\ncount=2\nrules=abc,def\n\n[abc]\nDescription=mine\n\n[def]\nDescription=also mine\n")
        self.apply()
        rc = self.read()
        self.assertEqual(rc["General"]["rules"], "abc,def,koma-no-titlebar")
        self.assertEqual(rc["General"]["count"], "3")
        self.assertEqual(rc["abc"]["Description"], "mine")

    def test_running_twice_adds_the_rule_once(self):
        self.apply()
        self.apply()
        rc = self.read()
        self.assertEqual(rc["General"]["rules"], "koma-no-titlebar")
        self.assertEqual(rc["General"]["count"], "1")


if __name__ == "__main__":
    unittest.main()
