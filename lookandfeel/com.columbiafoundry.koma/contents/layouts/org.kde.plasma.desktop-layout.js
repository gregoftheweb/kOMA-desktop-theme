// kOMA default panel layout: the top panel the kOMA installer builds, one per screen.
// Used only when Plasma explicitly loads/resets the theme desktop layout.
// Without the kOMA installer (the Global Theme installed on its own) kOMA widgets are
// missing, so each falls back to stock Plasma equivalents or is left out. The workspaces
// fallback adds a task manager, since without kOMA's launcher there is no other way to
// see open windows.
var fallback = {
    "kde-desktop.workspaces": ["org.kde.plasma.pager", "org.kde.plasma.icontasks"],
    "com.columbiafoundry.komalauncher": ["org.kde.plasma.kickoff"],
    "com.columbiafoundry.komanetworkmanager": ["org.kde.plasma.networkmanagement"]
};
var widgets = [
    "kde-desktop.workspaces", "com.github.idityage.spacerdivider", "org.kde.plasma.panelspacer",
    "com.columbiafoundry.komalauncher", "com.github.idityage.spacerdivider", "org.kde.plasma.digitalclock",
    "org.kde.plasma.panelspacer", "com.github.idityage.spacerdivider", "com.columbiafoundry.komaplugins",
    "com.columbiafoundry.komaaudiocontrol", "com.columbiafoundry.komapowercontrol",
    "com.columbiafoundry.komanetworkmanager", "org.kde.plasma.systemtray",
    "com.github.idityage.spacerdivider", "com.columbiafoundry.komacolors"
];
function known(id) {
    return knownWidgetTypes.indexOf(id) >= 0;
}
// the tray hides what kOMA's own widgets cover, but only when all of them are installed
var komaWidgets = widgets.every(function (id) { return id.indexOf("org.kde.") === 0 || known(id); });
for (var screen = 0; screen < screenCount; ++screen) {
    var panel = new Panel;
    panel.screen = screen;
    panel.location = "top";
    panel.height = 32;
    panel.floating = false;
    panel.hiding = "none";
    panel.alignment = "center";
    panel.lengthMode = "fill";
    panel.minimumLength = screenGeometry(screen).width;
    panel.maximumLength = screenGeometry(screen).width;
    var ids = [];
    widgets.forEach(function (id) {
        ids = ids.concat(known(id) ? [id] : (fallback[id] || []).filter(known));
    });
    ids.forEach(function (id) {
        var widget = panel.addWidget(id);
        if (id === "com.github.idityage.spacerdivider") {
            widget.currentConfigGroup = ["General"];
            widget.writeConfig("expanding", false);
            widget.writeConfig("minSize", 12);
            widget.writeConfig("preferredSize", 20);
            widget.writeConfig("dividerThickness", 2);
            widget.writeConfig("dividerHeight", 50);
            widget.writeConfig("dividerOpacity", 60);
        }
        if (id === "org.kde.plasma.digitalclock") {
            widget.currentConfigGroup = ["Appearance"];
            widget.writeConfig("dateDisplayFormat", "BesideTime");
            widget.writeConfig("dateFormat", "custom");
            widget.writeConfig("customDateFormat", "ddd, MMM d, ");
        }
        if (id === "kde-desktop.workspaces") {
            widget.currentConfigGroup = ["Appearance"];
            widget.writeConfig("elementSize", 24);
            widget.writeConfig("iconSize", 22);
            widget.writeConfig("indicatorShape", "separators");
        }
        if (id === "org.kde.plasma.systemtray" && komaWidgets) {
            widget.currentConfigGroup = ["General"];
            widget.writeConfig("showAllItems", false);
            widget.writeConfig("shownItems", "");
            widget.writeConfig("hiddenItems", [
                "org.kde.kdeconnect", "org.kde.plasma.manage-inputmethod", "org.kde.plasma.volume",
                "org.kde.plasma.clipboard", "org.kde.plasma.brightness", "org.kde.plasma.mediacontroller",
                "org.kde.plasma.devicenotifier", "org.kde.plasma.notifications", "org.kde.plasma.cameraindicator",
                "org.kde.plasma.battery", "org.kde.plasma.keyboardlayout", "KDE Connect Indicator"
            ].join(","));
        }
    });
}
// Global Theme without the kOMA installer: use the Lightcycles wallpaper this package
// carries, and put a "Get the full kOMA desktop" link (the kOMA logo, opening the install
// instructions) on each desktop
if (!known("com.columbiafoundry.komalauncher")) {
    var theme = ["/.local/share", "/usr/share", "/usr/local/share"].map(function (base) {
        return (base.indexOf("/.") === 0 ? userDataPath() : "") + base + "/plasma/look-and-feel/com.columbiafoundry.koma/contents";
    }).filter(function (path) { return fileExists(path + "/get-koma.desktop"); })[0];
    if (theme) {
        var link = theme + "/get-koma.desktop";
        desktops().forEach(function (desktop) {
            desktop.wallpaperPlugin = "org.kde.image";
            desktop.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
            desktop.writeConfig("Image", "file://" + theme + "/wallpaper/kOMA-Lightcycles.png");
            var icon = desktop.addWidget("org.kde.plasma.icon", gridUnit * 2, gridUnit * 4, gridUnit * 6, gridUnit * 6);
            icon.currentConfigGroup = ["General"];
            icon.writeConfig("url", "file://" + link);
        });
    }
}
