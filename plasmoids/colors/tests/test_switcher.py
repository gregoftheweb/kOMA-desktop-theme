import configparser
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('switcher', str(ROOT / 'contents/code/koma-colors'))
spec = importlib.util.spec_from_loader(loader.name, loader)
switcher = importlib.util.module_from_spec(spec)
loader.exec_module(switcher)


class SwitchingTests(unittest.TestCase):
    def test_missing_scheme_does_not_write_preferences(self):
        with patch.object(switcher, 'scheme_path', return_value=None), patch.object(switcher, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'Missing color scheme'):
                switcher.set_palette(switcher.PALETTES[0])
            run.assert_not_called()

    def test_command_failure_restores_previous_preferences(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'kdeglobals'
            original = b'[General]\nColorScheme=previous\n[Unrelated]\nSetting=keep\n'
            config.write_bytes(original)
            def failed_run(*args):
                if args[0] == 'kwriteconfig6':
                    config.write_text('[General]\n')
                    return ''
                raise RuntimeError('simulated apply failure')
            with patch.dict(os.environ, {'XDG_CONFIG_HOME': directory, 'XDG_CACHE_HOME': directory}), \
                    patch.object(switcher, 'scheme_path', return_value=Path(directory)), \
                    patch.object(switcher, 'current', return_value='previous'), \
                    patch.object(switcher, 'run', side_effect=failed_run):
                with self.assertRaisesRegex(RuntimeError, 'simulated apply failure'):
                    switcher.set_palette(switcher.PALETTES[0])
            self.assertEqual(config.read_bytes(), original)

    def test_schemes_match_swatches_and_have_readable_selection_text(self):
        def luminance(rgb):
            values = [v / 255 for v in rgb]
            values = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values]
            return sum(v * weight for v, weight in zip(values, (.2126, .7152, .0722)))
        for palette in switcher.PALETTES:
            with self.subTest(palette=palette['id']):
                c = configparser.ConfigParser()
                c.read(ROOT.parents[1] / 'color-schemes' / (palette['scheme'] + '.colors'))
                bg = [int(v) for v in c['Colors:Selection']['BackgroundNormal'].split(',')]
                fg = [int(v) for v in c['Colors:Selection']['ForegroundNormal'].split(',')]
                self.assertEqual(bg, [int(palette['color'][i:i + 2], 16) for i in (1, 3, 5)])
                self.assertGreaterEqual((luminance(bg) + .05) / (luminance(fg) + .05), 4.5)
                self.assertEqual(c['Colors:View']['BackgroundNormal'], '10,13,18')


if __name__ == '__main__':
    unittest.main()
