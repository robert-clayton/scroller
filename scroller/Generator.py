from PySide6.QtCore import QObject, QRunnable, Signal

class GeneratorSignals(QObject):
    dataGenerated = Signal(list)
    error = Signal(str)
    imageFolderSet = Signal()
    finished = Signal()

class Generator(QRunnable):
    def __init__(self, task, generationList: list, proxyID: int):
        super().__init__()
        self.signals = GeneratorSignals()
        self.task = task
        self.generationList = generationList
        self.proxyID = proxyID

    def run(self):
        try:
            data = self.task(self.generationList, self.proxyID)
            self.signals.dataGenerated.emit(data)
        except Exception as e:
            self.signals.error.emit(str(e))
        self.signals.finished.emit()