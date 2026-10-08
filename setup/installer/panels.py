"""Generate a portable Plasma panel replacement script."""
import json


def script(components, music=False, weather=False, power=False, audio=False):
    ids = {c['id'] for c in components}
    required = {'kde-desktop.workspaces', 'com.columbiafoundry.komalauncher',
                'com.columbiafoundry.komaplugins', 'com.columbiafoundry.komanetworkmanager',
                'com.github.idityage.spacerdivider'}
    if not required <= ids:
        raise ValueError('Panel installation requires the full desktop components.')
    separator = 'com.github.idityage.spacerdivider'
    widgets = ['kde-desktop.workspaces', separator, 'org.kde.plasma.panelspacer',
               'com.columbiafoundry.komalauncher', separator, 'org.kde.plasma.digitalclock']
    if weather:
        if 'org.kde.plasma.advanced-weather-widget' not in ids:
            raise ValueError('Weather must be installed before adding it to the panel.')
        widgets += [separator, 'org.kde.plasma.advanced-weather-widget']
    widgets += ['org.kde.plasma.panelspacer', separator, 'com.columbiafoundry.komaplugins']
    if music:
        widgets += ['com.columbiafoundry.komamusicthing']
    widgets += [separator]
    if audio:
        widgets += ['com.columbiafoundry.komaaudiocontrol']
    if power:
        if 'com.columbiafoundry.komapowercontrol' not in ids:
            raise ValueError('Power Control must be installed before adding it to the panel.')
        widgets += ['com.columbiafoundry.komapowercontrol']
    widgets += ['com.columbiafoundry.komanetworkmanager',
                'org.kde.plasma.systemtray', separator, 'com.columbiafoundry.komacolors']
    return '''
var hidden = ['org.kde.kdeconnect','org.kde.plasma.manage-inputmethod',
'org.kde.plasma.volume','org.kde.plasma.clipboard','org.kde.plasma.brightness',
'org.kde.plasma.mediacontroller','org.kde.plasma.devicenotifier',
'org.kde.plasma.notifications','org.kde.plasma.cameraindicator',
'org.kde.plasma.battery','org.kde.plasma.keyboardlayout','KDE Connect Indicator'];
var old = panels();
old.forEach(function(panel) {
    panel.widgets().forEach(function(widget) {
        if (widget.type === 'org.kde.plasma.systemtray') {
            widget.currentConfigGroup = ['General'];
            ['knownItems','extraItems','hiddenItems','shownItems'].forEach(function(key) {
                var value = widget.readConfig(key, '');
                String(value).split(',').forEach(function(id) {
                    if (id && hidden.indexOf(id) < 0) hidden.push(id);
                });
            });
        }
    });
});
old.forEach(function(panel) { panel.remove(); });
var specs = ''' + json.dumps(widgets) + ''';
for (var screen = 0; screen < screenCount; ++screen) {
    var panel = new Panel;
    panel.screen = screen;
    panel.location = 'top';
    panel.height = 32;
    panel.floating = false;
    panel.hiding = 'none';
    panel.alignment = 'center';
    panel.lengthMode = 'fill';
    panel.minimumLength = screenGeometry(screen).width;
    panel.maximumLength = screenGeometry(screen).width;
    specs.forEach(function(id) {
        var widget = panel.addWidget(id);
        if (id === 'com.github.idityage.spacerdivider') {
            widget.currentConfigGroup = ['General'];
            widget.writeConfig('expanding', false);
            widget.writeConfig('minSize', 12);
            widget.writeConfig('preferredSize', 20);
            widget.writeConfig('dividerThickness', 2);
            widget.writeConfig('dividerHeight', 50);
            widget.writeConfig('dividerOpacity', 60);
        }
        if (id === 'org.kde.plasma.digitalclock') {
            widget.currentConfigGroup = ['Appearance'];
            widget.writeConfig('dateDisplayFormat', 'BesideTime');
            widget.writeConfig('dateFormat', 'custom');
            widget.writeConfig('customDateFormat', 'ddd, MMM d, ');
        }
        if (id === 'kde-desktop.workspaces') {
            widget.currentConfigGroup = ['Appearance'];
            widget.writeConfig('elementSize', 24);
            widget.writeConfig('iconSize', 22);
            widget.writeConfig('indicatorShape', 'separators');
        }
        if (id === 'org.kde.plasma.systemtray') {
            widget.currentConfigGroup = ['General'];
            widget.writeConfig('showAllItems', false);
            widget.writeConfig('shownItems', '');
            widget.writeConfig('hiddenItems', hidden.join(','));
        }
    });
}
print('KOMA_PANELS_APPLIED');
'''
