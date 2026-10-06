pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.plasma.components as PC3
import org.kde.plasma.plasmoid
import org.kde.plasma.plasma5support as P5Support

PlasmoidItem {
    id: root
    property var palettes: []
    property string currentScheme: ""
    property string errorMessage: ""
    property bool busy: false
    readonly property string helper: decodeURIComponent(Qt.resolvedUrl("../code/koma-colors").toString().replace("file://", ""))
    readonly property color accent: Kirigami.Theme.highlightColor

    Plasmoid.icon: "preferences-desktop-color"
    toolTipMainText: "kOMA Colors"
    toolTipSubText: "Switch desktop palette: Tron, McLaren, Ferrari, or Lambo"
    preferredRepresentation: compactRepresentation

    function quote(value) {
        return "'" + String(value).replace(/'/g, "'\\''") + "'";
    }

    function request(palette) {
        if (busy) return;
        busy = true;
        errorMessage = "";
        runner.connectSource("python3 " + quote(helper) + " " + quote(palette));
    }

    Component.onCompleted: request("status")
    onExpandedChanged: { if (root.expanded) root.request("status"); }
    onAccentChanged: refreshTimer.restart()
    Timer {
        id: refreshTimer
        interval: 250
        onTriggered: root.request("status")
    }

    P5Support.DataSource {
        id: runner
        engine: "executable"
        connectedSources: []
        onNewData: function(source, data) {
            disconnectSource(source);
            root.busy = false;
            if (data["exit code"] !== 0) {
                root.errorMessage = String(data.stderr || data.stdout || "Could not switch palette.").trim();
                return;
            }
            try {
                var result = JSON.parse(data.stdout);
                root.currentScheme = result.scheme;
                if (result.palettes) root.palettes = result.palettes;
            } catch (error) {
                root.errorMessage = "Could not read palette status.";
            }
        }
    }

    compactRepresentation: PC3.ToolButton {
        implicitWidth: 28
        implicitHeight: 28
        Layout.minimumWidth: 24
        Layout.minimumHeight: 24
        Accessible.name: "kOMA Colors"
        onClicked: root.expanded = !root.expanded
        contentItem: Item {
            Grid {
                anchors.centerIn: parent
                columns: 2
                spacing: 3
                Repeater {
                    model: ["#23C8FF", "#FF8700", "#FF3245", "#68DC45"]
                    Rectangle {
                        required property string modelData
                        width: 7
                        height: 7
                        radius: 3.5
                        color: modelData
                    }
                }
            }
        }
    }

    fullRepresentation: ColumnLayout {
        Layout.minimumWidth: 270
        Layout.preferredWidth: 290
        Layout.minimumHeight: implicitHeight
        Layout.preferredHeight: implicitHeight
        spacing: Kirigami.Units.smallSpacing

        PC3.Label {
            text: "kOMA Colors"
            font.bold: true
            Layout.margins: Kirigami.Units.smallSpacing
        }
        Repeater {
            model: root.palettes
            PC3.Button {
                id: choice
                required property var modelData
                Layout.fillWidth: true
                implicitHeight: 42
                enabled: !root.busy
                Accessible.name: modelData.name + (root.currentScheme === modelData.scheme ? ", selected" : "")
                onClicked: root.request(modelData.id)
                contentItem: RowLayout {
                    spacing: 12
                    Rectangle {
                        Layout.preferredWidth: 20
                        Layout.preferredHeight: 20
                        radius: 10
                        color: choice.modelData.color
                    }
                    PC3.Label {
                        text: choice.modelData.name
                        Layout.fillWidth: true
                    }
                    PC3.Label {
                        text: root.currentScheme === choice.modelData.scheme ? "✓" : ""
                        color: Kirigami.Theme.highlightColor
                    }
                }
            }
        }
        PC3.Label {
            visible: root.errorMessage.length > 0
            text: root.errorMessage
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            color: Kirigami.Theme.negativeTextColor
        }
        PC3.Label {
            visible: root.busy
            text: "Updating…"
            Layout.margins: Kirigami.Units.smallSpacing
        }
    }
}
