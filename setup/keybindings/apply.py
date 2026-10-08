#!/usr/bin/env python3
"""Apply keybindings.tsv to KDE Plasma 6 global shortcuts, live.

  apply.py                 dry run: print the plan and every key it takes over
  apply.py --test-noop     write one shortcut back unchanged (safety check)
  apply.py --apply [N]     apply all rows (or only the first N)
  apply.py --undo          restore every action this script changed

Safety rules (KWin hosts the shortcut service on Plasma 6; a bad call can
crash the compositor):
  - Conflicts are found by reading ~/.config/kglobalshortcutsrc, never by
    asking KWin to search (globalShortcutsByKey crashed KWin once).
  - Only shortcutKeys / setForeignShortcutKeys / doRegister are called, with
    the exact D-Bus types shortcutKeys returns.
  - KWin's PID is checked around every write; the run stops if it changes.
  - Each action's previous keys are saved to undo.json before it is changed.
"""
import json
import os
import re
import subprocess
import sys
import shutil
import shlex
import time

import dbus

HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(HERE, "keybindings.tsv")
STATE = os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state"))
UNDO = os.environ.get("KOMA_SHORTCUT_UNDO", os.path.join(STATE, "koma", "hotkeys-undo.json"))
RC = os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "kglobalshortcutsrc")
APPS_DIR = os.path.join(os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")), "applications")
KOMALAUNCHER = os.path.expanduser("~/.local/bin/komalauncher")

MODS = {"meta": 0x10000000, "ctrl": 0x04000000, "alt": 0x08000000, "shift": 0x02000000}
NAMED = {
    "space": 0x20, "esc": 0x01000000, "escape": 0x01000000, "tab": 0x01000001,
    "backspace": 0x01000003, "return": 0x01000004, "enter": 0x01000005,
    "print": 0x01000009, "home": 0x01000010, "end": 0x01000011,
    "left": 0x01000012, "up": 0x01000013, "right": 0x01000014, "down": 0x01000015,
    "pgup": 0x01000016, "pgdown": 0x01000017, "del": 0x01000007, "delete": 0x01000007,
    "screensaver": 0x010000BA,
}
for i in range(1, 13):
    NAMED["f%d" % i] = 0x01000030 + i - 1
# US-layout shifted symbols: Wayland may report Shift+1 as "!" etc.
SHIFTED = {"1": "!", "2": "@", "3": "#", "4": "$", "5": "%", "6": "^",
           "7": "&", "8": "*", "9": "(", "0": ")", "/": "?"}
MOD_ORDER = ["meta", "ctrl", "alt", "shift"]


def parse_key(text):
    """'Meta+Ctrl+A' -> Qt int, or None if it has a key name we don't know."""
    text = text.strip()
    if text.endswith("++"):          # "Meta++"
        parts, key = text[:-2].split("+"), "+"
    else:
        parts = text.split("+")
        key = parts.pop()
    value = 0
    for m in parts:
        if m.lower() not in MODS:
            return None
        value |= MODS[m.lower()]
    k = key.lower()
    if k in NAMED:
        return value | NAMED[k]
    if len(key) == 1:
        return value | ord(key.upper())
    return None


def canon(text):
    """Canonical spelling for comparing keys read from kglobalshortcutsrc."""
    text = text.strip()
    if not text or text.lower() == "none":
        return None
    if text.endswith("++"):
        parts, key = text[:-2].split("+"), "+"
    else:
        parts = text.split("+")
        key = parts.pop()
    mods = sorted({p.lower() for p in parts}, key=lambda m: MOD_ORDER.index(m) if m in MOD_ORDER else 9)
    k = {"escape": "esc", "delete": "del"}.get(key.lower(), key.lower())
    return "+".join(mods + [k])


def variants(text):
    """A key plus its shifted-symbol twin: Meta+Shift+1 -> [Meta+Shift+1, Meta+!]."""
    out = [text]
    parts = text.split("+")
    if len(parts) >= 2 and "Shift" in parts[:-1] and parts[-1] in SHIFTED:
        twin = [p for p in parts[:-1] if p != "Shift"] + [SHIFTED[parts[-1]]]
        out.append("+".join(twin))
    return out


def read_rc():
    """{(component, action): [canonical keys]} from kglobalshortcutsrc."""
    holders = {}
    comp = None
    if not os.path.exists(RC):
        return holders
    with open(RC) as f:
        for line in f:
            line = line.rstrip("\n")
            m = re.match(r"^\[(.*)\]$", line)
            if m:
                comp = m.group(1)
                if comp.startswith("services]["):
                    comp = comp[len("services]["):]
                continue
            if not comp or "=" not in line or line.startswith("_k_friendly_name"):
                continue
            action, value = line.split("=", 1)
            active = value.split(",")[0]
            keys = [canon(k) for k in active.split("\\t")]
            holders[(comp, action)] = [k for k in keys if k]
    return holders


def load_rows():
    rows = []
    with open(TSV) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            keys, kind, target, label = line.split("\t")
            key_list = []
            for k in keys.split(" | "):
                key_list.extend(variants(k.strip()))
            rows.append({"keys": key_list, "kind": kind, "target": target, "label": label})
    return rows


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def action_id(row):
    kind, target, label = row["kind"], row["target"], row["label"]
    if kind in ("kwin", "plasmashell", "ksmserver"):
        friendly = {"kwin": "KWin", "plasmashell": "plasmashell", "ksmserver": "Session Management"}[kind]
        return [kind, target, friendly, label]
    if kind == "app":
        return [target, "_launch", label, label]
    name = slug(label)
    if not name.startswith("koma-"):
        name = "koma-" + name
    return [name + ".desktop", "_launch", label, label]


def desktop_exec(row):
    if row["label"] == "Browser":
        return os.path.expanduser("~/.local/bin/koma-browser")
    if row["kind"] == "koma":
        return KOMALAUNCHER + " open " + row["target"]
    return row["target"]


def write_desktop(row, comp):
    path = os.path.join(APPS_DIR, comp)
    body = ("[Desktop Entry]\nType=Application\nName=%s\nExec=%s\nNoDisplay=true\n"
            "X-KDE-GlobalAccel-CommandShortcut=true\nComment=Generated by kOMA-desktop-theme/setup/keybindings/apply.py\n"
            % (row["label"], desktop_exec(row)))
    old = open(path).read() if os.path.exists(path) else None
    if old != body:
        with open(path, "w") as f:
            f.write(body)
        return True
    return False


def kwin_pid():
    out = subprocess.run(["pgrep", "-x", "kwin_wayland"], capture_output=True, text=True).stdout.split()
    return out[0] if out else None


class Accel:
    def __init__(self):
        self.iface = dbus.Interface(dbus.SessionBus().get_object("org.kde.kglobalaccel", "/kglobalaccel"),
                                    "org.kde.KGlobalAccel")
        self.pid = kwin_pid()

    def check(self, what):
        now = kwin_pid()
        if now != self.pid:
            sys.exit("STOP: kwin_wayland PID changed (%s -> %s) after %s" % (self.pid, now, what))

    @staticmethod
    def aid(a):
        return dbus.Array([dbus.String(x) for x in a], signature="s")

    @staticmethod
    def encode(ints):
        return dbus.Array([dbus.Struct((dbus.Array([dbus.Int32(k), 0, 0, 0], signature="i"),), signature=None)
                           for k in ints], signature="(ai)")

    def get(self, a):
        return [int(s[0][0]) for s in self.iface.shortcutKeys(self.aid(a)) if int(s[0][0])]

    def set(self, a, ints, what):
        self.iface.setForeignShortcutKeys(self.aid(a), self.encode(ints))
        self.check(what)

    def register(self, a, what):
        self.iface.doRegister(self.aid(a))
        # SetPresent (2) marks a generated service action active; merely changing
        # its foreign shortcut keys can leave a registered action inactive.
        self.iface.setShortcutKeys(self.aid(a), self.encode(self.get(a)), dbus.UInt32(6))
        self.check(what)


def plan(rows):
    holders = read_rc()
    steps = []
    claimed = {}
    for row in rows:
        aid = action_id(row)
        ints = []
        for k in row["keys"]:
            v = parse_key(k)
            if v is None:
                sys.exit("unknown key name in %r: %s" % (row["label"], k))
            ints.append(v)
            c = canon(k)
            if c in claimed:
                sys.exit("key %s used twice in keybindings.tsv (%s, %s)" % (k, claimed[c], row["label"]))
            claimed[c] = row["label"]
        steps.append({"row": row, "aid": aid, "ints": ints})
    # Every other action holding one of our keys loses it.
    ours = {(s["aid"][0], s["aid"][1]) for s in steps}
    takeovers = []
    for (comp, action), keys in holders.items():
        if (comp, action) in ours:
            continue
        lost = [k for k in keys if k in claimed]
        if lost:
            takeovers.append({"aid": [comp, action, "", ""], "lost": lost, "to": [claimed[k] for k in lost]})
    return steps, takeovers


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--dry-run"
    rows = load_rows()
    holders = read_rc()
    available = []
    for row in rows:
        kind, target = row['kind'], row['target']
        if kind == 'app' and row['label'] == 'Browser':
            result = subprocess.run(['xdg-settings', 'get', 'default-web-browser'], capture_output=True, text=True)
            browser = result.stdout.strip()
            if browser and '/' not in browser and browser.endswith('.desktop'):
                row['target'] = target = browser
        enabled = True
        if kind in ('kwin', 'plasmashell', 'ksmserver'):
            enabled = (kind, target) in holders
        elif kind == 'app':
            enabled = any(os.path.isfile(os.path.join(base, 'applications', target)) for base in
                          [os.path.dirname(APPS_DIR)] + os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':'))
        elif kind == 'cmd':
            enabled = bool(shutil.which(shlex.split(target)[0]))
        if enabled:
            available.append(row)
        else:
            print('Skipped unavailable target: ' + row['label'])
    steps, takeovers = plan(available)


    if mode == "--dry-run":
        for s in steps:
            print("%-38s %-12s %s" % (" | ".join(s["row"]["keys"]), s["row"]["kind"], s["row"]["label"]))
        print("\nKeys taken from other actions:")
        for t in takeovers:
            print("  %-55s loses %s  (-> %s)" % ("/".join(t["aid"][:2]), ", ".join(t["lost"]), ", ".join(t["to"])))
        return

    accel = Accel()
    print("kwin_wayland PID", accel.pid)

    if mode == "--test-noop":
        a = ["kwin", "Window Close", "KWin", "Close Window"]
        raw = accel.iface.shortcutKeys(accel.aid(a))
        accel.iface.setForeignShortcutKeys(accel.aid(a), raw)
        accel.check("no-op write")
        print("no-op write OK; Window Close keys:", [hex(k) for k in accel.get(a)])
        return

    os.makedirs(os.path.dirname(UNDO), exist_ok=True)
    os.makedirs(APPS_DIR, exist_ok=True)
    undo = json.load(open(UNDO)) if os.path.exists(UNDO) else {}

    def remember(a):
        key = json.dumps(a[:2])
        if key not in undo:
            undo[key] = {"aid": a, "keys": accel.get(a)}
            json.dump(undo, open(UNDO, "w"), indent=1)

    def applied(a):
        key = json.dumps(a[:2])
        undo[key]['applied'] = accel.get(a)
        json.dump(undo, open(UNDO, 'w'), indent=1)

    if mode == "--undo":
        for entry in undo.values():
            if accel.get(entry['aid']) != entry.get('applied'):
                print('Preserved later shortcut edit: ' + '/'.join(entry['aid'][:2]))
                continue
            accel.set(entry["aid"], entry["keys"], "undo " + "/".join(entry["aid"][:2]))
            print("restored", "/".join(entry["aid"][:2]), [hex(k) for k in entry["keys"]])
        os.rename(UNDO, UNDO + ".applied")
        return

    if mode == "--apply":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else len(steps)
        todo = steps[:limit]
        todo_keys = {k for s in todo for k in s["ints"]}
        # Free the keys first, so no two actions ever hold the same key.
        for t in takeovers:
            a = t["aid"]
            current = accel.get(a)
            keep = [k for k in current if k not in todo_keys]
            if keep != current:
                remember(a)
                accel.set(a, keep, "freeing keys on " + "/".join(a[:2]))
                applied(a)
                print("freed  %-50s now %s" % ("/".join(a[:2]), [hex(k) for k in keep]))
        new_files = False
        for s in todo:
            a, row = s["aid"], s["row"]
            if row["kind"] in ("cmd", "koma"):
                new_files |= write_desktop(row, a[0])
        if new_files:
            subprocess.run(["kbuildsycoca6"], capture_output=True)
        for s in todo:
            a, row = s["aid"], s["row"]
            remember(a)
            generated = row["kind"] in ("app", "cmd", "koma")
            attempts = 5 if generated else 1
            for attempt in range(attempts):
                if generated:
                    accel.register(a, "registering " + a[0])
                    # Activate and assign together. A newly discovered desktop service
                    # can still be registering after the service-cache rebuild.
                    accel.iface.setShortcutKeys(accel.aid(a), accel.encode(s["ints"]), dbus.UInt32(6))
                    accel.check("setting " + row["label"])
                else:
                    accel.set(a, s["ints"], "setting " + row["label"])
                got = accel.get(a)
                ok = sorted(got) == sorted(s["ints"])
                if ok:
                    break
                if attempt + 1 < attempts:
                    time.sleep(0.25)
            applied(a)
            print("%s  %-38s %s" % ("ok " if ok else "MISMATCH", " | ".join(row["keys"]), row["label"]))
            if not ok:
                raise RuntimeError("Shortcut verification failed: " + row["label"])
        print("kwin_wayland PID unchanged:", accel.pid)
        return

    sys.exit(__doc__)


if __name__ == "__main__":
    main()
