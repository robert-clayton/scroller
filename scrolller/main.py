import ctypes
import os
import random
import sys
from pathlib import Path

from PIL import Image
from PySide6.QtCore import (
    Property,
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
    Signal,
    Slot,
)
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
import scroller.qml_rc


try:
    with open(Path(__file__).resolve().parent.parent / "VERSION") as f:
        version = f.read().strip()
except FileNotFoundError:
    version = "0.0.0"

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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.imageData = []
        self.imageList = []
        self.toGenerateList = []
        self.proxies = {}

    @Slot()
    @Slot(QUrl)
    def startup(self, folder: QUrl = None):
        if folder is None:
            folder = self.getFolder()
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

    def rowCount(self, index=QModelIndex()):
        return len(self.imageData)

    def roleNames(self):
        return {
            ImageModel.url: b"url",
            ImageModel.proxyID: b"proxyID",
            ImageModel.ratio: b"ratio",
        }

    @Slot(int, result="QVariant")
    def get(self, row):
        if 0 <= row < self.rowCount():
            return self.imageData[row]

    def setFolder(self, folder: QUrl):
        folder = folder.toLocalFile()
        QSettings().setValue("folder", folder)
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount() - 1)
        self.imageData = []
        self.endRemoveRows()
        self.imageList = [
            os.path.join(folder, file)
            for file in os.listdir(folder)
            if file.endswith((".jpg", ".png"))
        ]
        random.shuffle(self.imageList)
        self.toGenerateList = self.imageList
        for proxy in self.proxies.values():
            self.generateImages(proxyID=proxy.getProxyID())

    @Slot(result=QUrl)
    def getFolder(self):
        return QUrl.fromLocalFile(
            QSettings().value(
                "folder",
                QStandardPaths.standardLocations(QStandardPaths.PicturesLocation)[0],
            )
        )

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
            try:
                with Image.open(path) as img:
                    ratio = img.size[0] / img.size[1]
            except PermissionError:  # file is not readable
                continue
            data.append(
                {"url": QUrl.fromLocalFile(path), "ratio": ratio, "proxyID": proxyID}
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
        self._visibility = QSettings().value("visibility", "Windowed")
        self._tickSpeed = QSettings().value("tickSpeed", 1000)
        self._colCount = QSettings().value("colCount", 3)

    def setVisibility(self, visibility: str):
        self._visibility = visibility
        QSettings().setValue("visibility", visibility)
        self.visibilityChanged.emit(visibility)

    @Slot()
    def toggleVisibility(self):
        self.setVisibility(
            "FullScreen" if self._visibility == "Windowed" else "Windowed"
        )

    @Slot(int)
    def setTickSpeed(self, tickSpeed: int):
        self._tickSpeed = tickSpeed
        QSettings().setValue("tickSpeed", tickSpeed)
        self.tickSpeedChanged.emit(tickSpeed)

    @Slot(int)
    def setColCount(self, colCount: int):
        self._colCount = colCount
        QSettings().setValue("colCount", colCount)
        self.colCountChanged.emit(colCount)

    visibilityChanged = Signal(str)
    tickSpeedChanged = Signal(int)
    colCountChanged = Signal(int)
    visibility = Property(
        str, lambda self: self._visibility, setVisibility, notify=visibilityChanged
    )
    tickSpeed = Property(
        int, lambda self: self._tickSpeed, setTickSpeed, notify=tickSpeedChanged
    )
    colCount = Property(
        int, lambda self: self._colCount, setColCount, notify=colCountChanged
    )


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("Ziru's Musings")
    app.setOrganizationDomain("github.com/robert-clayton")
    app.setApplicationName("scroller")
    app.setDesktopFileName("scroller")
    app.setWindowIcon(QIcon())
    myappid = f"zirus-musings.scroller.bg.{version}"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app.setApplicationVersion(version)

    backend = Backend()
    images = ImageModel()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("Backend", backend)
    engine.rootContext().setContextProperty("ImageModel", images)
    engine.load("qrc:/gui.qml")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())
