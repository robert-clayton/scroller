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

    property int colCount: 5
    property int colWidth: width / colCount
    property int tickSpeed: 1000

    Item {
        id: internal
        function addColumn(amt) {
            if (window.colCount < 1) return
            if (amt < 0) ImageModel.removeProxy(window.colCount - 1)
            window.colCount += amt
        }

        FolderDialog { id: folderDialog }
        function changeFolder() {
            folderDialog.onAccepted.connect(() => {
                ImageModel.startup(folderDialog.folder)
            })
            folderDialog.folder = ImageModel.getFolder()
            folderDialog.open()
        }

        Shortcut { sequence: "Ctrl+S"; onActivated: internal.changeFolder() }
        Shortcut { sequence: "Ctrl+C"; onActivated: close() }
        Shortcut { sequence: "Ctrl+]"; onActivated: internal.addColumn(1) }
        Shortcut { sequence: "Ctrl+["; onActivated: internal.addColumn(-1) }
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

                Behavior on contentY { NumberAnimation{ duration: window.tickSpeed } }

                Timer {
                    id: timer
                    interval: window.tickSpeed
                    running: true
                    repeat: true
                    onTriggered: {
                        // flick(60, -70)
                        contentY += 100
                    }
                }
            }
        }
    }

    // FolderDialog {
    //     id: folderDialog
    //     // onAccepted: ImageModel.setFolder(folderDialog.folder)
    // }
}

