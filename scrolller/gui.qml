import QtQuick 2.15
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.11
import Qt.labs.platform 1.1
import Qt.labs.settings 1.0
import QtQml 2.15

ApplicationWindow {
    id: window
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

    signal newImage(QUrl url)
    onNewImage: {
        const newImage = imageFactory.createObject(
            window,
            {
                'url': url,
            }
        )
    }

    Component {
        id: imageFactory
        ImageLoader {}
    }

    FolderDialog {
        id: folderDialog
        onAccepted: Backend.setFolder(folderDialog.folder)
    }
}
