"""Shared user-level installation operations; no terminal UI dependencies."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid

REPO = Path(__file__).resolve().parents[2]
CONFIG_NAMES = ['kdeglobals', 'plasmarc', 'kwinrc', 'kcminputrc', 'ksplashrc',
                'plasma-org.kde.plasma.desktop-appletsrc', 'plasmashellrc',
                'kdedefaults', 'kglobalshortcutsrc', 'kscreenlockerrc']


def digest(path):
    if path.is_symlink():
        return 'link:' + os.readlink(path)
    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    return None


class Installer:
    def __init__(self, repo=REPO, env=None, emit=lambda message: None):
        self.repo = Path(repo)
        self.env = dict(os.environ if env is None else env)
        home = Path(self.env['HOME'])
        self.data = Path(self.env.get('XDG_DATA_HOME', home / '.local/share'))
        self.config = Path(self.env.get('XDG_CONFIG_HOME', home / '.config'))
        self.state = Path(self.env.get('XDG_STATE_HOME', home / '.local/state')) / 'koma'
        self.emit = emit
        self.manifest = json.loads((self.repo / 'packages/manifest.json').read_text())

    def inventory(self):
        """Inspect existing installations without requiring an installer journal."""
        import configparser
        def config(path):
            parser = configparser.ConfigParser(interpolation=None, strict=False)
            parser.optionxform = str
            try:
                parser.read(path)
            except (OSError, configparser.Error):
                pass
            return parser
        def get(parser, section, key, default=''):
            return parser.get(section, key, fallback=default)
        data_roots = [self.data] + [Path(p) for p in self.env.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':') if p]
        installed = {}
        for c in self.manifest:
            for base in data_roots:
                try:
                    metadata = json.loads((base / 'plasma/plasmoids' / c['id'] / 'metadata.json').read_text())
                    if metadata['KPlugin']['Id'] == c['id']:
                        installed[c['id']] = str(metadata['KPlugin']['Version'])
                        break
                except (OSError, ValueError, KeyError):
                    continue
        kde = config(self.config / 'kdeglobals')
        kwin = config(self.config / 'kwinrc')
        plasma = config(self.config / 'plasma-org.kde.plasma.desktop-appletsrc')
        views = config(self.config / 'plasmashellrc')
        core = [c for c in self.manifest if not c.get('optional')]
        choices = {'profile': 'full' if all(c['id'] in installed for c in core) else 'appearance'}
        for option in ('music', 'weather', 'power', 'audio'):
            choices[option] = any(c['id'] in installed for c in self.manifest if c.get('option', 'music' if c.get('optional') else '') == option)
        appearance = get(kde, 'KDE', 'LookAndFeelPackage') == 'com.columbiafoundry.koma'
        icons = get(kde, 'Icons', 'Theme') == 'plasma-monochrome-icons'
        panels = []
        for section in plasma.sections():
            if get(plasma, section, 'plugin') != 'org.kde.panel':
                continue
            ident = section.split('][')[-1]
            order = get(plasma, section + '][General', 'AppletOrder').split(';')
            ids = [get(plasma, section + '][Applets][' + i, 'plugin') for i in order]
            height = get(views, 'PlasmaViews][Panel ' + ident + '][Defaults', 'thickness')
            panels.append(get(plasma, section, 'location') == '3' and height == '32' and
                          all(c['id'] in ids for c in core) and 'org.kde.plasma.digitalclock' in ids and
                          'com.github.idityage.spacerdivider' in ids and ids.count('org.kde.plasma.panelspacer') >= 2)
        choices['panels'] = bool(panels) and all(panels)
        tiling = get(kwin, 'Plugins', 'krohnkiteEnabled') == 'true'
        borders = get(kwin, 'Plugins', 'kwin4_effect_shapecornersEnabled') == 'true'
        choices['tiling'] = tiling and borders
        shortcuts = config(self.config / 'kglobalshortcutsrc')
        expected = [('services][koma-launcher.desktop', '_launch', 'Meta+Space'),
                    ('services][koma-keybindings.desktop', '_launch', 'Meta+K'),
                    ('services][koma-browser.desktop', '_launch', 'Meta+Shift+Return'),
                    ('kwin', 'Window Close', 'Meta+W'),
                    ('kwin', 'Window Fullscreen', 'Meta+F')]
        def key(value):
            return frozenset(value.lower().replace('enter', 'return').split('+'))
        matches = 0
        for section, action, chord in expected:
            active = get(shortcuts, section, action).split(',')[0].split('\\t')
            if key(chord) in {key(k) for k in active}:
                matches += 1
        choices['hotkeys'] = matches == len(expected)
        lock = config(self.config / 'kscreenlockerrc')
        lock_image = get(lock, 'Greeter][Wallpaper][org.kde.image][General', 'Image')
        lock_active = 'kOMA-Tron-1/' in lock_image and Path(lock_image.removeprefix('file://')).is_file()
        sddm_theme = 'breeze'
        for file in [*sorted(Path('/usr/lib/sddm/sddm.conf.d').glob('*.conf')), *sorted(Path('/etc/sddm.conf.d').glob('*.conf')), Path('/etc/sddm.conf')]:
            sddm_theme = get(config(file), 'Theme', 'Current', sddm_theme)
        login_image = get(config(Path('/usr/share/sddm/themes') / sddm_theme / 'theme.conf.user'), 'General', 'background')
        login_active = login_image.startswith('/usr/share/backgrounds/koma/') and Path(login_image).is_file()
        choices['backgrounds'] = lock_active and login_active
        summary = ['Live inventory: kOMA appearance ' + ('active' if appearance else 'not active') + '; Plasma Monochrome ' + ('active' if icons else 'not active')]
        summary += [c['name'] + ': ' + ('installed ' + installed[c['id']] if c['id'] in installed else 'not installed') for c in self.manifest]
        summary += ['kOMA panels: ' + ('detected' if choices['panels'] else 'different or not configured'),
                    'kOMA core hotkeys: ' + str(matches) + '/' + str(len(expected)) + ' matched',
                    'Krohnkite: ' + ('enabled' if tiling else 'disabled') + '; colored borders: ' + ('enabled' if borders else 'disabled'),
                    'Login background: ' + ('kOMA' if login_active else 'other') + '; lock background: ' + ('kOMA' if lock_active else 'other')]
        return {'choices': choices, 'summary': summary, 'installed': installed, 'appearance': appearance, 'icons': icons}

    def current_status(self):
        live = self.inventory()
        path = self.state / 'status.json'
        if not path.exists():
            live['summary'].append('Existing setup detected directly; no installer backup history yet.')
            return live
        try:
            record = json.loads(path.read_text())
        except (ValueError, OSError):
            live['summary'].append('Saved history cannot be read; showing live inventory.')
            return live
        live['summary'].insert(0, 'Last operation: ' + record.get('status', 'unknown') + ' (' + record.get('id', 'unknown') + ')')
        if record.get('error'):
            live['summary'].append('Previous installation failed; backup retained. Pending selections kept for retry.')
            live['choices'].update(record.get('plan', {}))
        return live

    def plan(self, profile='appearance', music=False, panels=False, hotkeys=False, tiling=False, weather=False, power=False, audio=False, backgrounds=False):
        previous_hotkeys = next((p.parent / 'hotkeys-undo.json' for p in self.backups() if (p.parent / 'hotkeys-undo.json').exists()), None)
        restore_hotkeys = str(previous_hotkeys) if previous_hotkeys and not hotkeys else None
        components = [c for c in self.manifest if profile == 'full' and
                      (not c.get('optional') or {'weather': weather, 'power': power, 'audio': audio, 'music': music, 'panels': panels}.get(c.get('option', 'music'), False))]
        errors = []
        system_packages = []
        if backgrounds and not shutil.which('pkexec', path=self.env.get('PATH')):
            errors.append('Login background installation requires pkexec.')
        if backgrounds and not Path('/usr/share/sddm/themes').is_dir():
            errors.append('Login background installation requires SDDM.')
        if panels and profile != 'full':
            errors.append('Choose Full desktop components to install kOMA panels.')
        if hotkeys and subprocess.run(['python3', '-c', 'import dbus'], env=self.env, capture_output=True).returncode:
            errors.append('Install python-dbus before switching hotkeys.')
        if power and profile == 'full' and subprocess.run(['python3', '-c', 'import dbus; import gi'], env=self.env, capture_output=True).returncode:
            errors.append('Power Control requires python-dbus and python-gobject (dbus-python and PyGObject).')
        if audio and profile == 'full' and not shutil.which('pactl', path=self.env.get('PATH')):
            errors.append('Audio Control requires pactl (Arch/EndeavourOS: libpulse).')
        for name in ['bash', 'python3', 'tar', 'sha256sum', 'kpackagetool6',
                     'plasma-apply-lookandfeel', 'plasma-apply-colorscheme',
                     'kwriteconfig6', 'qdbus6']:
            if not shutil.which(name, path=self.env.get('PATH')):
                errors.append('Missing command: ' + name)
        if not any((p / 'icons/Papirus-Dark/index.theme').is_file() for p in
                   [self.data, Path('/usr/local/share'), Path('/usr/share')]):
            if shutil.which('pacman', path=self.env.get('PATH')) and shutil.which('pkexec', path=self.env.get('PATH')):
                system_packages.append('papirus-icon-theme')
            else:
                errors.append('Automatic Papirus installation requires pacman and pkexec on this system.')
        if tiling:
            effect = json.loads((self.repo / 'packages/focus-border.json').read_text())
            if digest(self.repo / 'packages' / effect['asset']) != effect['sha256']:
                errors.append('Focus-border package checksum failed.')
            if not Path('/usr/lib/qt6/plugins/kwin/effects/plugins/kwin4_effect_shapecorners.so').exists():
                version = subprocess.run(['pacman', '-Q', 'kwin'], env=self.env, capture_output=True, text=True)
                if version.stdout.strip() != 'kwin ' + effect['kwin']:
                    if not shutil.which('makepkg', path=self.env.get('PATH')) or not shutil.which('konsole', path=self.env.get('PATH')):
                        errors.append('Building borders requires Arch/EndeavourOS makepkg and Konsole.')
                if not shutil.which('pkexec', path=self.env.get('PATH')):
                    errors.append('Missing pkexec for system border-effect installation.')
            krohnkite = json.loads((self.repo / 'packages/krohnkite.json').read_text())
            if digest(self.repo / 'packages' / krohnkite['asset']) != krohnkite['sha256']:
                errors.append('Krohnkite package checksum failed.')
        for c in components:
            archive = self.repo / 'packages' / c['asset']
            if digest(archive) != c['sha256']:
                errors.append('Missing or invalid package: ' + c['asset'])
        icon = self.repo / 'icons/plasma-monochrome-icons.tar.gz'
        expected = (self.repo / 'icons/plasma-monochrome-icons.tar.gz.sha256').read_text().split()[0]
        if digest(icon) != expected:
            errors.append('Plasma Monochrome archive checksum failed.')
        if hotkeys:
            inspection = subprocess.run(['python3', str(self.repo / 'setup/keybindings/apply.py')], env=self.env, capture_output=True, text=True)
            if inspection.returncode:
                errors.append('Hotkey inspection failed: ' + inspection.stderr.strip())
            self.state.mkdir(parents=True, exist_ok=True)
            (self.state / 'hotkey-review.txt').write_text(inspection.stdout + inspection.stderr)
            conflicts = inspection.stdout.split('Keys taken from other actions:')[-1].strip().splitlines() if 'Keys taken from other actions:' in inspection.stdout else []
        else:
            conflicts = []
        return {'conflicts': conflicts, 'profile': profile, 'music': music, 'weather': weather, 'power': power, 'audio': audio, 'backgrounds': backgrounds, 'panels': panels, 'hotkeys': hotkeys, 'restore_hotkeys': restore_hotkeys, 'tiling': tiling, 'components': components,
                'system_packages': system_packages, 'errors': errors, 'changes':
                (['Install missing system packages: ' + ', '.join(system_packages) + ' (administrator authentication required)'] if system_packages else []) + ['Install and enable kOMA appearance',
                'Install Plasma Monochrome Icons', ('Replace panels: top, 32 px, clock between spacers, hidden tray items; ensure at least 4 desktops' if panels else 'Preserve existing panels'), ('Apply kOMA hotkeys; replace conflicting assignments' if hotkeys else ('Restore previous hotkeys; preserve later edits' if restore_hotkeys else 'Preserve existing hotkeys'))] +
                ['Install ' + c['name'] + ' ' + c['version'] for c in components] + (['Apply kOMA login and lock screen backgrounds (administrator authentication required for login screen)'] if backgrounds else []) + (['Install and enable Krohnkite 0.9.9.2 with kOMA defaults', 'Enable colored borders; install or build for this KWin (administrator authentication required)'] if tiling else []),
                'remaining': []}

    def deploy_installer(self):
        destination = self.data / 'koma/installer'
        if destination.resolve() != self.repo.resolve():
            shutil.copytree(self.repo, destination, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('.git', 'dist', '__pycache__', '*.pyc', 'ref', 'trial', 'dev', 'tests', 'undo.json*', 'backup'))
        self.emit('kOMA Installer is available from the Launcher menu.')

    def ensure_desktops(self, minimum=4):
        manager = ['qdbus6', 'org.kde.KWin', '/VirtualDesktopManager']
        def count():
            return int(subprocess.check_output(manager + ['org.kde.KWin.VirtualDesktopManager.count'], env=self.env, text=True).strip())
        before = count()
        for position in range(before, minimum):
            self.run(manager + ['org.kde.KWin.VirtualDesktopManager.createDesktop', str(position), 'Desktop ' + str(position + 1)])
        after = count()
        if after < minimum:
            raise RuntimeError('Could not create the required virtual desktops.')
        self.emit('Virtual desktops: ' + str(after) + ' (' + str(max(0, after - before)) + ' added).')

    def roots(self, components):
        roots = [self.config / name for name in CONFIG_NAMES]
        roots.append(self.data / 'koma/installer')
        roots += [self.data / 'icons/plasma-monochrome-icons',
                  self.data / 'icons/hicolor/scalable/apps/koma.svg',
                  self.data / 'plasma/desktoptheme/kOMA',
                  self.data / 'plasma/look-and-feel/com.columbiafoundry.koma',
                  self.data / 'aurorae/themes/com.columbiafoundry.komaborder',
                  self.data / 'wallpapers/kOMA-Tron-1',
                  self.data / 'wallpapers/kOMA-Lightcycles',
                  self.data / 'plasma/plasmoids/com.columbiafoundry.komacolors']
        roots += [self.data / 'color-schemes' / p.name for p in (self.repo / 'color-schemes').glob('kOMA*.colors')]
        roots += [self.data / 'plasma/plasmoids' / c['id'] for c in components]
        return roots

    @staticmethod
    def files(roots):
        paths = set()
        for root in roots:
            if root.is_dir() and not root.is_symlink():
                paths.update(p for p in root.rglob('*') if p.is_file() or p.is_symlink())
            elif root.exists() or root.is_symlink():
                paths.add(root)
        return paths

    def save(self, path, record):
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix('.tmp')
        tmp.write_text(json.dumps(record, indent=2) + '\n')
        tmp.replace(path)

    def run(self, args):
        self.emit('Running: ' + ' '.join(str(x) for x in args))
        output = []
        with subprocess.Popen(args, env=self.env, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True) as process:
            for line in process.stdout:
                output.append(line.rstrip())
                self.emit(line.rstrip())
            if process.wait():
                raise RuntimeError('Command failed: ' + str(args[0]) + '\n' + '\n'.join(output[-12:]))

    def install(self, plan):
        if plan['errors']:
            raise RuntimeError('\n'.join(plan['errors']))
        if os.geteuid() == 0:
            raise RuntimeError('Run the installer as your desktop user, not root.')
        roots = self.roots(plan['components'])
        if plan.get('hotkeys'):
            roots.append(Path(self.env['HOME']) / '.local/bin/komalauncher')
            roots.append(Path(self.env['HOME']) / '.local/bin/koma-browser')
            # Only generated launcher files belong to this operation.
            import importlib.util
            spec = importlib.util.spec_from_file_location('koma_keys', self.repo / 'setup/keybindings/apply.py')
            keys = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(keys)
            roots.extend(self.data / 'applications' / keys.action_id(row)[0]
                         for row in keys.load_rows() if row['kind'] in ('cmd', 'koma'))
        if plan.get('tiling'):
            roots.append(self.data / 'kwin/scripts/krohnkite')
        before = self.files(roots)
        run_id = time.strftime('%Y%m%d-%H%M%S-') + uuid.uuid4().hex[:8]
        folder = self.state / 'backups' / run_id
        folder.mkdir(parents=True)
        record = {'id': run_id, 'status': 'running', 'plan': plan,
                  'roots': [str(p) for p in roots], 'files': {}}
        for index, path in enumerate(sorted(before)):
            saved = folder / 'files' / str(index)
            saved.parent.mkdir(exist_ok=True)
            shutil.copy2(path, saved, follow_symlinks=False)
            record['files'][str(path)] = {'before': digest(path), 'backup': str(saved)}
        journal = folder / 'record.json'
        self.save(journal, record)
        self.emit('Backup: ' + run_id)
        try:
            if plan.get('system_packages'):
                self.emit('Installing required system packages; approve the administrator dialog.')
                self.run(['pkexec', 'pacman', '-S', '--needed', '--noconfirm'] + plan['system_packages'])
                if 'papirus-icon-theme' in plan['system_packages'] and not Path('/usr/share/icons/Papirus-Dark/index.theme').is_file():
                    raise RuntimeError('Papirus installation did not provide the required Papirus-Dark fallback.')
            for c in plan['components']:
                target = self.data / 'plasma/plasmoids' / c['id']
                if target.exists():
                    previous = folder / 'replaced-packages' / c['id']
                    previous.parent.mkdir(exist_ok=True)
                    shutil.move(str(target), str(previous))
                self.run(['kpackagetool6', '--type', 'Plasma/Applet', '--install',
                          str(self.repo / 'packages' / c['asset'])])
            self.run(['bash', str(self.repo / 'setup/install-theme.sh'), '--apply'])
            result = subprocess.check_output(['kreadconfig6', '--file', 'kdeglobals',
                     '--group', 'Icons', '--key', 'Theme'], env=self.env, text=True).strip()
            if result != 'plasma-monochrome-icons':
                raise RuntimeError('Icon activation verification failed: ' + result)
            for c in plan['components']:
                metadata = self.data / 'plasma/plasmoids' / c['id'] / 'metadata.json'
                if not metadata.is_file() or json.loads(metadata.read_text())['KPlugin']['Version'] != c['version']:
                    raise RuntimeError('Widget version verification failed: ' + c['name'])
            if plan.get('tiling'):
                effect = json.loads((self.repo / 'packages/focus-border.json').read_text())
                if not Path('/usr/lib/qt6/plugins/kwin/effects/plugins/kwin4_effect_shapecorners.so').exists():
                    version = subprocess.run(['pacman', '-Q', 'kwin'], env=self.env, capture_output=True, text=True)
                    if version.stdout.strip() == 'kwin ' + effect['kwin']:
                        self.emit('Installing the border effect: approve the administrator dialog.')
                        self.run(['pkexec', 'pacman', '-U', '--needed', '--noconfirm', str(self.repo / 'packages' / effect['asset'])])
                    else:
                        self.emit('A terminal will open to build borders for this KWin version; enter sudo password there.')
                        self.run(['konsole', '--separate', '--nofork', '-e', 'bash', str(self.repo / 'setup/install-focus-border.sh')])
                        if not Path('/usr/lib/qt6/plugins/kwin/effects/plugins/kwin4_effect_shapecorners.so').exists():
                            raise RuntimeError('Border build/install did not complete; see the build terminal output.')
                self.run(['bash', str(self.repo / 'setup/apply-focus-border.sh')])
                metadata = json.loads((self.repo / 'packages/krohnkite.json').read_text())
                target = self.data / 'kwin/scripts/krohnkite'
                installed = target / 'metadata.json'
                same = installed.is_file() and json.loads(installed.read_text())['KPlugin']['Version'] == metadata['version']
                if not same:
                    if target.exists():
                        previous = folder / 'replaced-packages/krohnkite'
                        previous.parent.mkdir(exist_ok=True)
                        shutil.move(str(target), str(previous))
                    self.run(['kpackagetool6', '--type', 'KWin/Script', '--install', str(self.repo / 'packages' / metadata['asset'])])
                defaults = {'screenGapBetween': 10, 'screenGapBottom': 10, 'screenGapLeft': 10,
                            'screenGapRight': 10, 'screenGapTop': 10, 'spiralLayoutOrder': 1,
                            'tileLayoutOrder': 2, 'binaryTreeLayoutOrder': 3, 'columnsLayoutOrder': 4,
                            'monocleLayoutOrder': 5, 'floatingClass': 'org.keepassxc.KeePassXC,org.kde.kcalc,org.kde.plasma-systemmonitor,pavucontrol'}
                for name in ['cascade', 'floating', 'quarter', 'spread', 'stacked', 'stair', 'threeColumn']:
                    defaults[name + 'LayoutOrder'] = 0
                for key, value in defaults.items():
                    self.run(['kwriteconfig6', '--file', 'kwinrc', '--group', 'Script-krohnkite', '--key', key, str(value)])
                self.run(['kwriteconfig6', '--file', 'kwinrc', '--group', 'Plugins', '--key', 'krohnkiteEnabled', 'true'])
                self.run(['qdbus6', 'org.kde.KWin', '/KWin', 'reconfigure'])
                check = subprocess.run(['qdbus6', 'org.kde.KWin', '/Scripting', 'org.kde.kwin.Scripting.isScriptLoaded', 'krohnkite'], env=self.env, capture_output=True, text=True)
                record['tiling_active'] = check.returncode == 0 and check.stdout.strip() == 'true'
                if not record['tiling_active']:
                    plan['remaining'].append('Krohnkite enabled; sign out/in, then reopen to verify activation.')
                self.emit('Krohnkite: ' + ('active' if record['tiling_active'] else 'enabled; activation pending'))
            if plan.get('restore_hotkeys'):
                self.env['KOMA_SHORTCUT_UNDO'] = plan['restore_hotkeys']
                self.run(['python3', str(self.repo / 'setup/keybindings/apply.py'), '--undo'])
                self.emit('Previous hotkeys restored; later edits preserved.')
            if plan.get('hotkeys'):
                helper = Path(self.env['HOME']) / '.local/bin/komalauncher'
                helper.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.repo / 'setup/keybindings/komalauncher', helper)
                helper.chmod(0o755)
                browser_helper = helper.with_name('koma-browser')
                shutil.copy2(self.repo / 'setup/keybindings/koma-browser', browser_helper)
                browser_helper.chmod(0o755)
                undo = folder / 'hotkeys-undo.json'
                record['hotkey_undo'] = str(undo)
                self.env['KOMA_SHORTCUT_UNDO'] = str(undo)
                self.run(['python3', str(self.repo / 'setup/keybindings/apply.py'), '--apply'])
            if plan.get('panels'):
                self.ensure_desktops()
                from panels import script
                data_roots = [self.data] + [Path(p) for p in self.env.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':') if p]
                audio = any((p / 'plasma/plasmoids/com.columbiafoundry.komaaudiocontrol/metadata.json').is_file() for p in data_roots)
                output = subprocess.check_output(['qdbus6', 'org.kde.plasmashell',
                    '/PlasmaShell', 'org.kde.PlasmaShell.evaluateScript',
                    script(plan['components'], plan['music'], plan.get('weather', False), plan.get('power', False), audio=audio)], env=self.env, text=True,
                    stderr=subprocess.STDOUT)
                if 'Error' in output or 'error' in output:
                    raise RuntimeError('Panel application failed: ' + output)
                self.emit('Top panels applied; existing known tray items hidden.')
            if plan.get('backgrounds'):
                system_backup = '/var/backups/koma-sddm/' + run_id
                record['login_background_backup'] = system_backup
                self.run(['pkexec', 'python3', str(self.repo / 'setup/install-login-background.py'), '--backup-dir', system_backup])
                image = (self.data / 'wallpapers/kOMA-Tron-1/contents/images/1280x1280.jpg').as_uri()
                self.run(['kwriteconfig6', '--file', 'kscreenlockerrc', '--group', 'Greeter', '--key', 'WallpaperPlugin', 'org.kde.image'])
                for key in ('Image', 'PreviewImage'):
                    self.run(['kwriteconfig6', '--file', 'kscreenlockerrc', '--group', 'Greeter', '--group', 'Wallpaper', '--group', 'org.kde.image', '--group', 'General', '--key', key, image])
                self.emit('Login and lock screen backgrounds applied; visible next time those screens open.')
            self.deploy_installer()
            if plan.get('panels'):
                # Give Plasma time to publish the new panel's reserved screen area
                # before KWin recalculates placement and window decoration state.
                time.sleep(0.5)
                self.run(['qdbus6', 'org.kde.KWin', '/KWin', 'org.kde.KWin.reconfigure'])
                self.emit('Window manager refreshed for the new top panel.')
            record['status'] = 'complete'
            self.emit('Appearance verified; Plasma Monochrome is active.')
        except Exception as error:
            record['status'] = 'failed'
            record['error'] = str(error)
            raise
        finally:
            for path in before | self.files(roots):
                entry = record['files'].setdefault(str(path), {'before': None, 'backup': None})
                entry['after'] = digest(path)
            self.save(journal, record)
            self.save(self.state / 'status.json', record)
        return record

    def backups(self):
        return sorted((self.state / 'backups').glob('*/record.json'), reverse=True)

    def restore(self, journal):
        record = json.loads(Path(journal).read_text())
        conflicts = []
        if record.get('login_background_backup'):
            self.run(['pkexec', 'python3', str(self.repo / 'setup/install-login-background.py'), '--restore', record['login_background_backup']])
        if record.get('hotkey_undo') and Path(record['hotkey_undo']).exists():
            self.env['KOMA_SHORTCUT_UNDO'] = record['hotkey_undo']
            self.run(['python3', str(self.repo / 'setup/keybindings/apply.py'), '--undo'])
            # The live shortcut service owns this file; action-level restore preserves later edits.
            record['files'].pop(str(self.config / 'kglobalshortcutsrc'), None)
        for name, entry in record['files'].items():
            path = Path(name)
            current = digest(path)
            if current == entry['before']:
                continue
            if current != entry.get('after'):
                conflicts.append(name)
                continue
            if path.exists() or path.is_symlink():
                path.unlink()
            if entry['backup']:
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(entry['backup'], path, follow_symlinks=False)
        record['restore_conflicts'] = conflicts
        record['status'] = 'restore-conflicts' if conflicts else 'restored'
        self.save(Path(journal), record)
        self.save(self.state / 'status.json', record)
        self.emit('Restore finished. Sign out and back in to reload restored desktop settings.')
        for name in conflicts:
            self.emit('Preserved later edit: ' + name)
        return record
