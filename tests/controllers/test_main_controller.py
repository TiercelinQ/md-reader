"""Tests du contrôleur principal (app/vue/document mockés)."""

from unittest.mock import MagicMock

from controllers.main_controller import MainController
from utils import helpers


def test_toggle_theme_bascule_persiste_et_propage(qtbot, temp_preferences):
    app, window, document = MagicMock(), MagicMock(), MagicMock()
    controller = MainController(app, window, document, "light")
    controller.toggle_theme()
    app.setStyleSheet.assert_called_once()
    window.apply_theme.assert_called_once_with("dark")
    document.apply_theme.assert_called_once_with("dark")
    assert helpers.get_preference("theme") == "dark"


def test_toggle_explorer_masque_et_persiste(qtbot, temp_preferences):
    window = MagicMock()
    window.is_explorer_visible.return_value = True
    controller = MainController(MagicMock(), window, MagicMock(), "light")
    controller.toggle_explorer()
    window.set_explorer_visible.assert_called_once_with(False)
    assert helpers.get_preference("explorer_visible") is False


def test_on_document_loaded_met_a_jour_le_titre(qtbot, temp_preferences, sample_markdown):
    window = MagicMock()
    controller = MainController(MagicMock(), window, MagicMock(), "light")
    controller.on_document_loaded(str(sample_markdown), "Titre")
    window.setWindowTitle.assert_called_once()
