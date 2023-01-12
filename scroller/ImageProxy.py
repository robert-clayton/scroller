from PySide6.QtCore import QSortFilterProxyModel, Slot
from scroller.ImageModel import ImageModel

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

    @Slot(int)
    def generateImages(self, count: int):
        self.sourceModel().generateImages(count=count, proxyID=self.proxyID)

    @Slot(result=int)
    def getProxyID(self):
        return self.proxyID
