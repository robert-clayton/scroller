import os
from pathlib import Path
import sys
import ctypes
import secrets
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QSettings, QUrl, QObject, Signal, Slot, QStandardPaths, \
    QtInfoMsg, QtWarningMsg, QtCriticalMsg, QtFatalMsg,  QStringListModel
from PySide6.QtGui import QIcon
from . import qml_rc


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


class Backend(QObject):
    exampleSignal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.images = QStringListModel()
        # self.images.setStringList(['/home/user/Pictures/1.jpg', '/home/user/Pictures/2.jpg'])

    @Slot(result=bool)
    def getRandomImage(self):
        return True

    @Slot(QUrl, result=bool)
    def setFolder(self, folder: QUrl):
        QSettings().setValue('folder', folder.toLocalFile())
        stringList = []
        for dir, _, files in os.walk(folder.toLocalFile()):
            for file in files:
                stringList.append(f'{dir}/{file}')
        self.images.setStringList(stringList)
        return True

    @Slot(result=QUrl)
    def getFolder(self):
        return QUrl.fromLocalFile(QSettings().value('folder', QStandardPaths.standardLocations(QStandardPaths.PicturesLocation)[0]))
    
    @Slot(result=QUrl)
    def getRandomImage(self):
        return QUrl.fromLocalFile(secrets.choice(self.images.stringList()))

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
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("Backend", backend)
    gui = os.fspath(Path(__file__).resolve().parent / 'gui.qml')
    engine.load(QUrl.fromLocalFile(gui))

    if not engine.rootObjects():
        sys.exit(-1)
        
    sys.exit(app.exec_())