"""Tests smoke du volet explorateur."""

from PySide6.QtWidgets import QToolButton

from views.explorer_view import ExplorerView


def test_explorer_view_objectname(qtbot):
    view = ExplorerView("light")
    qtbot.addWidget(view)
    assert view.objectName() == "explorer_panel"


def test_explorer_view_a_le_bouton_rafraichir(qtbot):
    view = ExplorerView("light")
    qtbot.addWidget(view)
    assert view.findChild(QToolButton, "btn_refresh") is not None


def test_explorer_view_set_root_path_ne_crash_pas(qtbot, tmp_path):
    (tmp_path / "doc.md").write_text("# x", encoding="utf-8")
    view = ExplorerView("light")
    qtbot.addWidget(view)
    view.set_root_path(str(tmp_path))
