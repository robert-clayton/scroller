import ctypes
import os
import sys
import shutil
from PySide6.QtCore import QObject, QtCriticalMsg, QtFatalMsg, QtInfoMsg, QtWarningMsg, QUrl, Slot
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
from scroller.ImageModel import ImageModel
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
