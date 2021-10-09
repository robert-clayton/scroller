import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.11
import QtQml 2.15

import "qrc:/objects"

ApplicationWindow {
    id: application
    width: 820
    height: 450

    maximumHeight: height
    maximumWidth: width

    minimumHeight: height
    minimumWidth: width

    color: Style.slate3
    visible: true

    Component.onCompleted: {
        Backend.exampleSignal.connect(onExampleSignal)
    }

    function onExampleSignal() {
        console.log('Example signal fired!')
    }
}