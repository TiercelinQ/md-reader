"""Point d'entrée de MD Reader — ordre d'initialisation strict."""

import logging
import sys
from pathlib import Path
from types import TracebackType

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

import config
from controllers.document_controller import DocumentController
from controllers.main_controller import MainController
from utils import helpers
from utils.logger import setup_logging
from utils.resource_path import resource_path
from views.main_window import MainWindow
from views.splash_screen import create_splash

logger = logging.getLogger(__name__)


def _resolve_startup_theme(app: QApplication) -> str:
    """Renvoie le thème persisté, sinon celui du système d'exploitation."""
    pref = helpers.get_preference("theme", None)
    if pref in ("light", "dark"):
        return str(pref)
    try:
        if app.styleHints().colorScheme() == Qt.ColorScheme.Dark:
            return "dark"
    except (AttributeError, RuntimeError):
        pass
    return "light"


def install_excepthook(window: MainWindow) -> None:
    """Installe un excepthook global qui logge puis notifie via toast."""

    def hook(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_tb: TracebackType | None,
    ) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        logger.critical("Exception non capturée", exc_info=(exc_type, exc_value, exc_tb))
        try:
            window.show_toast("danger", "Erreur inattendue", f"{exc_type.__name__} : {exc_value}")
        except Exception:
            logger.exception("Échec affichage toast d'erreur critique")

    sys.excepthook = hook


def _wire(
    window: MainWindow,
    document_controller: DocumentController,
    main_controller: MainController,
) -> None:
    """Câble les signaux des vues vers les contrôleurs."""
    window.btn_open_file.clicked.connect(main_controller.open_file)
    window.btn_open_folder.clicked.connect(main_controller.open_folder)
    window.explorer.refresh_requested.connect(main_controller.refresh_explorer)
    window.theme_toggle.clicked.connect(main_controller.toggle_theme)
    window.btn_toggle_explorer.clicked.connect(main_controller.toggle_explorer)
    window.btn_toggle_toc.clicked.connect(main_controller.toggle_toc)
    window.recents_menu.aboutToShow.connect(main_controller.populate_recents)
    document_controller.document_loaded.connect(main_controller.on_document_loaded)

    window.explorer.file_selected.connect(document_controller.load_document)
    window.toc.heading_selected.connect(document_controller.on_heading_selected)
    window.document.external_link_clicked.connect(document_controller.on_external_link)
    window.btn_search.clicked.connect(document_controller.toggle_search)
    window.btn_zoom_in.clicked.connect(document_controller.zoom_in)
    window.btn_zoom_out.clicked.connect(document_controller.zoom_out)
    window.zoom_reset_requested.connect(document_controller.zoom_reset)
    window.reload_requested.connect(document_controller.reload)


def main() -> None:
    """Démarre l'application."""
    setup_logging()
    logger.info("Démarrage %s %s", config.APP_NAME, config.APP_VERSION)

    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setStyle("Fusion")

    icon_path = resource_path("resources/icon.ico")
    if Path(icon_path).exists():
        app.setWindowIcon(QIcon(icon_path))

    theme = _resolve_startup_theme(app)
    app.setStyleSheet(helpers.read_stylesheet(theme))

    splash = create_splash(theme)
    splash.show()
    app.processEvents()

    window = MainWindow(theme)
    install_excepthook(window)
    document_controller = DocumentController(window, theme)
    main_controller = MainController(app, window, document_controller, theme)
    _wire(window, document_controller, main_controller)

    main_controller.restore_state()
    document_controller.show_welcome()
    app.aboutToQuit.connect(main_controller.save_state)

    window.show()
    QTimer.singleShot(config.SPLASH_MIN_DURATION_MS, lambda: splash.finish(window))
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
