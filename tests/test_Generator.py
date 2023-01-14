import pytest
from PySide6.QtCore import QThreadPool
from scroller.Generator import Generator

@pytest.fixture
def task_successful():
    def task(generationList, proxyID):
        return [1, 2, 3]
    return task

@pytest.fixture
def task_error():
    def task(generationList, proxyID):
        raise ValueError("test error")
    return task

def test_dataGenerated(qtbot, task_successful):
    generator = Generator(task_successful, [], 1)
    data_generated = False
    error_emitted = False
    finished_emitted = False

    def data_generated_callback(data):
        nonlocal data_generated
        data_generated = True
        assert data == [1, 2, 3]

    def error_callback(error):
        nonlocal error_emitted
        error_emitted = True

    def finished_callback():
        nonlocal finished_emitted
        finished_emitted = True

    generator.signals.dataGenerated.connect(data_generated_callback)
    generator.signals.error.connect(error_callback)
    generator.signals.finished.connect(finished_callback)

    QThreadPool.globalInstance().start(generator)
    qtbot.waitUntil(lambda: data_generated, timeout=200)

    assert data_generated
    assert not error_emitted
    assert finished_emitted

def test_error(qtbot, task_error):
    generator = Generator(task_error, [], 1)
    data_generated = False
    error_emitted = False
    finished_emitted = False

    def data_generated_callback(data):
        nonlocal data_generated
        data_generated = True

    def error_callback(error):
        nonlocal error_emitted
        error_emitted = True
        assert error == "test error"

    def finished_callback():
        nonlocal finished_emitted
        finished_emitted = True

    generator.signals.dataGenerated.connect(data_generated_callback)
    generator.signals.error.connect(error_callback)
    generator.signals.finished.connect(finished_callback)

    generator.run()

    assert not data_generated
    assert error_emitted
    assert finished_emitted

def test_run(qtbot, task_successful):
    generator = Generator(task_successful, [], 1)
    data_generated = False
    error_emitted = False
    finished_emitted = False

    def data_generated_callback(data):
        nonlocal data_generated
        data_generated = True
        assert data == [1, 2, 3]

    def error_callback(error):
        nonlocal error_emitted
        error_emitted = True

    def finished_callback():
        nonlocal finished_emitted
        finished_emitted = True

    generator.signals.dataGenerated.connect(data_generated_callback)
    generator.signals.error.connect(error_callback)
    generator.signals.finished.connect(finished_callback)

    generator.run()

    assert data_generated
    assert not error_emitted
    assert finished_emitted
