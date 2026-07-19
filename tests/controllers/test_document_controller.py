"""Tests du contrôleur de rendu multi-documents (vue mockée)."""

from unittest.mock import MagicMock

from controllers.document_controller import DocumentController


def test_load_document_inexistant_emet_toast_danger(qtbot, temp_preferences, tmp_path):
    window = MagicMock()
    controller = DocumentController(window, "light")
    controller.load_document(str(tmp_path / "absent.md"))
    window.show_toast.assert_called_once()
    assert window.show_toast.call_args.args[0] == "danger"


def test_load_document_succes_ouvre_un_onglet(qtbot, temp_preferences, sample_markdown):
    window = MagicMock()
    controller = DocumentController(window, "light")
    loaded: list[tuple[str, str]] = []
    controller.document_loaded.connect(lambda path, title: loaded.append((path, title)))
    controller.load_document(str(sample_markdown))
    window.document.open_document.assert_called_once()
    assert loaded and loaded[0][1] == "Titre"


def test_load_document_deja_ouvert_active_l_onglet(qtbot, temp_preferences, sample_markdown):
    window = MagicMock()
    controller = DocumentController(window, "light")
    controller.load_document(str(sample_markdown))
    controller.load_document(str(sample_markdown))
    window.document.open_document.assert_called_once()
    window.document.activate_document.assert_called_with(str(sample_markdown))


def test_on_tab_activated_met_a_jour_sommaire_et_titre(qtbot, temp_preferences, sample_markdown):
    window = MagicMock()
    controller = DocumentController(window, "light")
    titles: list[str] = []
    controller.active_document_changed.connect(titles.append)
    controller.load_document(str(sample_markdown))
    controller.on_tab_activated(str(sample_markdown))
    window.toc.set_toc.assert_called_once()
    assert titles and titles[-1] == "Titre"


def test_on_tab_activated_accueil_vide_le_sommaire(qtbot, temp_preferences):
    window = MagicMock()
    controller = DocumentController(window, "light")
    titles: list[str] = []
    controller.active_document_changed.connect(titles.append)
    controller.on_tab_activated("")
    window.toc.set_toc.assert_called_with([])
    assert titles == [""]


def test_close_active_tab_ferme_l_onglet_actif(qtbot, temp_preferences, sample_markdown):
    window = MagicMock()
    controller = DocumentController(window, "light")
    controller.load_document(str(sample_markdown))
    controller.on_tab_activated(str(sample_markdown))
    controller.close_active_tab()
    window.document.close_document.assert_called_with(str(sample_markdown))


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


def test_restore_session_sans_prefs_affiche_accueil(qtbot, temp_preferences):
    window = MagicMock()
    controller = DocumentController(window, "light")
    controller.restore_session()
    window.document.set_welcome.assert_called()
    window.toc.set_toc.assert_called_with([])


def test_restore_session_rouvre_les_fichiers(qtbot, temp_preferences, sample_markdown):
    from utils import helpers

    helpers.set_preference("open_files", [str(sample_markdown)])
    helpers.set_preference("active_file", str(sample_markdown))
    window = MagicMock()
    controller = DocumentController(window, "light")
    controller.restore_session()
    window.document.open_document.assert_called_once()
    window.document.activate_document.assert_called_with(str(sample_markdown))


def test_save_session_persiste_ouvertures_et_actif(qtbot, temp_preferences, sample_markdown):
    from utils import helpers

    window = MagicMock()
    window.document.open_paths.return_value = [str(sample_markdown)]
    controller = DocumentController(window, "light")
    controller.load_document(str(sample_markdown))
    controller.on_tab_activated(str(sample_markdown))
    controller.save_session()
    assert helpers.get_preference("open_files") == [str(sample_markdown)]
    assert helpers.get_preference("active_file") == str(sample_markdown)
