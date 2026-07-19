"""Tests du contrôleur de rendu (vue mockée)."""

from unittest.mock import MagicMock

from controllers.document_controller import DocumentController


def test_load_document_inexistant_emet_toast_danger(qtbot, temp_preferences, tmp_path):
    window = MagicMock()
    controller = DocumentController(window, "light")
    controller.load_document(str(tmp_path / "absent.md"))
    window.show_toast.assert_called_once()
    assert window.show_toast.call_args.args[0] == "danger"


def test_load_document_succes_met_a_jour_la_vue(qtbot, temp_preferences, sample_markdown):
    window = MagicMock()
    controller = DocumentController(window, "light")
    loaded: list[tuple[str, str]] = []
    controller.document_loaded.connect(lambda path, title: loaded.append((path, title)))
    controller.load_document(str(sample_markdown))
    window.document.set_html.assert_called_once()
    window.toc.set_toc.assert_called_once()
    assert loaded and loaded[0][1] == "Titre"


def test_zoom_in_applique_et_persiste(qtbot, temp_preferences):
    from utils import helpers

    window = MagicMock()
    controller = DocumentController(window, "light")
    controller.zoom_in()
    window.document.set_zoom.assert_called()
    assert helpers.get_preference("zoom") is not None


def test_zoom_reset_revient_au_defaut(qtbot, temp_preferences):
    import config

    window = MagicMock()
    controller = DocumentController(window, "light")
    controller.zoom_in()
    controller.zoom_reset()
    window.document.set_zoom.assert_called_with(config.ZOOM_DEFAULT)


def test_show_welcome_affiche_et_vide_le_sommaire(qtbot, temp_preferences):
    window = MagicMock()
    controller = DocumentController(window, "light")
    controller.show_welcome()
    window.document.set_html.assert_called()
    window.toc.set_toc.assert_called_with([])
