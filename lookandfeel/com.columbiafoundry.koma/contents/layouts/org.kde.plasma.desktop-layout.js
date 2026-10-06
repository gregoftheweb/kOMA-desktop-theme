// kOMA default panel layout, captured from the live desktop on 2026-10-04.
// Used only when Plasma explicitly loads/resets the theme desktop layout.
// Coordinates are logical pixels. Panels fill each screen width.
var geometry = {
    "location": "top",
    "height": 32,
    "lengthMode": "fill",
    "alignment": "center",
    "hiding": "none",
    "floating": false,
    "offset": 0
};
var widgetDefaults = [
    {
        "plugin": "kde-desktop.workspaces",
        "config": [
            {
                "group": [
                    "Appearance"
                ],
                "values": {
                    "elementSize": "24",
                    "iconSize": "22",
                    "indicatorShape": "separators"
                }
            }
        ]
    },
    {
        "plugin": "org.kde.plasma.panelspacer",
        "config": []
    },
    {
        "plugin": "com.columbiafoundry.komalauncher",
        "config": []
    },
    {
        "plugin": "org.kde.plasma.digitalclock",
        "config": [
            {
                "group": [],
                "values": {
                    "popupHeight": "400",
                    "popupWidth": "560"
                }
            },
            {
                "group": [
                    "Appearance"
                ],
                "values": {
                    "customDateFormat": "ddd, MMM d, ",
                    "dateDisplayFormat": "BesideTime",
                    "dateFormat": "custom"
                }
            }
        ]
    },
    {
        "plugin": "com.columbiafoundry.komarandomimage",
        "config": [
            {
                "group": [],
                "values": {
                    "popupHeight": "153",
                    "popupWidth": "360"
                }
            },
            {
                "group": [
                    "General"
                ],
                "values": {
                    "imageDirectory": ""
                }
            }
        ]
    },
    {
        "plugin": "org.kde.plasma.panelspacer",
        "config": []
    },
    {
        "plugin": "com.columbiafoundry.komaplugins",
        "config": [
            {
                "group": [],
                "values": {
                    "popupHeight": "505",
                    "popupWidth": "540"
                }
            }
        ]
    },
    {
        "plugin": "com.columbiafoundry.komamusicthing",
        "config": [
            {
                "group": [],
                "values": {
                    "popupHeight": "69",
                    "popupWidth": "360"
                }
            }
        ]
    },
    {
        "plugin": "com.columbiafoundry.komanetworkmanager",
        "config": [
            {
                "group": [],
                "values": {
                    "popupHeight": "378",
                    "popupWidth": "432"
                }
            }
        ]
    },
    {
        "plugin": "com.columbiafoundry.komaaudiocontrol",
        "config": [
            {
                "group": [],
                "values": {
                    "popupHeight": "360",
                    "popupWidth": "414"
                }
            }
        ]
    },
    {
        "plugin": "com.columbiafoundry.komacolors",
        "config": [
            {
                "group": [],
                "values": {
                    "popupHeight": "400",
                    "popupWidth": "560"
                }
            }
        ]
    },
    {
        "plugin": "org.kde.plasma.systemtray",
        "config": [
            {
                "group": [],
                "values": {
                    "popupHeight": "432",
                    "popupWidth": "432"
                }
            },
            {
                "group": [
                    "General"
                ],
                "values": {
                    "extraItems": "org.kde.kdeconnect,org.kde.plasma.manage-inputmethod,org.kde.plasma.volume,org.kde.plasma.clipboard,org.kde.plasma.brightness,org.kde.plasma.devicenotifier,org.kde.plasma.notifications,org.kde.plasma.cameraindicator,org.kde.plasma.battery,org.kde.plasma.keyboardlayout",
                    "hiddenItems": "org.kde.kdeconnect,org.kde.plasma.manage-inputmethod,org.kde.plasma.volume,org.kde.plasma.clipboard,org.kde.plasma.brightness,org.kde.plasma.mediacontroller,org.kde.plasma.devicenotifier,org.kde.plasma.notifications,org.kde.plasma.cameraindicator,org.kde.plasma.battery,org.kde.plasma.keyboardlayout,KDE Connect Indicator",
                    "knownItems": "org.kde.kdeconnect,org.kde.plasma.manage-inputmethod,org.kde.plasma.volume,org.kde.plasma.clipboard,org.kde.plasma.brightness,org.kde.plasma.mediacontroller,org.kde.plasma.devicenotifier,org.kde.plasma.notifications,org.kde.plasma.cameraindicator,org.kde.plasma.battery,org.kde.plasma.keyboardlayout",
                    "showAllItems": "false",
                    "shownItems": ""
                }
            },
            {
                "group": [
                    "Shortcuts"
                ],
                "values": {
                    "global": ""
                }
            }
        ]
    },
    {
        "plugin": "org.kde.plasma.marginsseparator",
        "config": []
    }
];
for (var screen = 0; screen < screenCount; ++screen) {
    var panel = new Panel;
    panel.screen = screen;
    panel.location = geometry.location;
    panel.alignment = geometry.alignment;
    panel.height = geometry.height;
    panel.offset = geometry.offset;
    panel.floating = geometry.floating;
    panel.hiding = geometry.hiding;
    panel.lengthMode = geometry.lengthMode;
    var width = screenGeometry(screen).width;
    panel.minimumLength = width;
    panel.maximumLength = width;
    widgetDefaults.forEach(function (spec) {
        var widget = panel.addWidget(spec.plugin);
        spec.config.forEach(function (config) {
            widget.currentConfigGroup = config.group;
            Object.keys(config.values).forEach(function (key) {
                widget.writeConfig(key, config.values[key]);
            });
        });
    });
}
