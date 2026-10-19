import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('border_operations', Path(__file__).resolve().parents[1] / 'setup/installer/operations.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BorderCompatibilityTests(unittest.TestCase):
    def test_factory_must_match_exact_kwin_patch(self):
        with tempfile.TemporaryDirectory() as directory:
            plugin = Path(directory) / 'effect.so'
            self.assertFalse(module.border_plugin_matches('6.7.5', plugin))
            plugin.write_bytes(b'\x00org.kde.kwin.EffectPluginFactory6.7.2\x00')
            self.assertFalse(module.border_plugin_matches('6.7.5', plugin))
            self.assertTrue(module.border_plugin_matches('6.7.2', plugin))
            plugin.write_bytes(b'\x00org.kde.kwin.EffectPluginFactory6.7.50\x00')
            self.assertFalse(module.border_plugin_matches('6.7.5', plugin))
            plugin.write_bytes(b'unknown metadata')
            self.assertFalse(module.border_plugin_matches('6.7.5', plugin))

    def test_existing_incompatible_plugin_triggers_rebuild(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = module.Installer(env={'HOME': directory})
            with patch.object(module.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, 'kwin 6.7.5-3\n')), patch.object(module, 'border_plugin_matches', return_value=False):
                self.assertEqual(engine.border_installation(), 'build')

    def test_matching_bundle_reinstalls_and_compatible_plugin_is_kept(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = module.Installer(env={'HOME': directory})
            version = json.loads((engine.repo / 'packages/focus-border.json').read_text())['kwin'].split('-')[0]
            with patch.object(module.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, 'kwin ' + version + '-99\n')):
                with patch.object(module, 'border_plugin_matches', return_value=False):
                    self.assertEqual(engine.border_installation(), 'package')
                with patch.object(module, 'border_plugin_matches', return_value=True):
                    self.assertEqual(engine.border_installation(), 'keep')

    def test_unknown_kwin_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = module.Installer(env={'HOME': directory})
            with patch.object(module.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1, '')):
                with self.assertRaisesRegex(RuntimeError, 'Cannot determine'):
                    engine.border_installation()
