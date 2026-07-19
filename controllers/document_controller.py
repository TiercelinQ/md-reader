"""Contrôleur du rendu — charge un document, met à jour la vue web, le sommaire, la statusbar.

Possède le modèle de document et l'assembleur HTML. Intercepte les erreurs des modèles
et les surface via des toasts (jamais de propagation vers la vue).
"""

import logging
from pathlib import Path

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtGui import QDesktopServices

import config
from models.document_model import DocumentModel, TocEntry
from models.exceptions import FileError, RenderError
from models.html_builder import build_page, build_welcome_page
from utils import helpers
from views.main_window import MainWindow
from views.toc_view import TocNode

logger = logging.getLogger(__name__)

_THEME_LABEL = {"light": "Clair", "dark": "Sombre"}


class DocumentController(QObject):
    """Orchestration du rendu d'un document Markdown."""

    document_loaded = Signal(str, str)  # (path, title)
    render_failed = Signal(str)

    def __init__(self, window: MainWindow, theme: str) -> None:
        super().__init__()
        self._window = window
        self._model = DocumentModel()
        self._theme = theme
        self._zoom = self._clamp_zoom(helpers.get_preference("zoom", config.ZOOM_DEFAULT))
        self._current_path: str | None = None
        self._showing_welcome = False
        self._heading_count = 0
        self._word_count = 0
        self._window.document.set_zoom(self._zoom)
        self._update_info()

    # -- Chargement ----------------------------------------------------------

    def show_welcome(self) -> None:
        """Affiche la page d'accueil (présentation, icônes, raccourcis) — aucun document ouvert."""
        self._current_path = None
        self._showing_welcome = True
        self._heading_count = 0
        self._word_count = 0
        self._window.document.set_html(build_welcome_page(self._theme), QUrl())
        self._window.document.set_zoom(self._zoom)
        self._window.toc.set_toc([])
        self._window.set_file_label("")
        self._window.set_status("Prêt")
        self._update_info()

    def load_document(self, path: str) -> None:
        """Rend le fichier `path` et met à jour toutes les surfaces."""
        self._window.set_status("Rendu…")
        try:
            doc = self._model.render(path)
        except (FileError, RenderError) as e:
            logger.exception("Échec du rendu : %s", path)
            self._window.set_status("Prêt")
            self._window.show_toast("danger", "Impossible d'afficher le document", str(e))
            self.render_failed.emit(str(e))
            return

        self._display(path, doc.body_html)
        self._window.toc.set_toc(self._to_nodes(doc.toc))
        self._current_path = path
        self._showing_welcome = False
        self._heading_count = doc.heading_count
        self._word_count = doc.word_count
        self._window.set_file_label(Path(path).name)
        self._window.set_status(f"Chargé : {Path(path).name}")
        self._update_info()
        self.document_loaded.emit(path, doc.title)

    def reload(self) -> None:
        """Recharge le document courant, s'il y en a un."""
        if self._current_path:
            self.load_document(self._current_path)

    # -- Zoom ----------------------------------------------------------------

    def zoom_in(self) -> None:
        """Augmente le zoom du contenu."""
        self._set_zoom(self._zoom + config.ZOOM_STEP)

    def zoom_out(self) -> None:
        """Diminue le zoom du contenu."""
        self._set_zoom(self._zoom - config.ZOOM_STEP)

    def zoom_reset(self) -> None:
        """Réinitialise le zoom du contenu."""
        self._set_zoom(config.ZOOM_DEFAULT)

    # -- Recherche / navigation ----------------------------------------------

    def toggle_search(self) -> None:
        """Affiche/masque la barre de recherche."""
        self._window.document.toggle_find_bar()

    def on_heading_selected(self, anchor: str) -> None:
        """Défile le document vers le titre sélectionné dans le sommaire."""
        self._window.document.scroll_to_anchor(anchor)

    def on_external_link(self, url: QUrl) -> None:
        """Ouvre un lien externe dans le navigateur système."""
        QDesktopServices.openUrl(url)

    # -- Thème ---------------------------------------------------------------

    def apply_theme(self, theme: str) -> None:
        """Re-rend le document courant (ou la page d'accueil) dans le nouveau thème."""
        self._theme = theme
        if self._current_path:
            try:
                doc = self._model.render(self._current_path)
            except (FileError, RenderError):
                logger.exception("Échec du re-rendu au changement de thème")
            else:
                self._display(self._current_path, doc.body_html)
            self._update_info()
        elif self._showing_welcome:
            self.show_welcome()
        else:
            self._update_info()

    # -- Interne -------------------------------------------------------------

    def _display(self, path: str, body_html: str) -> None:
        """Injecte le HTML thématisé dans la vue web avec la bonne base URL."""
        html = build_page(body_html, self._theme)
        base_url = QUrl.fromLocalFile(str(Path(path).resolve().parent) + "/")
        self._window.document.set_html(html, base_url)
        self._window.document.set_zoom(self._zoom)

    def _set_zoom(self, factor: float) -> None:
        self._zoom = self._clamp_zoom(factor)
        self._window.document.set_zoom(self._zoom)
        helpers.set_preference("zoom", self._zoom)
        self._update_info()

    @staticmethod
    def _clamp_zoom(factor: object) -> float:
        value = float(factor) if isinstance(factor, (int, float)) else config.ZOOM_DEFAULT
        return round(min(config.ZOOM_MAX, max(config.ZOOM_MIN, value)), 2)

    def _update_info(self) -> None:
        percent = int(round(self._zoom * 100))
        theme_label = _THEME_LABEL.get(self._theme, "")
        if self._current_path:
            self._window.set_info(
                f"{percent} % · {self._heading_count} titres · "
                f"{self._word_count} mots · {theme_label}"
            )
        else:
            self._window.set_info(f"{percent} % · {theme_label}")

    def _to_nodes(self, entries: list[TocEntry]) -> list[TocNode]:
        """Convertit les TocEntry (modèle) en TocNode (vue)."""
        return [TocNode(e.text, e.anchor, self._to_nodes(e.children)) for e in entries]
