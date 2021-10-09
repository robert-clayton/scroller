import os
import sys
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QIcon
from . import qml_rc

try:
    with open(os.path.join(os.path.pardir(__file__), 'VERSION')) as f:
        version = f.read().strip()
except FileNotFoundError:
    version = '0.0.0'

class Backend(QObject):
    exampleSignal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
    
    @Slot(result=bool)
    def exampleSlot(self):
        return True

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

    engine.load(':/gui.qml')

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())