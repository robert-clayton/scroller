import QtQuick 2.15
import QtQuick.Controls 2.15


Dialog {
    id: dockMenu
    width: 500
    height: 100
    x: -width / 2
    property var buttons: []
    property var callbacks: []

    enter: Transition {
        NumberAnimation {
            properties: "y"
            from: dockMenu.height
            to: -dockMenu.height
            duration: 200
        }
    }

    exit: Transition {
        NumberAnimation { 
            properties: "y"
            from: -dockMenu.height
            to: dockMenu.height
            duration: 200
        }
    }

    Item {  // WRAP IT IN THE ITEM -> WORKS FOR ME
        anchors.fill: parent
        Row {
            id: menuRow
            anchors.centerIn: parent
            spacing: 10

            Repeater {
                model: dockMenu.buttons
                Button {
                    text: modelData.text
                    onClicked: dockMenu.callbacks[modelData.text]()
                }
            }

        }
    }
}
