import ctypes
import os
import random
import sys
import shutil
from pathlib import Path
from PIL import Image

from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QObject,
    QSettings,
    QSortFilterProxyModel,
    QStandardPaths,
    Qt,
    QtCriticalMsg,
    QtFatalMsg,
    QtInfoMsg,
    QtWarningMsg,
    QUrl,
    Slot,
)
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

import scroller.qml_rc

def qt_message_handler(mode, context, message):
    if mode == QtInfoMsg:
        mode = "Info"
    elif mode == QtWarningMsg:
        mode = "Warning"
    elif mode == QtCriticalMsg:
        mode = "critical"
    elif mode == QtFatalMsg:
        mode = "fatal"
    else:
        mode = "Debug"
    print(
        "%s: %s (%s:%d, %s)" % (mode, message, context.file, context.line, context.file)
    )


class ImageProxy(QSortFilterProxyModel):
    def __init__(self, source, proxyID):
        super().__init__()
        self.setSourceModel(source)
        self.proxyID = proxyID

    def filterAcceptsRow(self, source_row, source_parent):
        return (
            self.sourceModel()
            .index(source_row, 0, source_parent)
            .data(ImageModel.proxyID)
            == self.proxyID
        )

    @Slot()
    def generateImages(self):
        self.sourceModel().generateImages(proxyID=self.proxyID)

    @Slot(result=int)
    def getProxyID(self):
        return self.proxyID


class ImageModel(QAbstractListModel):
    url = Qt.UserRole + 1
    proxyID = Qt.UserRole + 2
    ratio = Qt.UserRole + 3
    type = Qt.UserRole + 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self.imageData = []
        self.imageList = []
        self.toGenerateList = []
        self.proxies = {}

    @Slot(QUrl)
    def startup(self, folder: QUrl):
        self.setFolder(folder)

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if index.isValid() and 0 <= row < self.rowCount():
            if role == ImageModel.url:
                return self.imageData[row]["url"]
            elif role == ImageModel.proxyID:
                return self.imageData[row]["proxyID"]
            elif role == ImageModel.ratio:
                return self.imageData[row]["ratio"]
            elif role == ImageModel.type:
                return self.imageData[row]["type"]

    def rowCount(self, index=QModelIndex()):
        return len(self.imageData)

    def roleNames(self):
        return {
            ImageModel.url: b"url",
            ImageModel.proxyID: b"proxyID",
            ImageModel.ratio: b"ratio",
            ImageModel.type: b"type",
        }

    @Slot(int, result="QVariant")
    def get(self, row):
        if 0 <= row < self.rowCount():
            return self.imageData[row]

    def setFolder(self, folder: QUrl):
        folder = folder.toLocalFile() if folder.toLocalFile() else folder.toString()
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount() - 1)
        self.imageData = []
        self.endRemoveRows()
        self.imageList = [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith((".jpg", ".jpeg", ".png", ".gif"))]
        random.shuffle(self.imageList)
        self.toGenerateList = self.imageList
        for proxy in self.proxies.values():
            self.generateImages(proxyID=proxy.getProxyID())

    @Slot(result=QUrl)
    @Slot(bool, result=str)
    def getFolder(self, local: bool = False):
        folder = QSettings().value(
                "folder",
                QStandardPaths.standardLocations(QStandardPaths.PicturesLocation)[0],
            )
        return folder if local else QUrl.fromLocalFile(folder)

    def generateImageData(self, count: int, proxyID: int):
        if count > len(self.toGenerateList):
            random.shuffle(self.imageList)
            self.toGenerateList = self.imageList
        data = []
        self.toGenerateList, generatingList = (
            self.toGenerateList[count:],
            self.toGenerateList[:count],
        )
        for path in generatingList:
            if path.endswith((".jpg", ".jpeg", "png")):
                type_ = "image"
            elif path.endswith((".gif")):
                type_ = "gif"
            else:
                continue

            try:
                with Image.open(path) as img:
                    ratio = img.size[0] / img.size[1]
            except PermissionError:  # file is not readable
                continue
            data.append(
                {
                    "url": QUrl.fromLocalFile(path),
                    "ratio": ratio,
                    "proxyID": proxyID,
                    "type": type_,
                }
            )
        return data

    @Slot(result=bool)
    @Slot(int, result=bool)
    @Slot(int, int, result=bool)
    def generateImages(self, count: int = 5, proxyID: int = 0):
        self.beginInsertRows(
            QModelIndex(), self.rowCount(), self.rowCount() + count - 1
        )
        self.imageData.extend(self.generateImageData(count, proxyID))
        self.endInsertRows()
        return True

    @Slot(int, result=QAbstractListModel)
    def requestProxy(self, proxyID: int):
        self.proxies[proxyID] = ImageProxy(self, proxyID)
        return self.proxies[proxyID]

    @Slot(int)
    def removeProxy(self, proxyID: int):
        self.proxies.pop(proxyID, None)

class Backend(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    @Slot(QUrl, QUrl, result=bool)
    def copyFile(self, source: QUrl, destination: QUrl):
        source = source.toLocalFile()
        name = os.path.basename(source)
        destination = destination.toLocalFile()
        if not os.path.exists(destination):
            os.makedirs(destination)
        
        try:
            shutil.copy(source, os.path.join(destination, name))
            return True
        except PermissionError:
            return False


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("Ziru's Musings")
    app.setOrganizationDomain("github.com/robert-clayton")
    app.setApplicationName("scroller")
    app.setDesktopFileName("scroller")
    app.setWindowIcon(QIcon())
    myappid = f"zirus-musings.scroller.bg.dev"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app.setApplicationVersion('dev')

    backend = Backend()
    images = ImageModel()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("ImageModel", images)
    engine.rootContext().setContextProperty("Backend", backend)
    engine.load("qrc:/gui")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())
