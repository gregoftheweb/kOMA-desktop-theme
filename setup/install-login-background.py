#!/usr/bin/env python3
"""Install the kOMA login wallpaper for the active login manager.

SDDM: sets the background of the active SDDM theme (the theme itself is kept).
Plasma Login Manager: sets the greeter wallpaper in /etc/plasmalogin.conf.
"""

import argparse
import configparser
import datetime
import os
from pathlib import Path
import shutil
import json
import hashlib


def read_config(path):
    config = configparser.ConfigParser(interpolation=None, strict=False)
    config.optionxform = str
    config.read(path)
    return config


PLASMALOGIN_CONF = Path('/etc/plasmalogin.conf')
PLASMALOGIN_WALLPAPER = 'Greeter][Wallpaper][org.kde.image][General'


def login_manager():
    """'plasmalogin' or 'sddm', from the display-manager.service systemd links to."""
    unit = Path('/etc/systemd/system/display-manager.service')
    name = unit.resolve().name if unit.is_symlink() else ''
    if name.startswith('plasmalogin'):
        return 'plasmalogin'
    if name.startswith('sddm'):
        return 'sddm'
    return 'plasmalogin' if Path('/usr/bin/plasmalogin').exists() and not Path('/usr/bin/sddm').exists() else 'sddm'


def write_config(path, values):
    """Set keys in an INI/KConfig file, keeping everything else; values: {section: {key: value}}."""
    config = read_config(path)
    for section, keys in values.items():
        if not config.has_section(section):
            config.add_section(section)
        for key, value in keys.items():
            config.set(section, key, value)
    temporary = path.with_name(path.name + '.koma-new')
    with temporary.open('w') as output:
        config.write(output, space_around_delimiters=False)
    temporary.chmod(0o644)
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wallpaper', type=Path)
    parser.add_argument('--backup-dir', type=Path)
    parser.add_argument('--restore', type=Path)
    parser.add_argument('--theme', help='Override the detected active SDDM theme')
    args = parser.parse_args()
    if args.restore:
        if os.geteuid() != 0:
            parser.error('Restore requires administrator access')
        folder = args.restore.resolve()
        if folder.parent != Path('/var/backups/koma-sddm'):
            parser.error('Invalid backup location')
        entries = json.loads((folder / 'record.json').read_text())
        conflicts = []
        for name, entry in entries.items():
            target = Path(name)
            current = hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None
            if current == entry['before']:
                continue
            if current != entry['after']:
                conflicts.append(name)
                continue
            if entry['backup']:
                shutil.copy2(folder / entry['backup'], target)
            else:
                target.unlink(missing_ok=True)
        if conflicts:
            parser.error('Preserved later login background edits: ' + ', '.join(conflicts))
        print('Login background restored.')
        return
    root = Path(__file__).resolve().parent.parent
    image = args.wallpaper or root / 'wallpapers/kOMA-River/contents/images/1280x1280.jpg'
    if not image.is_file():
        parser.error(f'Wallpaper does not exist: {image}')
    manager = login_manager()
    if manager == 'sddm':
        theme = 'breeze'
        for path in [*sorted(Path('/usr/lib/sddm/sddm.conf.d').glob('*.conf')),
                     *sorted(Path('/etc/sddm.conf.d').glob('*.conf')), Path('/etc/sddm.conf')]:
            theme = read_config(path).get('Theme', 'Current', fallback=theme)
        theme = args.theme or theme
        if not theme or Path(theme).name != theme or theme in ('.', '..'):
            parser.error('Invalid SDDM theme name')
        directory = Path('/usr/share/sddm/themes') / theme
        if not directory.is_dir():
            parser.error(f'SDDM theme not installed: {theme}')
        settings = directory / 'theme.conf.user'
    else:
        settings = PLASMALOGIN_CONF
    if os.geteuid() != 0:
        parser.error('Run with sudo; login screen settings are system-wide')
    timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup = args.backup_dir or Path('/var/backups/koma-sddm') / timestamp
    if backup.resolve().parent != Path('/var/backups/koma-sddm'):
        parser.error('Invalid backup location')
    backup.mkdir(parents=True, exist_ok=False)
    destination = Path('/usr/share/backgrounds/koma') / ('login' + image.suffix.lower())
    entries = {}
    for target in (settings, destination):
        entries[str(target)] = {'before': hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None, 'backup': target.name if target.is_file() else None}
        if target.is_file():
            shutil.copy2(target, backup / target.name)
    (backup / 'target.txt').write_text(str(settings) + '\n' + str(destination) + '\n')
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(image, destination)
    destination.chmod(0o644)
    if manager == 'sddm':
        write_config(settings, {'General': {'background': str(destination), 'type': 'image'}})
        print(f'SDDM {theme} login wallpaper: {destination}')
    else:
        uri = destination.as_uri()
        write_config(settings, {'Greeter': {'WallpaperPluginId': 'org.kde.image'},
                                PLASMALOGIN_WALLPAPER: {'Image': uri, 'PreviewImage': uri}})
        print(f'Plasma Login Manager wallpaper: {destination}')
    for target in (settings, destination):
        entries[str(target)]['after'] = hashlib.sha256(target.read_bytes()).hexdigest()
    (backup / 'record.json').write_text(json.dumps(entries, indent=2) + '\n')
    print(f'Previous settings saved in {backup}')
    print('Applies at the next login screen. The running session was not restarted.')


if __name__ == '__main__':
    main()
