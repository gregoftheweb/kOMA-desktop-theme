// SPDX-FileCopyrightText: 2026 Columbia Foundry
// SPDX-License-Identifier: GPL-3.0-or-later
pragma ComponentBehavior: Bound
import QtCore
import QtQuick

Rectangle {
    id: root
    property int stage: 0
    readonly property bool animating: visible && stage < 6 && width > 0 && height > 0
    property real progress: 0
    property point startPoint: Qt.point(0.18, 0.65)
    property point controlOne: Qt.point(0.35, 0.25)
    property point controlTwo: Qt.point(0.55, 0.85)
    property point endPoint: Qt.point(0.8, 0.35)
    color: "#0A0D12"

    function pointOnPath(t) {
        var u = 1 - t;
        return Qt.point(u*u*u*startPoint.x + 3*u*u*t*controlOne.x + 3*u*t*t*controlTwo.x + t*t*t*endPoint.x,
                        u*u*u*startPoint.y + 3*u*u*t*controlOne.y + 3*u*t*t*controlTwo.y + t*t*t*endPoint.y);
    }
    function randomPoint() {
        return Qt.point(0.1 + Math.random() * 0.8, 0.12 + Math.random() * 0.72);
    }
    function nextFlight() {
        if (!animating) return;
        startPoint = pointOnPath(progress);
        var destination = randomPoint();
        // Make a visible journey rather than tiny movements around one spot.
        if (Math.abs(destination.x - startPoint.x) < 0.3)
            destination.x = startPoint.x < 0.5 ? 0.75 + Math.random() * 0.15 : 0.1 + Math.random() * 0.15;
        controlOne = randomPoint();
        controlTwo = randomPoint();
        endPoint = destination;
        progress = 0;
        flight.duration = 2400 + Math.random() * 2200;
        flight.restart();
    }
    onAnimatingChanged: {
        if (animating) nextFlight();
        else flight.stop();
    }
    Component.onCompleted: {
        startPoint = randomPoint();
        progress = 0;
        nextFlight();
    }

    Image {
        anchors.fill: parent
        source: "images/tron-flower.jpg"
        fillMode: Image.PreserveAspectCrop
        autoTransform: true
    }
    Item {
        id: scene
        anchors.fill: parent
        opacity: 0
        Component.onCompleted: reveal.start()
        NumberAnimation { id: reveal; target: scene; property: "opacity"; from: 0; to: 1; duration: 450 }
        Butterfly {
            id: butterfly
            readonly property point position: root.pointOnPath(root.progress)
            width: Math.max(44, Math.min(72, root.height * 0.06))
            height: width * 0.75
            x: position.x * root.width - width / 2
            y: position.y * root.height - height / 2 + Math.sin(root.progress * Math.PI * 8) * 5
            rotation: Math.sin(root.progress * Math.PI * 2) * 20 + (root.endPoint.x > root.startPoint.x ? 15 : -15)
            flying: root.animating
        }
        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: root.height * 0.045
            spacing: Math.max(8, root.height * 0.012)
            Image {
                anchors.horizontalCenter: parent.horizontalCenter
                width: Math.max(58, Math.min(96, root.height * 0.09))
                height: width
                source: "images/koma.svg"
                sourceSize.width: width * 2
                sourceSize.height: height * 2
                smooth: true
            }
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "kOMA"
                color: "#E9EEF5"
                opacity: 0.85
                font.pixelSize: Math.max(18, root.height * 0.022)
                font.letterSpacing: 4
            }
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                // only until the kOMA installer has run (it installs this icon)
                visible: installed.status === Image.Error
                text: "Get the full kOMA desktop: github.com/gregoftheweb/kOMA-desktop-theme"
                color: "#E9EEF5"
                opacity: 0.6
                font.pixelSize: Math.max(12, root.height * 0.013)
            }
        }
        Image {
            id: installed
            visible: false
            source: StandardPaths.writableLocation(StandardPaths.GenericDataLocation) + "/icons/hicolor/scalable/apps/koma.svg"
        }
    }
    NumberAnimation {
        id: flight
        target: root
        property: "progress"
        from: 0
        to: 1
        easing.type: Easing.Linear
        onFinished: root.nextFlight()
    }
}
