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

    property int colCount: 3
    property int colWidth: width / colCount

    Component.onCompleted: {
        folderDialog.folder = ImageModel.getFolder()
    }

    Shortcut {
        sequence: "Ctrl+S"
        onActivated: folderDialog.open()
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

                onCurrentIndexChanged: {
                    if (model == null) return
                    console.log(model.getProxyID() + ':' + view.currentIndex)
                    if (view.currentIndex > view.count - 10)
                        model.generateImages()
                }

                Timer {
                    interval: 1000; running: true; repeat: true
                    triggeredOnStart: true
                    onTriggered: view.currentIndex += 1
                }

            }
        }
    }
    

    FolderDialog {
        id: folderDialog
        onAccepted: ImageModel.setFolder(folderDialog.folder)
    }
}

