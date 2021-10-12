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

    property int colCount: 1
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
                model: ImageModel
                highlightRangeMode: ListView.StrictlyEnforceRange
                boundsBehavior: Flickable.StopAtBounds

                // ScrollBar.vertical: ScrollBar {
                //     id: scrollbar
                //     visible: false
                //     stepSize: .11
                //     NumberAnimation on position {
                //         id: scrollAnimation
                //         duration: 1000
                //         easing.type: Easing.Linear
                //     }

                //     Timer {
                //         interval: 1000
                //         running: true
                //         repeat: true
                //         onTriggered: scrollbar.position += scrollbar.stepSize
                //     }
                // }

                

                delegate: Image {
                    source: model.url
                    width: window.colWidth
                    height: window.colWidth / model.ratio
                }

                onCurrentIndexChanged: {
                    if (model == null) return
                    if (view.currentIndex > view.count - 10)
                        model.generateImages()
                }

            }
        }
    }

    FolderDialog {
        id: folderDialog
        onAccepted: ImageModel.setFolder(folderDialog.folder)
    }
}

