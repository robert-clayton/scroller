import QtQuick 2.11

Image {
    id: image
    source: model.url
    width: window.colWidth
    height: window.colWidth / model.ratio
    mipmap: true
    asynchronous: true
    opacity: 0

    NumberAnimation on opacity {
        id: animation
        from: 0
        to: 1
        duration: 1500
    }

    PropertyAnimation {
        id: fadeOutAnimation
        target: image
        property: "opacity"
        from: 1
        to: 0
        duration: 750
        running: false
        onStopped: {
            image.visible = false
            image.opacity = 0
        }
    }

    PropertyAnimation {
        id: boingAnimation
        target: image
        property: "scale"
        from: 1
        to: 1.1
        duration: 100
        running: false

        property bool reversed: false

        onStopped: {
            if (!reversed) {
                boingAnimation.reversed = true
                boingAnimation.from = 1.1
                boingAnimation.to = 1
                boingAnimation.running = true
            } else {
                boingAnimation.reversed = false
                boingAnimation.from = 1
                boingAnimation.to = 1.1
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton

        onClicked: (mouse) => {
            if (mouse.button === Qt.RightButton) {
                internal.deleteUrl(model.url)
                fadeOutAnimation.running = true
            } else if (mouse.button === Qt.MiddleButton) {
                internal.saveUrl(model.url)
            }
        }

        onDoubleClicked: (mouse) => {
            if (mouse.button === Qt.LeftButton) {
                boingAnimation.running = true
                internal.openUrl(model.url)
            }
        }
    }

    onVisibleChanged: {
        if (visible) {
            animation.start()
        } else {
            animation.stop()
        }
    }
}
