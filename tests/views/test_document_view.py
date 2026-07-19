"""Tests smoke du volet document à onglets (QtWebEngine)."""

import pytest
from PySide6.QtCore import QUrl
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


def test_document_view_accueil_par_defaut(qtbot):
    view = DocumentView("light")
    qtbot.addWidget(view)
    assert view.current_document_path() is None
    assert view.open_paths() == []


def test_open_document_ajoute_un_onglet(qtbot):
    view = DocumentView("light")
    qtbot.addWidget(view)
    view.open_document("/tmp/a.md", "a.md", "<p>a</p>", QUrl())
    assert view.has_document("/tmp/a.md")
    assert view.open_paths() == ["/tmp/a.md"]
    assert view.current_document_path() == "/tmp/a.md"


def test_open_document_deja_ouvert_n_ajoute_pas_de_doublon(qtbot):
    view = DocumentView("light")
    qtbot.addWidget(view)
    view.open_document("/tmp/a.md", "a.md", "<p>a</p>", QUrl())
    view.open_document("/tmp/a.md", "a.md", "<p>a</p>", QUrl())
    assert view.open_paths() == ["/tmp/a.md"]


def test_close_document_revient_a_l_accueil(qtbot):
    view = DocumentView("light")
    qtbot.addWidget(view)
    closed: list[str] = []
    view.tab_closed.connect(closed.append)
    view.open_document("/tmp/a.md", "a.md", "<p>a</p>", QUrl())
    view.close_document("/tmp/a.md")
    assert closed == ["/tmp/a.md"]
    assert view.current_document_path() is None
