import QtQuick 2.15
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.11
import Qt.labs.platform 1.1
import Qt.labs.settings 1.0
import QtQml 2.15

ApplicationWindow {
    id: window
    visible: true
    width: 1600
    height: 900
    color: "transparent"
    title: qsTr("scrolller")
    flags: visibility == "FullScreen" ? (Qt.Window | Qt.FramelessWindowHint) : Qt.Window
    visibility: Backend ? Backend.visibility : "Windowed"

    property int colCount: Backend ? Backend.colCount : 1
    property int colWidth: width / colCount
    property int tickSpeed: Backend ? Backend.tickSpeed : 1
    

    Item {
        id: internal
        anchors.fill: parent

        function addColumn(amt) {
            if (window.colCount + amt < 1) return
            if (amt < 0) ImageModel.removeProxy(window.colCount - 1)
            Backend.setColCount(window.colCount + amt)
        }

        function addTickSpeed(speed) {
            Backend.setTickSpeed(window.tickSpeed + speed)
        }

        FolderDialog { id: folderDialog }
        function changeFolder() {
            folderDialog.onAccepted.connect(() => {
                ImageModel.startup(folderDialog.folder)
            })
            folderDialog.folder = ImageModel.getFolder()
            folderDialog.open()
        }

        Shortcut { sequence: StandardKey.Open; onActivated: internal.changeFolder() }
        Shortcut { sequence: "Esc"; onActivated: close() }
        Shortcut { sequence: StandardKey.ZoomOut; onActivated: internal.addColumn(1) }
        Shortcut { sequence: StandardKey.ZoomIn; onActivated: internal.addColumn(-1) }
        Shortcut { sequence: "F11"; onActivated: Backend.toggleVisibility() }

        MouseArea { 
            anchors.fill: parent
            onWheel: (wheel) => {
                if (wheel.modifiers & Qt.ControlModifier) {
                    internal.addColumn(wheel.angleDelta.y > 0 ? -1 : 1)
                } else {
                    internal.addTickSpeed(wheel.angleDelta.y > 0 ? 1 : -1)
                }
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        Repeater {
            id: repeater
            model: window.colCount
            Component.onCompleted: ImageModel.startup()
            ListView {
                id: view
                Layout.fillHeight: true
                width: colWidth
                model: ImageModel.requestProxy(index)
                interactive: false

                delegate: Image {
                    source: model.url
                    width: window.colWidth
                    height: window.colWidth / model.ratio
                    mipmap: true
                    asynchronous: true
                }

                onAtYEndChanged: {
                    if (model == null) return
                    if (view.atYEnd) model.generateImages()
                }

                Behavior on contentY { NumberAnimation{ duration: 100 } }
                Timer { interval: 100; running: true; repeat: true; onTriggered: contentY += window.tickSpeed }
            }
        }
    }
}

