import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('operations', Path(__file__).resolve().parents[1] / 'setup/installer/operations.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RestoreTests(unittest.TestCase):
    def test_restore_preserves_later_edits_and_removes_owned_additions(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            engine = module.Installer(env={'HOME': str(home)})
            original = home / 'original'
            original.write_text('original')
            backup = home / 'backup'
            backup.write_text('original')
            before = module.digest(original)
            original.write_text('installed')
            addition = home / 'addition'
            addition.write_text('installed')
            edited = home / 'edited'
            edited.write_text('installed')
            after = module.digest(edited)
            edited.write_text('user edit')
            journal = home / 'record.json'
            journal.write_text(json.dumps({'files': {
                str(original): {'before': before, 'after': module.digest(original), 'backup': str(backup)},
                str(addition): {'before': None, 'after': module.digest(addition), 'backup': None},
                str(edited): {'before': None, 'after': after, 'backup': None}}}))
            result = engine.restore(journal)
            self.assertEqual(original.read_text(), 'original')
            self.assertFalse(addition.exists())
            self.assertEqual(edited.read_text(), 'user edit')
            self.assertEqual(result['restore_conflicts'], [str(edited)])
            engine.restore(journal)
            self.assertEqual(original.read_text(), 'original')

    def test_restore_puts_panels_back_with_the_shell_stopped_and_removes_the_installer(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            engine = module.Installer(env={'HOME': str(home)})
            calls = []
            engine.run = lambda command: calls.append(command)
            engine.config.mkdir(parents=True)
            panels = engine.config / 'plasma-org.kde.plasma.desktop-appletsrc'
            saved = home / 'saved-panels'
            saved.write_text('stock panels')
            before = module.digest(saved)
            panels.write_text('kOMA panels')
            after = module.digest(panels)
            panels.write_text('kOMA panels, rewritten by plasmashell')
            installer = engine.data / 'koma/installer'
            script = installer / 'setup/install-login-background.py'
            script.parent.mkdir(parents=True)
            script.write_text('installed')
            journal = home / 'record.json'
            journal.write_text(json.dumps({'files': {
                str(panels): {'before': before, 'after': after, 'backup': str(saved)},
                str(script): {'before': None, 'after': module.digest(script), 'backup': None}}}))
            result = engine.restore(journal)
            self.assertEqual(panels.read_text(), 'stock panels')
            self.assertEqual(result['restore_conflicts'], [])
            stop = calls.index(['systemctl', '--user', 'stop', 'plasma-plasmashell.service'])
            start = calls.index(['systemctl', '--user', 'start', 'plasma-plasmashell.service'])
            self.assertLess(stop, start)
            self.assertFalse(installer.exists())

    def test_restore_removes_package_folders_it_empties(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            engine = module.Installer(env={'HOME': str(home)})
            engine.run = lambda command: None
            widget = engine.data / 'plasma/plasmoids/com.columbiafoundry.example'
            added = widget / 'contents/ui/main.qml'
            added.parent.mkdir(parents=True)
            added.write_text('installed')
            other = engine.data / 'plasma/plasmoids/someone.elses/metadata.json'
            other.parent.mkdir(parents=True)
            other.write_text('keep')
            journal = home / 'record.json'
            journal.write_text(json.dumps({'files': {str(added): {'before': None, 'after': module.digest(added), 'backup': None}}}))
            engine.restore(journal)
            self.assertFalse(widget.exists())
            self.assertTrue(other.exists())
            self.assertTrue(engine.data.is_dir())

    def test_desktops_added_once_and_extras_preserved(self):
        from unittest.mock import patch
        for initial in (1, 4, 6):
            engine = module.Installer()
            state = [initial]
            calls = []
            def create(command):
                calls.append(command)
                state[0] += 1
            engine.run = create
            with patch.object(module.subprocess, 'check_output', side_effect=lambda *a, **k: str(state[0])):
                engine.ensure_desktops()
                engine.ensure_desktops()
            self.assertEqual(state[0], max(initial, 4))
            self.assertEqual(len(calls), max(0, 4 - initial))
            self.assertEqual([c[-2] for c in calls], [str(n) for n in range(initial, 4)])

    def test_inventory_recognizes_widgets_without_installer_history(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            engine = module.Installer(env={'HOME': str(home), 'XDG_DATA_DIRS': str(home / 'system')})
            launcher = next(c for c in engine.manifest if c['name'] == 'Launcher')
            metadata = engine.data / 'plasma/plasmoids' / launcher['id'] / 'metadata.json'
            metadata.parent.mkdir(parents=True)
            metadata.write_text(json.dumps({'KPlugin': {'Id': launcher['id'], 'Version': '9.0'}}))
            status = engine.current_status()
            self.assertEqual(status['installed'][launcher['id']], '9.0')
            self.assertFalse(status['choices']['audio'])
            self.assertFalse((engine.state / 'status.json').exists())
            self.assertIn('Launcher: installed 9.0', status['summary'])

    def test_all_bundled_packages_match_manifest(self):
        engine = module.Installer()
        for item in engine.manifest:
            self.assertEqual(module.digest(engine.repo / 'packages' / item['asset']), item['sha256'])


if __name__ == '__main__':
    unittest.main()
