import QtQuick 2.15
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.11
import Qt.labs.platform 1.1
import Qt.labs.settings 1.0
import QtQml 2.15
import Qt5Compat.GraphicalEffects

ApplicationWindow {
    id: window
    visible: true
    width: 1600
    height: 900
    color: "transparent"
    title: qsTr("scroller")
    flags: visibility == "FullScreen" ? (Qt.Window | Qt.FramelessWindowHint) : Qt.Window
    visibility: Backend ? Backend.visibility : "Windowed"

    property bool paused: false
    property int colCount: Backend ? Backend.colCount : 1
    property int colWidth: width / colCount
    property int tickSpeed: Backend ? Backend.tickSpeed : 1
    

    Item {
        id: internal
        anchors.fill: parent

        function addColumn(amt) {
            const previousWidth = window.colWidth
            if (window.colCount + amt < 1)
                return
            for (var i = 0; i < repeater.count; i++)
                Backend.setColPosition(i, repeater.itemAt(i).contentY)
            if (amt < 0)
                ImageModel.removeProxy(window.colCount - 1)
            Backend.setColCount(window.colCount + amt)
            for (var i = 0; i < repeater.count; i++) {
                const colPosition = Backend.getColPosition(i)
                const deltaWidth = window.colWidth / previousWidth
                repeater.itemAt(i).contentY = colPosition * deltaWidth
            }
        }

        function addTickSpeed(speed) {
            Backend.setTickSpeed(window.tickSpeed + speed)
        }

        function togglePause() {
            window.paused = !window.paused
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
        Shortcut { sequence: "Space"; onActivated: internal.togglePause() }

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
        id: container
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

                delegate: Component {
                    // Loader {
                    //     source: switch(model.type) {
                    //         case "image":
                    //             model.path
                    //         case "video":
                    //             model.thumbnail
                    //         default:
                                Image {
                                    source: model.url
                                    width: window.colWidth
                                    height: window.colWidth / model.ratio
                                    mipmap: true
                                    asynchronous: true
                                }
                    //     }
                    // }
                    
                }

                onAtYEndChanged: {
                    if (model == null) return
                    if (view.atYEnd) model.generateImages()
                }
                Behavior on contentY { id: behaviorContentY; NumberAnimation{ duration: 100 } }
                Timer { interval: 100; running: !window.paused; repeat: true; onTriggered: contentY += window.tickSpeed }
            }
        }
    }

    // ShaderEffectSource {
    //     id: effectSource

    //     sourceItem: container
    //     anchors.fill: container
    //     sourceRect: Qt.rect(x,y, width, height)
    // }

    // FastBlur{
    //     id: blur
    //     anchors.fill: effectSource

    //     source: effectSource
    //     radius: 10
    // }
}

