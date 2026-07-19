"""Contrôleur principal — chrome, navigation et état de l'application.

Gère les dialogues d'ouverture, la racine de l'explorateur, la bascule de thème,
le menu des récents, le repli des volets et la persistance de l'état fenêtre.
Possède le modèle des fichiers récents.
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication, QFileDialog

import config
from controllers.document_controller import DocumentController
from models.recent_files_model import RecentFilesModel
from utils import helpers
from views.main_window import MainWindow

logger = logging.getLogger(__name__)

_FILE_FILTER = "Fichiers Markdown (*.md *.markdown *.mdown *.mkd);;Tous les fichiers (*)"


class MainController:
    """Coordonne les actions globales et l'état de l'application."""

    def __init__(
        self,
        app: QApplication,
        window: MainWindow,
        document_controller: DocumentController,
        theme: str,
    ) -> None:
        self._app = app
        self._window = window
        self._document_controller = document_controller
        self._theme = theme
        self._recent_files = RecentFilesModel()

    # -- Ouverture -----------------------------------------------------------

    def open_file(self) -> None:
        """Ouvre un fichier Markdown via un dialogue et l'affiche."""
        start = str(helpers.get_preference("last_folder", "") or "")
        path, _ = QFileDialog.getOpenFileName(
            self._window, "Ouvrir un fichier Markdown", start, _FILE_FILTER
        )
        if path:
            self._document_controller.load_document(path)

    def open_folder(self) -> None:
        """Ouvre un dossier dans l'explorateur via un dialogue."""
        start = str(helpers.get_preference("last_folder", "") or "")
        folder = QFileDialog.getExistingDirectory(self._window, "Ouvrir un dossier", start)
        if folder:
            self._window.explorer.set_root_path(folder)
            helpers.set_preference("last_folder", folder)

    def refresh_explorer(self) -> None:
        """Recharge l'arborescence du dossier courant."""
        folder = str(helpers.get_preference("last_folder", "") or "")
        if folder and Path(folder).is_dir():
            self._window.explorer.set_root_path(folder)

    # -- Récents -------------------------------------------------------------

    def populate_recents(self) -> None:
        """(Re)construit le menu des fichiers récents à l'ouverture."""
        menu = self._window.recents_menu
        menu.clear()
        items = self._recent_files.get_all()
        if not items:
            action = menu.addAction("Aucun fichier récent")
            action.setEnabled(False)
            return
        for path in items:
            action = menu.addAction(Path(path).name)
            action.setToolTip(path)
            action.triggered.connect(
                lambda _checked=False, p=path: self._document_controller.load_document(p)
            )
        menu.addSeparator()
        menu.addAction("Effacer la liste").triggered.connect(self._recent_files.clear)

    def on_document_loaded(self, path: str, title: str) -> None:
        """Ajoute le document aux récents et met à jour le titre de la fenêtre."""
        self._recent_files.add(path)
        self._window.setWindowTitle(f"{title} — {config.APP_NAME}")

    # -- Thème ---------------------------------------------------------------

    def toggle_theme(self) -> None:
        """Bascule clair/sombre : feuille QSS, icônes, re-rendu du contenu, persistance."""
        self._theme = "dark" if self._theme == "light" else "light"
        self._app.setStyleSheet(helpers.read_stylesheet(self._theme))
        self._window.apply_theme(self._theme)
        self._document_controller.apply_theme(self._theme)
        helpers.set_preference("theme", self._theme)

    # -- Volets --------------------------------------------------------------

    def toggle_explorer(self) -> None:
        """Affiche/masque le volet explorateur et persiste l'état."""
        visible = not self._window.is_explorer_visible()
        self._window.set_explorer_visible(visible)
        helpers.set_preference("explorer_visible", visible)

    def toggle_toc(self) -> None:
        """Affiche/masque le volet sommaire et persiste l'état."""
        visible = not self._window.is_toc_visible()
        self._window.set_toc_visible(visible)
        helpers.set_preference("toc_visible", visible)

    # -- État de la fenêtre --------------------------------------------------

    def restore_state(self) -> None:
        """Restaure taille, position, volets et dernier dossier depuis les préférences."""
        size = helpers.get_preference("window_size", list(config.WINDOW_DEFAULT_SIZE))
        if isinstance(size, list) and len(size) == 2:
            self._window.resize(int(size[0]), int(size[1]))
        pos = helpers.get_preference("window_pos", None)
        if isinstance(pos, list) and len(pos) == 2:
            self._window.move(int(pos[0]), int(pos[1]))
        else:
            self._window.center_on_screen()
        sizes = helpers.get_preference("splitter_sizes", None)
        if isinstance(sizes, list) and sizes:
            self._window.set_splitter_sizes([int(s) for s in sizes])
        self._window.set_explorer_visible(bool(helpers.get_preference("explorer_visible", True)))
        self._window.set_toc_visible(bool(helpers.get_preference("toc_visible", True)))
        last_folder = str(helpers.get_preference("last_folder", "") or "")
        if last_folder and Path(last_folder).is_dir():
            self._window.explorer.set_root_path(last_folder)

    def save_state(self) -> None:
        """Persiste taille, position, tailles de volets et visibilité."""
        helpers.set_preference("window_size", [self._window.width(), self._window.height()])
        helpers.set_preference("window_pos", [self._window.x(), self._window.y()])
        helpers.set_preference("splitter_sizes", self._window.splitter_sizes())
        helpers.set_preference("explorer_visible", self._window.is_explorer_visible())
        helpers.set_preference("toc_visible", self._window.is_toc_visible())
