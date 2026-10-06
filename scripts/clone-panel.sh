#!/usr/bin/env bash
# Make every Plasma panel match the template panel (default: id 28).
# Rebuilds each non-template panel's widgets in the template's order with the
# template's widget settings, then copies height/length/alignment/floating.
# Usage: sync-panels.sh [template-panel-id]
set -euo pipefail
TEMPLATE="${1:-28}"
CFG=~/.config/plasma-org.kde.plasma.desktop-appletsrc
ts=$(date +%Y%m%d-%H%M%S)
cp -a "$CFG" "$CFG.bak-$ts"
cp -a ~/.config/plasmashellrc ~/.config/plasmashellrc.bak-$ts
echo "backup: $CFG.bak-$ts"

qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var TEMPLATE = $TEMPLATE;
// Containment-level keys a system tray exposes at its root; never copy these.
var SKIP_ROOT = ['activityId','formfactor','immutability','lastScreen','location','plugin','wallpaperplugin'];

function snapshot(w, path, out) {
  w.currentConfigGroup = path;
  w.configKeys.slice().forEach(function (k) {
    if (path.length === 0 && SKIP_ROOT.indexOf(k) !== -1) return;
    out.push({ path: path.slice(), key: k, value: w.readConfig(k) });
  });
  // configGroups is a live list that re-reads when currentConfigGroup changes, so copy it first.
  // Skip a system tray's own child applets ([Applets][N]); the new tray creates its own.
  w.configGroups.slice().forEach(function (g) {
    if (path.length === 0 && g === 'Applets') return;
    snapshot(w, path.concat([g]), out);
  });
  return out;
}

var tpl = panelById(TEMPLATE);
if (!tpl) throw 'template panel ' + TEMPLATE + ' not found';
tpl.currentConfigGroup = ['General'];
var order = String(tpl.readConfig('AppletOrder')).split(';').filter(String).map(Number);
var byId = {};
tpl.widgets().forEach(function (w) { byId[w.id] = w; });
var spec = order.filter(function (id) { return byId[id]; }).map(function (id) {
  return { type: byId[id].type, config: snapshot(byId[id], [], []) };
});
print('template ' + TEMPLATE + ': ' + spec.map(function (s) { return s.type.replace('org.kde.plasma.', ''); }).join(', ') + '\n');

panels().forEach(function (p) {
  if (p.id === TEMPLATE) return;
  p.widgets().forEach(function (w) { w.remove(); });
  var newIds = spec.map(function (s) {
    var w = p.addWidget(s.type);
    s.config.forEach(function (c) { w.currentConfigGroup = c.path; w.writeConfig(c.key, c.value); });
    w.reloadConfig();
    return w.id;
  });
  p.currentConfigGroup = ['General'];
  p.writeConfig('AppletOrder', newIds.join(';'));
  p.location = tpl.location;
  p.height = tpl.height;
  p.lengthMode = tpl.lengthMode;
  p.alignment = tpl.alignment;
  p.hiding = tpl.hiding;
  p.floating = tpl.floating;
  p.offset = tpl.offset;
  p.maximumLength = tpl.maximumLength;
  p.minimumLength = tpl.minimumLength;
  p.maximumLength = tpl.maximumLength;
  print('panel ' + p.id + ' (screen ' + p.screen + ') rebuilt: ' + newIds.join(';') + ' height=' + p.height + ' length=' + p.minimumLength + '-' + p.maximumLength + '\n');
});
"
