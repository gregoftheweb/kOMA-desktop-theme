import QtQuick
import QtQuick.Window
import "../../lookandfeel/com.columbiafoundry.koma/contents/splash"

Window {
    id: preview
    width: 1100
    height: 700
    visible: true
    title: "kOMA splash preview — Escape to close"
    Splash { anchors.fill: parent; stage: 2 }
    Shortcut { sequence: "Escape"; onActivated: preview.close() }
}
