import pytest
from PySide6.QtCore import QUrl, QModelIndex
from scroller.Models.ImageModel import ImageModel

@pytest.fixture
def prefabs():
    source = ImageModel()
    source.startup(QUrl("tests/img"))
    id = 1
    return source, id, source.requestProxy(id)

def test_filterAcceptsRow(qtbot, prefabs):
    source, id, proxy = prefabs
    assert proxy.filterAcceptsRow(0, QModelIndex()) == (
        source.index(0, 0, QModelIndex()).data(ImageModel.proxyID) == id
    )

def test_generateImages(qtbot, prefabs):
    _, _, proxy = prefabs
    count = 5
    proxy.generateImages(count)
    qtbot.waitUntil(lambda: proxy.rowCount() == count, timeout=10000)
    assert proxy.rowCount() == count

def test_getProxyID(qtbot, prefabs):
    _, id, proxy = prefabs
    assert proxy.getProxyID() == id
