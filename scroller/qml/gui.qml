import QtQuick 2.15
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.11
import Qt.labs.platform 1.1
import Qt.labs.settings 1.0
import QtQml 2.15
import QtCore 6.2
import Qt5Compat.GraphicalEffects

import 'qrc:/delegates'
import 'qrc:/components'

ApplicationWindow {
    id: window
    visible: true
    color: "black"
    flags: visibility == "FullScreen" ? (Qt.Window | Qt.FramelessWindowHint) : Qt.Window

    property bool paused: false
    property int colWidth: width / settings.colCount


    Component.onCompleted: {
        internal.ensureValidWindowPosition()
        title = qsTr("Scroller") + " | " + settings.folder
        ImageModel.startup(settings.folder)
    }

    Component.onDestruction: internal.saveScreenLayout()

    Connections {
        target: settings
        function onFolderChanged() {
            title = qsTr("Scroller") + " | " + settings.folder
        }
    }
    

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
            const newCount = settings.colCount + amt
            if (newCount == 0 || newCount > 10)
                return
            
            // Save the current positions of the columns
            for (var i = 0; i < repeater.count; i++)
                colPositions[i] = repeater.itemAt(i).contentY

            settings.colCount += amt

            // Resize the columns
            for (var i = 0; i < repeater.count; i++) {
                const deltaWidth = window.colWidth / previousWidth
                repeater.itemAt(i).contentY = colPositions[i] * deltaWidth
            }

            // Remove any column positions that are no longer needed
            for (var i = 0; i < Object.keys(settings.colCount).length; i++)
                if (i > settings.colCount)
                    delete colPositions[i]
        }

        FolderDialog { 
            id: folderDialog 
            onAccepted: { 
                settings.folder = folderDialog.folder
                const curColCount = settings.colCount
                settings.colCount = 0
                ImageModel.startup(settings.folder)
                settings.colCount = curColCount
            }
        }

        function changeFolder() {
            folderDialog.folder = settings.folder
            folderDialog.open()
        }

        function toggleVisibility() {
            window.visibility = window.visibility == 5 ? 2 : 5
        }

        function saveUrl(url) {
            Backend.copyFile(url, settings.saveFolder)
        }

        Shortcut { sequence: StandardKey.Open; onActivated: internal.changeFolder() }
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
                    settings.tickSpeed = Math.min(Math.max(settings.tickSpeed, 0), 100)
                }
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        id: container
        spacing: 0
        Repeater {
            id: repeater
            model: settings.colCount
            ListView {
                id: view
                Layout.fillHeight: true
                Layout.fillWidth: true
                model: ImageModel.requestProxy(index)
                interactive: false
                cacheBuffer: 10
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
                    if (model == null) return
                    if (view.atYEnd) model.generateImages(cacheBuffer) 
                }

                Component.onDestruction: {
                    ImageModel.removeProxy(index)
                }

                Behavior on contentY { id: behaviorContentY; NumberAnimation{ duration: 100 } }
                Timer { interval: 100; running: !window.paused; repeat: true; onTriggered: contentY += settings.tickSpeed }
            }
        }
    }


    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onPositionChanged: (mouse) => {
            const lowEnough = mouse.y > 0.8 * window.height
            const tooLow = mouse.y > window.height - 5
            const tooLeft = mouse.x < bottomCenter.anchors.leftMargin
            const tooRight = mouse.x > window.width - bottomCenter.anchors.rightMargin

            if (lowEnough && !tooLow && !tooLeft && !tooRight) {
                dockMenu.open()
                bottomGradient.opacity = 1
            } else {
                dockMenu.close()
                bottomGradient.opacity = 0
            }
        }
    }

    Item {
        id: bottomCenter
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 30
        anchors.leftMargin: 10
        anchors.rightMargin: 10

        DockMenu {
            id: dockMenu
            
            buttons: [
                { text: "Change Folder" }
            ]
            callbacks: {
                "Change Folder": internal.changeFolder
            }
        }
    }

    Rectangle {
        id: bottomGradient
        width: parent.width
        height: bottomCenter.anchors.bottomMargin * 2
        anchors.bottom: parent.bottom
        opacity: 0
        z: 100
        
        gradient: Gradient {
            GradientStop { position: 1.0; color: Qt.rgba(0,0,0,1) }
            GradientStop { position: 0.9; color: Qt.rgba(0,0,0,1) }
            GradientStop { position: 0.4; color: Qt.rgba(0,0,0,.5) }
            GradientStop { position: 0.1; color: "transparent"}
        }

        Behavior on opacity { id: behaviorOpacity; NumberAnimation{ duration: 300 } }

    }
}
