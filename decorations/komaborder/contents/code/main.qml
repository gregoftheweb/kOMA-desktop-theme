/*
    kOMA Border — Omarchy-style window decoration: no title bar.
    The focus border itself is drawn by the KDE-Rounded-Corners effect
    (setup/apply-focus-border.sh) so client-side decorated apps get it too.
    Set borderWidth > 0 to draw a highlight border here instead (no effect).
    SPDX-License-Identifier: GPL-2.0-or-later
*/
import QtQuick
import org.kde.kwin.decoration

Decoration {
    id: root

    // Width of a border drawn by this decoration in px (0 = leave it to the effect).
    // The 6 px resize grab area outside the window exists either way.
    readonly property int borderWidth: decoration.readConfig("borderWidth", 0)
    readonly property bool active: decoration.client.active

    SystemPalette { id: palette; colorGroup: SystemPalette.Active }

    readonly property color activeColor: palette.highlight
    readonly property color inactiveColor: Qt.rgba(0.35, 0.35, 0.35, 0.67)

    alpha: true

    function applyBorders() {
        borders.setBorders(borderWidth);
        borders.setTitle(borderWidth);
        maximizedBorders.setAllBorders(0);
        extendedBorders.setAllBorders(6);
    }

    Rectangle {
        anchors.fill: parent
        visible: root.borderWidth > 0 && !decoration.client.maximized
        color: "transparent"
        border.width: root.borderWidth
        border.color: root.active ? root.activeColor : root.inactiveColor
    }

    Component.onCompleted: applyBorders()
}
