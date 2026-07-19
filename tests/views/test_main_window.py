"""Tests smoke de la fenêtre principale."""

import pytest

from views.main_window import MainWindow

pytestmark = pytest.mark.webengine


def test_main_window_instanciation(qtbot):
    window = MainWindow("light")
    qtbot.addWidget(window)
    assert window.btn_open_file is not None
    assert window.theme_toggle is not None


def test_main_window_expose_les_sous_vues(qtbot):
    window = MainWindow("light")
    qtbot.addWidget(window)
    assert window.explorer.objectName() == "explorer_panel"
    assert window.document.objectName() == "document_panel"
    assert window.toc.objectName() == "toc_panel"


def test_main_window_show_toast_ne_crash_pas(qtbot):
    window = MainWindow("light")
    qtbot.addWidget(window)
    window.resize(1000, 700)
    window.show_toast("info", "Bonjour")
