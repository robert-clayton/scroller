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

    Component.onCompleted: {
        folderDialog.folder = ImageModel.getFolder()
        ImageModel.startup()
    }

    Shortcut {
        sequence: "Ctrl+S"
        onActivated: folderDialog.open()
    }

    Shortcut {
        sequence: "Ctrl+C"
        onActivated: close()
    }

    Shortcut {
        sequence: "Ctrl+]"
        onActivated: internal.addColumn(1)
    }

    Shortcut {
        sequence: "Ctrl+["
        onActivated: internal.addColumn(-1)
    }

    Item {
        id: internal
        function addColumn(amt) {
            window.colCount += amt
        }
    }


    RowLayout {
        anchors.fill: parent
        Repeater {
            model: window.colCount
            ListView {
                id: view
                Layout.fillHeight: true
                width: colWidth
                model: ImageModel.requestProxy()
                highlightRangeMode: ListView.StrictlyEnforceRange
                boundsBehavior: Flickable.StopAtBounds
                interactive: false
                
                highlightMoveDuration: -1
                highlightMoveVelocity: 70

                delegate: Image {
                    source: model.url
                    width: window.colWidth
                    height: window.colWidth / model.ratio
                    mipmap: true
                }

                // onCurrentIndexChanged: {
                //     if (model == null) return
                //     console.log(model.getProxyID() + ':' + view.currentIndex)
                //     if (view.currentIndex > view.count - 5)
                //         model.generateImages()
                // }

                onAtYEndChanged: {
                    if (model == null) return
                    if (view.atYEnd) {
                        model.generateImages()
                        timer.start()
                    }
                }

                Timer {
                    id: timer
                    interval: 1000;
                    onTriggered: view.currentIndex = view.count - 1
                }
            }
        }
    }

    FolderDialog {
        id: folderDialog
        onAccepted: {
            ImageModel.setFolder(folderDialog.folder)
        }
    }
}

