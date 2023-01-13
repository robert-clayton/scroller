import QtQuick 2.11

AnimatedImage {
    source: model.url
    width: window.colWidth
    height: window.colWidth / model.ratio
    mipmap: true
    asynchronous: true
    playing: true

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.MiddleButton
        onClicked: (mouse) => { internal.saveUrl(model.url) }
    }

    NumberAnimation on opacity {
        from: 0
        to: 1
        duration: 1500
    }

    onVisibleChanged: opacity.start()
}