import QtQuick 2.15
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.11
import Qt.labs.platform 1.1
import Qt.labs.settings 1.0
import QtQml 2.15
import QtCore 6.2
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
        title = qsTr("Scroller") + "      " + settings.folder
        ImageModel.startup(settings.folder)
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
            property alias flags: window.flags
            property int desktopAvailableWidth
            property int desktopAvailableHeight
            property int tickSpeed: 10
            property int colCount: 5
            property string folder: StandardPaths.writableLocation(StandardPaths.PicturesLocation)
            property string saveFolder: StandardPaths.writableLocation(StandardPaths.PicturesLocation) + '/scroller/saved'
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

        FolderDialog { 
            id: folderDialog 
            onAccepted: {
                settings.folder = folderDialog.folder
                ImageModel.startup(settings.folder)
            }
        }
        function changeFolder() {
            folderDialog.folder = settings.folder
            folderDialog.open()
        }

        function openMenu(openingMenu) {
            if (openingMenu)
                menu.open()
            window.paused = openingMenu
            blur.visible = openingMenu
        }

        function toggleVisibility() {
            window.visibility = window.visibility == 5 ? 2 : 5
        }

        function saveUrl(url) {
            Backend.copyFile(url, settings.saveFolder)
        }

        Shortcut { sequence: StandardKey.Open; onActivated: internal.changeFolder() }
        Shortcut { sequence: "Esc"; onActivated: internal.openMenu(true) }
        Shortcut { sequence: StandardKey.ZoomOut; onActivated: internal.addColumn(1) }
        Shortcut { sequence: StandardKey.ZoomIn; onActivated: internal.addColumn(-1) }
        Shortcut { sequence: "F10"; onActivated: () => { settings.flags ^= Qt.FramelessWindowHint} }
        Shortcut { sequence: "F11"; onActivated: internal.toggleVisibility() }
        Shortcut { sequence: "Space"; onActivated: () => { window.paused = !window.paused } }

        MouseArea { 
            anchors.fill: parent
            onWheel: (wheel) => {
                if (wheel.modifiers & Qt.ControlModifier) {
                    internal.addColumn(wheel.angleDelta.y > 0 ? -1 : 1)
                } else if (wheel.modifiers & Qt.ShiftModifier) {
                    window.opacity += wheel.angleDelta.y > 0 ? 0.02 : -0.02
                    window.opacity = Math.min(Math.max(window.opacity, 0.02), 1)
                } else {
                    settings.tickSpeed += wheel.angleDelta.y > 0 ? 5 : -5
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
