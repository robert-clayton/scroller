import QtQuick 2.11

Image {
    source: model.url
    width: window.colWidth
    height: window.colWidth / model.ratio
    mipmap: true
    asynchronous: true

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.MiddleButton
        onClicked: (mouse) => { internal.saveUrl(model.url) }
    }
}