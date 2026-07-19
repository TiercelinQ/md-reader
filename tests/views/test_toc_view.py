"""Tests smoke du volet sommaire."""

from views.toc_view import TocNode, TocView


def test_toc_view_objectname(qtbot):
    view = TocView()
    qtbot.addWidget(view)
    assert view.objectName() == "toc_panel"


def test_toc_view_set_toc_ne_crash_pas(qtbot):
    view = TocView()
    qtbot.addWidget(view)
    view.set_toc([TocNode("Intro", "intro", [TocNode("Détail", "detail", [])])])


def test_toc_view_set_toc_vide_ne_crash_pas(qtbot):
    view = TocView()
    qtbot.addWidget(view)
    view.set_toc([])
