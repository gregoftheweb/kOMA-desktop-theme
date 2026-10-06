import QtQuick
import QtTest
import "../../lookandfeel/com.columbiafoundry.koma/contents/splash"

TestCase {
    name: "KomaSplash"
    when: windowShown
    width: 960
    height: 540
    visible: true
    Splash { id: splash; anchors.fill: parent; stage: 2 }
    function test_pathAndStartupLifecycle() {
        verify(splash.animating);
        wait(100);
        verify(splash.progress > 0);
        for (var leg = 0; leg < 40; leg++) {
            splash.nextFlight();
            for (var step = 0; step <= 10; step++) {
                var point = splash.pointOnPath(step / 10);
                verify(point.x >= 0.1 && point.x <= 0.9);
                verify(point.y >= 0.12 && point.y <= 0.84);
            }
        }
        splash.stage = 6;
        verify(!splash.animating);
        var stopped = splash.progress;
        wait(100);
        compare(splash.progress, stopped);
    }
}
