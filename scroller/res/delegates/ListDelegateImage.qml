import QtQuick 2.11

Image {
    source: model.url
    width: window.colWidth
    height: window.colWidth / model.ratio
    mipmap: true
    asynchronous: true
    opacity: 0

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