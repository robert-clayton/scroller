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

    Component.onCompleted: {
        folderDialog.folder = ImageModel.getFolder()
    }

    Shortcut {
        sequence: "Ctrl+S"
        onActivated: folderDialog.open()
    }

    ListView{
        id: view
        property int colWidth: window.width / 3
        anchors.fill: parent
        model: ImageModel
        highlightRangeMode: ListView.StrictlyEnforceRange

        delegate: Image {
            source: model.url
            width: view.colWidth
            height: view.colWidth / model.ratio
        }

        
        onCurrentIndexChanged: {
            if (view.currentIndex == view.count - 1) {
                console.debug('Scrolled to bottom ' + count)
                ImageModel.generateImages()
            }
            console.debug('Current index changed ' + view.currentIndex)
        }
    }

    FolderDialog {
        id: folderDialog
        onAccepted: ImageModel.setFolder(folderDialog.folder)
    }
}

