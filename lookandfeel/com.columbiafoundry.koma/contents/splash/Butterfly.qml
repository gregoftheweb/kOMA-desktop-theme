pragma ComponentBehavior: Bound
import QtQuick

Item {
    id: butterfly
    property bool flying: true
    property real wingSpread: 1
    width: 72
    height: 54
    Image {
        id: leftWing
        width: butterfly.width / 2
        height: butterfly.height
        source: "images/butterfly-wing.svg"
        smooth: true
        transform: Scale {
            origin.x: leftWing.width
            origin.y: leftWing.height / 2
            xScale: butterfly.wingSpread
        }
    }
    Image {
        id: rightWing
        x: butterfly.width / 2
        width: butterfly.width / 2
        height: butterfly.height
        source: "images/butterfly-wing.svg"
        mirror: true
        smooth: true
        transform: Scale {
            origin.x: 0
            origin.y: rightWing.height / 2
            xScale: butterfly.wingSpread
        }
    }
    Image {
        anchors.centerIn: parent
        width: butterfly.width / 6
        height: butterfly.height
        source: "images/butterfly-body.svg"
    }
    SequentialAnimation on wingSpread {
        running: butterfly.flying && butterfly.visible
        loops: Animation.Infinite
        NumberAnimation { from: 1; to: 0.14; duration: 105; easing.type: Easing.InOutSine }
        NumberAnimation { from: 0.14; to: 1; duration: 145; easing.type: Easing.InOutSine }
    }
}
