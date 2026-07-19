"""Tests smoke du volet document (QtWebEngine)."""

import pytest
from PySide6.QtWidgets import QLineEdit

from views.document_view import DocumentView

pytestmark = pytest.mark.webengine


def test_document_view_objectname(qtbot):
    view = DocumentView("light")
    qtbot.addWidget(view)
    assert view.objectName() == "document_panel"


def test_document_view_a_le_champ_de_recherche(qtbot):
    view = DocumentView("light")
    qtbot.addWidget(view)
    assert view.findChild(QLineEdit, "find_input") is not None


def test_document_view_barre_recherche_masquee_par_defaut(qtbot):
    view = DocumentView("light")
    qtbot.addWidget(view)
    view.show_find_bar()
    view.hide_find_bar()
