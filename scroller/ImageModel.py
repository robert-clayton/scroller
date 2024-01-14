from ctypes.wintypes import VARIANT_BOOL
import random
import os
import importlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from PySide6.QtCore import QAbstractListModel, QModelIndex, QSettings, QStandardPaths, Qt, QUrl, Slot, QRunnable, QThreadPool
from PySide6.QtGui import QPixmap
from scroller.ManagedThreadPool import ManagedThreadPool
from scroller.Generator import Generator

class ImageDataWorker(QRunnable):
    def __init__(self, path, proxyID):
        super().__init__()
        self.path = path
        self.proxyID = proxyID
        self.result = None

    @Slot()
    def run(self):
        _, ext = os.path.splitext(self.path)
        ext = ext.lower()
        if ext in (".jpg", ".jpeg", ".png"):
            type_ = "image"
        elif ext == ".gif":
            type_ = "gif"
        else:
            return 

        try:
            pixmap = QPixmap(self.path)
            ratio = pixmap.width() / pixmap.height()
            self.result = {
                "url": QUrl.fromLocalFile(self.path),
                "ratio": ratio,
                "proxyID": self.proxyID,
                "type": type_,
            }
        except PermissionError:
            pass
        except ZeroDivisionError:
            print(f"Error reading image, div by zero: {self.path}")

class ImageModel(QAbstractListModel):
    """
    Custom model class for displaying a list of images in a QtQuick view
    """
    url = Qt.UserRole + 1
    proxyID = Qt.UserRole + 2
    ratio = Qt.UserRole + 3
    type = Qt.UserRole + 4

    def __init__(self, parent=None):
        """
        Initialize the ImageModel class
        """
        super().__init__(parent)
        self.imageData = []
        self.proxies = {}
        self.imageList = []
        self.toGenerateList = []

        self.threadPool = ManagedThreadPool()
        self.threadPool.setMaxThreadCount(10)

    @Slot(QUrl)
    def startup(self, folder: QUrl):
        """
        Set the folder containing the images to be displayed
        """
        self.setFolder(folder)

    def data(self, index, role=Qt.DisplayRole):
        """
        Return the data for the given role at the given index
        """
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
        """
        Return the number of rows in the model
        """
        return len(self.imageData)

    def roleNames(self):
        """
        Return the role names for the model
        """
        return {
            ImageModel.url: b"url",
            ImageModel.proxyID: b"proxyID",
            ImageModel.ratio: b"ratio",
            ImageModel.type: b"type",
        }

    @Slot(int, result="QVariant")
    def get(self, row):
        """
        Return the image data for the given row
        """
        try:
            return self.imageData[row]
        except IndexError:
            return VARIANT_BOOL()

    def setFolder(self, folder: QUrl):
        """
        Set the folder containing the images to be displayed, including images in sub-folders
        """
        folderPath = folder.toLocalFile() if folder.toLocalFile() else folder.toString()
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount() - 1)
        self.imageData = []
        self.endRemoveRows()

        def collect_images(directory):
            image_paths = []
            for file in os.listdir(directory):
                if file.endswith((".jpg", ".jpeg", ".png", ".gif")):
                    fullPath = os.path.join(directory, file)
                    image_paths.append(fullPath)
            return image_paths
        
        def get_file_info(file_path):
            try:
                return file_path, os.path.getmtime(file_path)
            except OSError:
                return file_path, 0

        # Use ThreadPoolExecutor to walk the directory structure in parallel
        with ThreadPoolExecutor() as executor:
            future_to_directory = {executor.submit(collect_images, root): root for root, dirs, files in os.walk(folderPath)}
            self.imageList = []
            for future in as_completed(future_to_directory):
                self.imageList.extend(future.result())
        
        # Retrieve file info in parallel
        with ThreadPoolExecutor() as executor:
            file_infos = list(executor.map(get_file_info, self.imageList))

        # Sort based on modification time
        file_infos.sort(key=lambda x: x[1], reverse=True)
        self.imageList = [info[0] for info in file_infos]

        # self.imageList.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        self.toGenerateList = self.imageList

        self.threadPool.cancelAll()

        for proxy in self.proxies.values():
            self.generateImages(count=10, proxyID=proxy.getProxyID())

    @Slot(result=QUrl)
    @Slot(bool, result=str)
    def getFolder(self, local: bool = False):
        """
        Return the current folder path
        """
        folder = QSettings().value(
                "folder",
                QStandardPaths.standardLocations(QStandardPaths.PicturesLocation)[0],
            )
        return folder if local else QUrl.fromLocalFile(folder)

    @Slot(list, result=list)
    def generateImageData(self, generationList: list, proxyID: int):
        threadPool = QThreadPool.globalInstance()
        workers = [ImageDataWorker(path, proxyID) for path in generationList]
        
        for worker in workers:
            threadPool.start(worker)

        threadPool.waitForDone()

        data = [worker.result for worker in workers if worker.result is not None]
        return data

    @Slot(result=bool)
    @Slot(int, result=bool)
    @Slot(int, int, result=bool)
    def generateImages(self, count: int = 1, proxyID: int = 0):
        """
        Generate images for the model
        """
        if count > len(self.toGenerateList):
            random.shuffle(self.imageList)
            self.toGenerateList = self.imageList
        
        self.toGenerateList, generationList = (
            self.toGenerateList[count:],
            self.toGenerateList[:count],
        )

        thread = Generator(self.generateImageData, generationList, proxyID)
        thread.signals.dataGenerated.connect(self._onDataGenerated)
        thread.signals.error.connect(self._onError)
        self.threadPool.start(thread)
        return True

    def _onDataGenerated(self, data):
        """
        Slot called when image data has been generated by a worker thread
        """
        index = self.rowCount()
        self.beginInsertRows(QModelIndex(), index, index + len(data) - 1)
        self.imageData.extend(data)
        self.endInsertRows()

    def _onError(self, error):
        """
        Slot called when an error occurs in a worker thread
        """
        print(f"An error occurred with the thread: {error}")

    @Slot(int, result=QAbstractListModel)
    def requestProxy(self, proxyID: int):
        """
        Return a new proxy object for the given proxy ID
        """
        importlib.import_module("scroller.ImageProxy")
        from scroller.ImageProxy import ImageProxy
        self.proxies[proxyID] = ImageProxy(self, proxyID)
        return self.proxies[proxyID]

    @Slot(int)
    def removeProxy(self, proxyID: int):
        """
        Slot called when a proxy object is deleted
        """
        self.proxies.pop(proxyID, None)
