"""Contrôleur du rendu — documents ouverts en onglets, sommaire, statusbar, session.

Possède le modèle de document et l'assembleur HTML. Gère l'ensemble des documents
ouverts (un onglet chacun), la persistance de session, et intercepte les erreurs des
modèles pour les surfacer via des toasts (jamais de propagation vers la vue).
"""

import logging
from dataclasses import dataclass
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


@dataclass
class _OpenDocument:
    """État d'un document ouvert (surfaces mises à jour sans re-rendu au changement d'onglet)."""

    path: str
    title: str
    toc: list[TocEntry]
    heading_count: int
    word_count: int


class DocumentController(QObject):
    """Orchestration du rendu et des onglets de documents Markdown."""

    document_loaded = Signal(str, str)  # (path, title) — alimente les récents
    render_failed = Signal(str)
    active_document_changed = Signal(str)  # titre du document actif ("" = accueil)

    def __init__(self, window: MainWindow, theme: str) -> None:
        super().__init__()
        self._window = window
        self._model = DocumentModel()
        self._theme = theme
        self._zoom = self._clamp_zoom(helpers.get_preference("zoom", config.ZOOM_DEFAULT))
        self._open_docs: dict[str, _OpenDocument] = {}
        self._active_path: str | None = None
        self._window.document.set_zoom(self._zoom)
        self._update_info()

    # -- Chargement ----------------------------------------------------------

    def load_document(self, path: str) -> None:
        """Ouvre `path` dans un onglet (ou l'active s'il est déjà ouvert)."""
        if path in self._open_docs:
            self._window.document.activate_document(path)
            return

        self._window.set_status("Rendu…")
        try:
            doc = self._model.render(path)
        except (FileError, RenderError) as e:
            logger.exception("Échec du rendu : %s", path)
            self._window.set_status("Prêt")
            self._window.show_toast("danger", "Impossible d'afficher le document", str(e))
            self.render_failed.emit(str(e))
            return

        self._open_docs[path] = _OpenDocument(
            path=path,
            title=doc.title,
            toc=doc.toc,
            heading_count=doc.heading_count,
            word_count=doc.word_count,
        )
        self._window.document.open_document(
            path, Path(path).name, self._page(doc.body_html), self._base_url(path)
        )
        self._window.document.set_zoom(self._zoom)
        self.document_loaded.emit(path, doc.title)

    def reload(self) -> None:
        """Recharge le document actif depuis le disque, s'il y en a un."""
        if self._active_path:
            self._rerender(self._active_path)

    # -- Onglets -------------------------------------------------------------

    def on_tab_activated(self, path: str) -> None:
        """Met à jour sommaire, statusbar, libellé et titre pour l'onglet devenu actif."""
        if not path:
            self._active_path = None
            self._window.toc.set_toc([])
            self._window.set_file_label("")
            self._window.set_status("Prêt")
            self._update_info()
            self.active_document_changed.emit("")
            return
        doc = self._open_docs.get(path)
        if doc is None:
            return
        self._active_path = path
        self._window.toc.set_toc(self._to_nodes(doc.toc))
        self._window.set_file_label(Path(path).name)
        self._window.set_status(str(Path(path).parent))
        self._update_info()
        self.active_document_changed.emit(doc.title)

    def on_tab_closed(self, path: str) -> None:
        """Retire le document fermé de l'état (les surfaces suivent via tab_activated)."""
        self._open_docs.pop(path, None)

    def close_active_tab(self) -> None:
        """Ferme l'onglet actif (Ctrl+W)."""
        if self._active_path:
            self._window.document.close_document(self._active_path)

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
        """Re-rend l'accueil et chaque document ouvert dans le nouveau thème."""
        self._theme = theme
        self._window.document.set_welcome(build_welcome_page(theme))
        for path in list(self._open_docs):
            self._rerender(path)
        self._update_info()

    # -- Session -------------------------------------------------------------

    def restore_session(self) -> None:
        """Rouvre les documents de la dernière session ; sinon affiche l'accueil."""
        self._window.document.set_welcome(build_welcome_page(self._theme))
        open_files = helpers.get_preference("open_files", [])
        active_file = str(helpers.get_preference("active_file", "") or "")
        opened: list[str] = []
        if isinstance(open_files, list):
            for entry in open_files:
                path = str(entry)
                if helpers.is_markdown_file(path):
                    self.load_document(path)
                    if path in self._open_docs:
                        opened.append(path)
        if not opened:
            self.on_tab_activated("")
            return
        target = active_file if active_file in self._open_docs else opened[-1]
        self._window.document.activate_document(target)

    def save_session(self) -> None:
        """Persiste les documents ouverts et l'onglet actif."""
        helpers.set_preference("open_files", self._window.document.open_paths())
        helpers.set_preference("active_file", self._active_path or "")

    # -- Interne -------------------------------------------------------------

    def _rerender(self, path: str) -> None:
        """Re-rend `path` depuis le disque et met à jour son onglet (+ surfaces si actif)."""
        try:
            doc = self._model.render(path)
        except (FileError, RenderError):
            logger.exception("Échec du re-rendu : %s", path)
            return
        self._open_docs[path] = _OpenDocument(
            path=path,
            title=doc.title,
            toc=doc.toc,
            heading_count=doc.heading_count,
            word_count=doc.word_count,
        )
        self._window.document.update_document(path, self._page(doc.body_html), self._base_url(path))
        self._window.document.set_zoom(self._zoom)
        if path == self._active_path:
            self._window.toc.set_toc(self._to_nodes(doc.toc))
            self._update_info()

    def _page(self, body_html: str) -> str:
        """Assemble la page HTML thématisée pour le corps rendu."""
        return build_page(body_html, self._theme)

    @staticmethod
    def _base_url(path: str) -> QUrl:
        """Base URL de résolution des ressources relatives (images) du document."""
        return QUrl.fromLocalFile(str(Path(path).resolve().parent) + "/")

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
        doc = self._open_docs.get(self._active_path) if self._active_path else None
        if doc is not None:
            self._window.set_info(
                f"{percent} % · {doc.heading_count} titres · {doc.word_count} mots · {theme_label}"
            )
        else:
            self._window.set_info(f"{percent} % · {theme_label}")

    def _to_nodes(self, entries: list[TocEntry]) -> list[TocNode]:
        """Convertit les TocEntry (modèle) en TocNode (vue)."""
        return [TocNode(e.text, e.anchor, self._to_nodes(e.children)) for e in entries]
