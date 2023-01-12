from PySide6.QtCore import QThreadPool, QThread

class ManagedThreadPool(QThreadPool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.activeThreads = []
    
    def start(self, runnable, priority=QThread.NormalPriority):
        runnable.signals.finished.connect(lambda : self._onRunnableFinished(runnable))
        self.activeThreads.append(runnable)
        super().start(runnable, priority)
    
    def cancel(self, runnable):
        if runnable in self.activeThreads:
            runnable.signals.finished.disconnect()
            self.activeThreads.remove(runnable)
        else:
            print("Thread not found")
    
    def cancelAll(self):
        for runnable in self.activeThreads:
            self.cancel(runnable)
    
    def _onRunnableFinished(self, runnable):
        if runnable in self.activeThreads:
            self.activeThreads.remove(runnable)