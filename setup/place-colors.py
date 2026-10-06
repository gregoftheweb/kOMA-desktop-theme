#!/usr/bin/env python3
"""Place kOMA Colors before kOMA Plugins on every existing panel, once."""
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess

config = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
rc = config / "plasma-org.kde.plasma.desktop-appletsrc"
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
shutil.copy2(rc, rc.with_name(rc.name + ".bak-colors-" + stamp))
script = """
var result = [];
panels().forEach(function(p) {
    if (p.widgets().some(function(w) { return w.type === 'com.columbiafoundry.komacolors'; })) return;
    p.currentConfigGroup = ['General'];
    var order = String(p.readConfig('AppletOrder') || '').split(';').filter(String);
    if (!order.length) order = p.widgets().map(function(w) { return String(w.id); });
    var anchor = p.widgets().filter(function(w) { return w.type === 'com.columbiafoundry.komaplugins'; })[0];
    var widget = p.addWidget('com.columbiafoundry.komacolors');
    var index = anchor ? order.indexOf(String(anchor.id)) : -1;
    if (index < 0) order.push(String(widget.id)); else order.splice(index, 0, String(widget.id));
    result.push({panel: p.id, order: order.join(';')});
});
print(JSON.stringify(result));
"""
result = subprocess.run(["qdbus6", "org.kde.plasmashell", "/PlasmaShell",
                         "org.kde.PlasmaShell.evaluateScript", script],
                        capture_output=True, text=True, check=True, timeout=30)
plan = json.loads(result.stdout)
if plan:
    subprocess.run(["systemctl", "--user", "stop", "plasma-plasmashell.service"], check=True, timeout=30)
    try:
        for panel in plan:
            subprocess.run(["kwriteconfig6", "--file", str(rc), "--group", "Containments",
                            "--group", str(int(panel["panel"])), "--group", "General",
                            "--key", "AppletOrder", panel["order"]], check=True, timeout=10)
    finally:
        subprocess.run(["systemctl", "--user", "start", "plasma-plasmashell.service"], check=True, timeout=30)
print(f"kOMA Colors added to {len(plan)} panel(s)")
