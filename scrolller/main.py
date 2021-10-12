import os
from pathlib import Path
import sys
import ctypes
import secrets
import random
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import Qt, QSettings, QUrl, QObject, Signal, Slot, QStandardPaths, \
    QtInfoMsg, QtWarningMsg, QtCriticalMsg, QtFatalMsg,  QAbstractListModel, QModelIndex
from PySide6.QtGui import QIcon
from PIL import Image
# from . import qml_rc


try:
    with open(Path(__file__).resolve().parent.parent / 'VERSION') as f:
        version = f.read().strip()
except FileNotFoundError:
    version = '0.0.0'


def qt_message_handler(mode, context, message):
    if mode == QtInfoMsg:
        mode = 'Info'
    elif mode == QtWarningMsg:
        mode = 'Warning'
    elif mode == QtCriticalMsg:
        mode = 'critical'
    elif mode == QtFatalMsg:
        mode = 'fatal'
    else:
        mode = 'Debug'
    print("%s: %s (%s:%d, %s)" % (mode, message, context.file, context.line, context.file))


class ImageModel(QAbstractListModel):
    url = Qt.UserRole + 1
    name = Qt.UserRole + 2
    ratio = Qt.UserRole + 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self.imageData = []
        self.imageList = []
        self.setFolder(self.getFolder())

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if index.isValid() and 0 <= row < self.rowCount():
            if role == ImageModel.url:
                return self.imageData[row]["url"]
            elif role == ImageModel.name:
                return self.imageData[row]["name"]
            elif role == ImageModel.ratio:
                return self.imageData[row]["ratio"]

    def rowCount(self, index=QModelIndex()):
        return len(self.imageData)

    def roleNames(self):
        return {
            ImageModel.url: b'url',
            ImageModel.name: b'name',
            ImageModel.ratio: b'ratio'
        }

    @Slot(int, result='QVariant')
    def get(self, row):
        if 0 <= row < self.rowCount():
            return self.imageData[row]

    @Slot(QUrl, result=bool)
    def setFolder(self, folder: QUrl):
        folder = folder.toLocalFile()
        QSettings().setValue('folder', folder)
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount() - 1)
        self.imageData = []
        self.endRemoveRows()
        self.imageList = [os.path.join(folder, file) for folder, _, files in os.walk(folder) for file in files if file.endswith(('.jpg', '.png'))]
        random.shuffle(self.imageList)
        self.toGenerateList = self.imageList
        return self.generateImages()

    @Slot(result=QUrl)
    def getFolder(self):
        return QUrl.fromLocalFile(QSettings().value('folder', QStandardPaths.standardLocations(QStandardPaths.PicturesLocation)[0]))

    def generateImageData(self, count: int):
        if count > len(self.toGenerateList):
            random.shuffle(self.imageList)
            self.toGenerateList = self.imageList
        data = []
        self.toGenerateList, generatingList = self.toGenerateList[count:], self.toGenerateList[:count]
        for path in generatingList:
            try:
                with Image.open(path) as img:
                    ratio = img.size[0] / img.size[1]
            except PermissionError: # file is not readable
                continue
            data.append({ "url": QUrl.fromLocalFile(path), "ratio": ratio })
        return data

    @Slot(result=bool)
    @Slot(int, result=bool)
    def generateImages(self, count: int = 5):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount() + count - 1)
        self.imageData.extend(self.generateImageData(count))
        self.endInsertRows()
        return True

class Backend(QObject):
    exampleSignal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName('Ziru\'s Musings')
    app.setOrganizationDomain('github.com/robert-clayton')
    app.setApplicationName('scrolller')
    app.setDesktopFileName('scrolller')
    app.setWindowIcon(QIcon())
    myappid = f'zirus-musings.scrolller.bg.{version}'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app.setApplicationVersion(version)

    backend = Backend()
    images = ImageModel()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("Backend", backend)
    engine.rootContext().setContextProperty("ImageModel", images)
    gui = os.fspath(Path(__file__).resolve().parent / 'gui.qml')
    engine.load(QUrl.fromLocalFile(gui))

    if not engine.rootObjects():
        sys.exit(-1)
        
    sys.exit(app.exec_())
