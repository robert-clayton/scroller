import QtQuick 2.15
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.11
import Qt.labs.platform 1.1
import Qt.labs.settings 1.0
import QtQml 2.15

Window {
    visible: true
    width: 640
    height: 480
    title: qsTr("scrolller")

    Component.onCompleted: {
        folderDialog.folder = Backend.getFolder()
        imagesView.model = Backend.images
    }

    Shortcut {
        sequence: "Ctrl+S"
        onActivated: folderDialog.open()
    }

    ScrollView {
        id: scroll
        width: 200
        height: 200
        clip: true
        property int tickTimerMS: 1000

        ScrollBar.horizontal: ScrollBar { visible: false }
        ScrollBar.vertical: ScrollBar {
            id: scrollBar
            parent: scroll
            visible: false
            stepSize: .01
            NumberAnimation on position {
                id: scrollAnimation
                duration: scroll.tickTimerMS
                easing.type: Easing.Linear
            }
        }

        ListView {
            id: imagesView
            boundsBehavior: Flickable.StopAtBounds
            delegate: ItemDelegate {
                    id: imageDelegate
                    Image {
                        id: image
                        anchors.fill: parent
                        source: modelData.source
                    }
                }
        
            onAtYEndChanged: {
                if (atYEnd) {
                }
            }
        }
    }

    Timer {
        id: tickTimer
        running: true
        repeat: true
        interval: 500
        onTriggered: scrollBar.increase()
    }

    FolderDialog {
        id: folderDialog
        onAccepted: Backend.setFolder(folderDialog.folder)
    }
}
