#!/usr/bin/env python3
"""kOMA terminal setup app. Arrow keys, Space, Enter, Escape."""
import argparse
import curses
import json
import queue
import threading
from operations import Installer

LOGO = [' _    ___  __  __    _ ', '| |__/ _ \\|  \\/  |  / \\', '| / / | | | |\\/| | / _ \\', '|_\\_\\___/|_|  |_|/_/ \\_\\']


def ui(screen):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)
    installer = Installer()
    saved = installer.current_status()
    choices = saved['choices']
    profile = choices.get('profile', 'appearance')
    music = choices.get('music', False)
    weather = choices.get('weather', False)
    power = choices.get('power', False)
    audio = choices.get('audio', False)
    backgrounds = choices.get('backgrounds', False)
    panels = choices.get('panels', False)
    hotkeys = True  # kOMA (Omarchy) shortcuts by default; the user can choose Keep my hotkeys
    tiling = choices.get('tiling', False)
    stage = 'welcome'
    selected = 0
    logs = []
    events = queue.Queue()
    busy = False
    result = None
    backups = []
    plan = None

    def worker(action):
        installer.emit = lambda line: events.put(('log', line))
        try:
            events.put(('done', action()))
        except Exception as error:
            events.put(('error', str(error)))

    while True:
        while not events.empty():
            kind, value = events.get()
            if kind == 'log':
                logs.append(value)
            else:
                busy = False
                result = value
                stage = 'finish' if kind == 'done' else 'error'
                selected = 0
        screen.erase()
        height, width = screen.getmaxyx()
        def draw(y, text, style=0):
            if 0 <= y < height - 1:
                try:
                    screen.addnstr(y, 2, text, max(0, width - 4), style)
                except curses.error:
                    pass
        for i, line in enumerate(LOGO):
            draw(i + 1, line, curses.color_pair(1) | curses.A_BOLD)
        draw(6, 'DESKTOP SETUP  /  ' + stage.upper(), curses.color_pair(1))
        details = []
        if stage == 'welcome':
            options = ['Install kOMA', 'Restore a previous installation', 'Exit']
            saved = installer.current_status()
            details = saved['summary'] + ['Install for the current user. No automatic logout or reboot.']
        elif stage == 'choose':
            complete = profile == 'full' and all((music, weather, power, audio, hotkeys, panels, tiling, backgrounds))
            options = ['Install Complete kOMA Theme' + (' [Selected]' if complete else ''),
                       'Profile: ' + ('Appearance only' if profile == 'appearance' else 'Full desktop components'),
                       'Optional Music Thing: ' + ('Yes' if music else 'No'),
                       'Optional Advanced Weather: ' + ('Yes' if weather else 'No'),
                       'Optional Power Control: ' + ('Yes' if power else 'No'),
                       'Optional Audio Control: ' + ('Yes' if audio else 'No'),
                       'Hotkeys: ' + ('Use kOMA hotkeys' if hotkeys else 'Keep my hotkeys'), 'Panels: ' + ('Apply kOMA panels' if panels else 'Keep my panels'),
                       'Window management: ' + ('Krohnkite + colored borders' if tiling else 'Keep existing setup'), 'Change login & lock screen background: ' + ('Yes' if backgrounds else 'No'), 'Review installation', 'Back']
            flags = saved['choices']
            for index, flag in [(1, flags['profile'] == 'full'), (2, flags['music']),
                                (3, flags['weather']), (4, flags['power']), (5, flags['audio']),
                                (6, flags['hotkeys']), (7, flags['panels']),
                                (8, flags['tiling']), (9, flags['backgrounds'])]:
                if flag:
                    options[index] += ' [Detected]'
            details = ['Existing components are detected live; review lists install/update actions.',
                       'Krohnkite provides automatic tiling; existing setup is preserved unless selected.']
        elif stage == 'review':
            options = ['Install now', 'Back'] if not plan['errors'] else ['Back']
            details = plan['changes'] + ['Settings and replaced packages will be backed up.'] + (['Cannot install yet:'] + plan['errors'] if plan['errors'] else []) + plan['remaining'] + ['Shortcut conflicts: ' + str(len(plan.get('conflicts', []))), 'Full shortcut review: ~/.local/state/koma/hotkey-review.txt'] + plan.get('conflicts', [])[:4]
        elif stage == 'restore':
            options = [p.parent.name for p in backups] + ['Back']
            details = ['Restore preserves files edited since installation.', 'Choose a backup to review it.']
        elif stage == 'restore-review':
            options = ['Restore now', 'Back']
            details = ['Backup: ' + str(journal.parent.name), 'Later edits will be preserved and reported.',
                       'Sign out/in after restore to reload desktop settings.']
        elif busy:
            options = []
            details = logs[-max(1, height - 12):]
        else:
            options = ['Return to welcome', 'Exit']
            if stage == 'error':
                details = ['Installation failed: ' + str(result), 'Backup retained; restore or retry from Welcome.'] + logs[-4:]
            else:
                details = ['Result: ' + result['status']] + result.get('plan', {}).get('remaining', []) + logs[-4:]
        selected = min(selected, max(0, len(options) - 1))
        separators = {1, len(options) - 2} if stage == 'choose' else set()
        separator_rows = len(separators)
        offset = 0
        for i, option in enumerate(options):
            if i in separators:
                draw(8 + i + offset, '-' * max(0, width - 4), curses.color_pair(1))
                offset += 1
            draw(8 + i + offset, ('> ' if selected == i else '  ') + option,
                 curses.color_pair(2) if selected == i else 0)
        # messages can hold several lines (a failed command's output); curses would
        # wrap them to column 0 underneath the following rows
        details = [part for line in details for part in str(line).splitlines() or ['']]
        for i, line in enumerate(details):
            draw(10 + len(options) + separator_rows + i, line)
        draw(height - 2, '↑/↓ Move   Enter/Space Select   Esc Back', curses.color_pair(1))
        screen.refresh()
        screen.timeout(100 if busy else 250)
        key = screen.getch()
        if busy or key == -1:
            continue
        if key == curses.KEY_UP:
            selected = max(0, selected - 1)
        elif key == curses.KEY_DOWN:
            selected = min(len(options) - 1, selected + 1)
        elif key == 27:
            stage, selected = 'welcome', 0
        elif key in (10, 13, 32):
            choice = options[selected]
            if choice == 'Exit':
                return
            if stage == 'welcome':
                if selected == 0:
                    stage = 'choose'
                else:
                    backups = installer.backups()
                    stage = 'restore'
            elif stage == 'choose':
                if selected == 0:
                    profile = 'full'
                    music = weather = power = audio = hotkeys = panels = tiling = backgrounds = True
                elif selected == 1:
                    profile = 'full' if profile == 'appearance' else 'appearance'
                    panels = profile == 'full'
                elif selected == 2:
                    music = not music
                elif selected == 3:
                    weather = not weather
                    if weather:
                        profile = 'full'
                elif selected == 4:
                    power = not power
                    if power:
                        profile = 'full'
                elif selected == 5:
                    audio = not audio
                    if audio:
                        profile = 'full'
                elif selected == 6:
                    hotkeys = not hotkeys
                elif selected == 7:
                    panels = not panels
                    if panels:
                        profile = 'full'
                elif selected == 8:
                    tiling = not tiling
                elif selected == 9:
                    backgrounds = not backgrounds
                elif choice == 'Review installation':
                    plan = installer.plan(profile, music, panels, hotkeys, tiling, weather, power, audio, backgrounds)
                    stage = 'review'
                elif choice == 'Back':
                    stage = 'welcome'
                else:
                    continue
            elif stage == 'review':
                if choice == 'Install now':
                    busy, stage, logs = True, 'install', []
                    threading.Thread(target=worker, args=(lambda: installer.install(plan),), daemon=True).start()
                else:
                    stage = 'choose'
            elif stage == 'restore':
                if choice == 'Back':
                    stage = 'welcome'
                else:
                    journal = backups[selected]
                    stage = 'restore-review'
            elif stage == 'restore-review':
                if choice == 'Restore now':
                    busy, stage, logs = True, 'restoring', []
                    threading.Thread(target=worker, args=(lambda: installer.restore(journal),), daemon=True).start()
                else:
                    stage = 'restore'
            else:
                stage = 'welcome'
            selected = 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', action='store_true', help='Print inspection results without changing settings')
    parser.add_argument('--profile', choices=['appearance', 'full'], default='appearance')
    parser.add_argument('--music', action='store_true')
    parser.add_argument('--weather', action='store_true')
    parser.add_argument('--power', action='store_true')
    parser.add_argument('--audio', action='store_true')
    parser.add_argument('--backgrounds', action='store_true')
    parser.add_argument('--panels', action='store_true')
    parser.add_argument('--restore-latest', action='store_true')
    args = parser.parse_args()
    if args.plan:
        print(json.dumps(Installer().plan(args.profile, args.music, args.panels, weather=args.weather, power=args.power, audio=args.audio, backgrounds=args.backgrounds), indent=2))
    elif args.restore_latest:
        installer = Installer(emit=print)
        backups = installer.backups()
        if not backups:
            parser.error('No installation backups found.')
        print(json.dumps(installer.restore(backups[0]), indent=2))
    else:
        curses.wrapper(ui)


if __name__ == '__main__':
    main()
