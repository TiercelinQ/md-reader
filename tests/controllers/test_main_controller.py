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
    window.is_toc_visible.return_value = True
    window.explorer_width.return_value = 280
    window.toc_width.return_value = 240
    controller = MainController(MagicMock(), window, MagicMock(), "light")
    controller.toggle_explorer()
    window.set_explorer_visible.assert_called_once_with(False)
    assert helpers.get_preference("explorer_visible") is False


def test_toggle_explorer_persiste_la_largeur(qtbot, temp_preferences):
    window = MagicMock()
    window.is_explorer_visible.return_value = True
    window.is_toc_visible.return_value = False
    window.explorer_width.return_value = 300
    controller = MainController(MagicMock(), window, MagicMock(), "light")
    controller.toggle_explorer()
    assert helpers.get_preference("explorer_width") == 300


def test_save_state_persiste_les_largeurs_de_volets(qtbot, temp_preferences):
    window = MagicMock()
    window.is_explorer_visible.return_value = True
    window.is_toc_visible.return_value = True
    window.explorer_width.return_value = 260
    window.toc_width.return_value = 220
    window.width.return_value = 1280
    window.height.return_value = 800
    window.x.return_value = 0
    window.y.return_value = 0
    controller = MainController(MagicMock(), window, MagicMock(), "light")
    controller.save_state()
    assert helpers.get_preference("explorer_width") == 260
    assert helpers.get_preference("toc_width") == 220


def test_on_document_loaded_ajoute_aux_recents(qtbot, temp_preferences, sample_markdown):
    window = MagicMock()
    controller = MainController(MagicMock(), window, MagicMock(), "light")
    controller.on_document_loaded(str(sample_markdown), "Titre")
    assert str(sample_markdown) in controller._recent_files.get_all()


def test_on_active_document_changed_met_a_jour_le_titre(qtbot, temp_preferences):
    window = MagicMock()
    controller = MainController(MagicMock(), window, MagicMock(), "light")
    controller.on_active_document_changed("Titre")
    window.setWindowTitle.assert_called_once()
    controller.on_active_document_changed("")
    import config

    window.setWindowTitle.assert_called_with(config.APP_NAME)
