import QtQuick 2.15
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.11
import Qt.labs.platform 1.1
import Qt.labs.settings 1.0
import QtQml 2.15
import Qt5Compat.GraphicalEffects

import 'qrc:/delegates'

ApplicationWindow {
    id: window
    visible: true
    color: "black"
    flags: visibility == "FullScreen" ? (Qt.Window | Qt.FramelessWindowHint) : Qt.Window

    property bool paused: false
    property int colWidth: width / settings.colCount

    Component.onCompleted: {
        internal.ensureValidWindowPosition()
        title = qsTr("Scroller") + "      " + ImageModel.getFolder(true)
    }
    Component.onDestruction: internal.saveScreenLayout()

    Item {
        id: internal
        anchors.fill: parent

        property var colPositions: {'0': 0}

        Settings {
            id: settings
            property alias x: window.x
            property alias y: window.y
            property alias width: window.width
            property alias height: window.height
            property alias visibility: window.visibility
            property var desktopAvailableWidth
            property var desktopAvailableHeight
            property var tickSpeed: 10
            property var colCount: 5
        }

        function saveScreenLayout() {
            settings.desktopAvailableWidth = Screen.desktopAvailableWidth
            settings.desktopAvailableHeight = Screen.desktopAvailableHeight
        }

        function ensureValidWindowPosition() {
            var savedScreenLayout = (settings.desktopAvailableWidth === Screen.desktopAvailableWidth)
                    && (settings.desktopAvailableHeight === Screen.desktopAvailableHeight)
            window.x = (savedScreenLayout) ? settings.x : Screen.width / 2 - window.width / 2
            window.y = (savedScreenLayout) ? settings.y : Screen.height / 2 - window.height / 2
        }

        function addColumn(amt) {
            const previousWidth = window.colWidth
            if (settings.colCount + amt < 1)
                return
            for (var i = 0; i < repeater.count; i++)
                colPositions[i] = repeater.itemAt(i).contentY
            if (amt < 0)
                ImageModel.removeProxy(settings.colCount - 1)
            settings.colCount += amt
            for (var i = 0; i < repeater.count; i++) {
                const deltaWidth = window.colWidth / previousWidth
                repeater.itemAt(i).contentY = colPositions[i] * deltaWidth
            }
            if (amt < 0)
                for (var i = 0; i < Object.keys(settings.colCount).length; i++)
                    if (i > settings.colCount)
                        delete colPositions[i]
        }

        FolderDialog { id: folderDialog }
        function changeFolder() {
            folderDialog.onAccepted.connect(() => {
                ImageModel.startup(folderDialog.folder)
            })
            folderDialog.folder = ImageModel.getFolder()
            folderDialog.open()
        }

        function openMenu(openingMenu) {
            if (openingMenu)
                menu.open()
            window.paused = openingMenu
            blur.visible = openingMenu
        }

        Shortcut { sequence: StandardKey.Open; onActivated: internal.changeFolder() }
        Shortcut { sequence: "Esc"; onActivated: internal.openMenu(true) }
        Shortcut { sequence: StandardKey.ZoomOut; onActivated: internal.addColumn(1) }
        Shortcut { sequence: StandardKey.ZoomIn; onActivated: internal.addColumn(-1) }
        Shortcut { sequence: "F11"; onActivated: Backend.toggleVisibility() }
        Shortcut { sequence: "Space"; onActivated: () => { window.paused = !window.paused } }

        MouseArea { 
            anchors.fill: parent
            onWheel: (wheel) => {
                if (wheel.modifiers & Qt.ControlModifier) {
                    internal.addColumn(wheel.angleDelta.y > 0 ? -1 : 1)
                } else {
                    settings.tickSpeed += wheel.angleDelta.y > 0 ? 1 : -1
                }
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        id: container
        Repeater {
            id: repeater
            model: settings.colCount
            Component.onCompleted: ImageModel.startup()
            ListView {
                id: view
                Layout.fillHeight: true
                width: colWidth
                model: ImageModel.requestProxy(index)
                interactive: false

                delegate: 
                    Component {
                        Loader {
                            source: switch(model.type) {
                                case "gif":
                                    return "delegates/ListDelegateGif.qml"
                                default:
                                    return "delegates/ListDelegateImage.qml"
                            }
                        }
                    }

                onAtYEndChanged: {
                    if (model == null)
                        return
                    if (view.atYEnd)
                        model.generateImages()
                }
                Behavior on contentY { id: behaviorContentY; NumberAnimation{ duration: 100 } }
                Timer { interval: 100; running: !window.paused; repeat: true; onTriggered: contentY += settings.tickSpeed }
            }
        }
    }

    Popup {
        id: menu
        anchors.centerIn: parent
        width: 300
        height: 300
        visible: false
        modal: true
        focus: true
        closePolicy: Popup.CloseOnPressOutside | Popup.CloseOnEscape

        onClosed: internal.openMenu(false)
    }

    ShaderEffectSource {
        id: effectSource
        sourceItem: container
        anchors.fill: container
        sourceRect: Qt.rect(x,y, width, height)
    }

    FastBlur {
        id: blur
        anchors.fill: effectSource
        source: effectSource
        radius: 25
        visible: false
    }
}
