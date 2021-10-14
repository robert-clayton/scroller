import QtQuick 2.11

AnimatedImage {
    source: model.url
    width: window.colWidth
    height: window.colWidth / model.ratio
    mipmap: true
    asynchronous: true
    playing: true
}