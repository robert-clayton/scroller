import QtQuick 2.11

Image {
    source: model.url
    width: window.colWidth
    height: window.colWidth / model.ratio
    mipmap: true
    asynchronous: true
}