"""Fenêtre principale — topbar à boutons + QSplitter (explorateur|document|sommaire) + statusbar.

PySide6 uniquement, aucune logique métier : expose les sous-vues, les boutons (signaux),
et des méthodes d'affichage. Les contrôleurs câblent le comportement.
"""

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import (
    QCloseEvent,
    QGuiApplication,
    QIcon,
    QKeySequence,
    QResizeEvent,
    QShortcut,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QSplitter,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

import config
from utils.icons import get_icon
from utils.resource_path import resource_path
from views.document_view import DocumentView
from views.explorer_view import ExplorerView
from views.toast_manager import ToastManager
from views.toc_view import TocView


class MainWindow(QMainWindow):
    """Fenêtre principale de MD Reader."""

    zoom_reset_requested = Signal()
    reload_requested = Signal()
    close_tab_requested = Signal()
    closing = Signal()

    def __init__(self, theme: str) -> None:
        super().__init__()
        self._theme = theme
        self.setWindowTitle(config.APP_NAME)
        self.setMinimumSize(*config.WINDOW_MIN_SIZE)
        self.resize(*config.WINDOW_DEFAULT_SIZE)

        central = QWidget(self)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_topbar())
        root.addWidget(self._build_splitter(theme), 1)
        self.setCentralWidget(central)

        self._build_statusbar()
        self._toast_manager = ToastManager(self, theme)
        self._install_shortcuts()
        self.apply_theme(theme)

    # -- API publique --------------------------------------------------------

    def show_toast(self, toast_type: str, message: str, description: str | None = None) -> None:
        """Affiche un toast de notification."""
        self._toast_manager.show(toast_type, message, description)

    def set_status(self, message: str) -> None:
        """Met à jour le message d'état à gauche de la statusbar."""
        self._status_message.setText(message)

    def set_info(self, text: str) -> None:
        """Met à jour l'info contextuelle à droite de la statusbar."""
        self._status_info.setText(text)

    def set_file_label(self, text: str) -> None:
        """Met à jour le nom du fichier courant dans la topbar."""
        self._file_label.setText(text)

    def set_explorer_visible(self, visible: bool) -> None:
        """Affiche ou masque le volet explorateur."""
        self.explorer.setVisible(visible)

    def set_toc_visible(self, visible: bool) -> None:
        """Affiche ou masque le volet sommaire."""
        self.toc.setVisible(visible)

    def is_explorer_visible(self) -> bool:
        """Indique si le volet explorateur est visible."""
        return self.explorer.isVisible()

    def is_toc_visible(self) -> bool:
        """Indique si le volet sommaire est visible."""
        return self.toc.isVisible()

    def explorer_width(self) -> int:
        """Largeur courante du volet explorateur (0 s'il est masqué)."""
        return self._splitter.sizes()[0]

    def toc_width(self) -> int:
        """Largeur courante du volet sommaire (0 s'il est masqué)."""
        return self._splitter.sizes()[2]

    def set_panel_widths(self, explorer_width: int, toc_width: int) -> None:
        """Applique les largeurs des volets ; le document occupe l'espace restant."""
        total = self._splitter.width()
        document = max(0, total - explorer_width - toc_width)
        self._splitter.setSizes([explorer_width, document, toc_width])

    def apply_theme(self, theme: str) -> None:
        """Recolore les icônes et propage le thème aux sous-vues et aux toasts."""
        self._theme = theme
        for button, icon_name in self._icon_buttons:
            button.setIcon(get_icon(icon_name, "default", theme, config.ICON_LG))
        toggle_icon = "moon" if theme == "light" else "sun"
        self.theme_toggle.setIcon(get_icon(toggle_icon, "default", theme, config.ICON_LG))
        self.theme_toggle.setToolTip(
            "Passer en mode sombre" if theme == "light" else "Passer en mode clair"
        )
        self.explorer.apply_theme(theme)
        self.document.apply_theme(theme)
        self._toast_manager.set_theme(theme)

    # -- Construction interne ------------------------------------------------

    def _build_topbar(self) -> QFrame:
        topbar = QFrame(self)
        topbar.setObjectName("topbar")
        topbar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(8)

        logo = QLabel(topbar)
        logo.setObjectName("app_logo")
        icon_path = Path(resource_path("resources/icon.ico"))
        if icon_path.exists():
            logo.setPixmap(QIcon(str(icon_path)).pixmap(config.ICON_LG, config.ICON_LG))
        layout.addWidget(logo)

        title = QLabel(config.APP_NAME, topbar)
        title.setObjectName("app_title")
        layout.addWidget(title)

        self._file_label = QLabel("", topbar)
        self._file_label.setObjectName("file_label")
        layout.addWidget(self._file_label)

        layout.addStretch(1)

        self.btn_open_file = self._make_button(
            topbar, "btn_open_file", "Ouvrir un fichier (Ctrl+O)"
        )
        self.btn_open_folder = self._make_button(
            topbar, "btn_open_folder", "Ouvrir un dossier (Ctrl+Maj+O)"
        )
        self.btn_recents = self._make_button(topbar, "btn_recents", "Fichiers récents")
        self.btn_search = self._make_button(topbar, "btn_search", "Rechercher (Ctrl+F)")
        self.btn_zoom_out = self._make_button(topbar, "btn_zoom_out", "Zoom arrière (Ctrl+-)")
        self.btn_zoom_in = self._make_button(topbar, "btn_zoom_in", "Zoom avant (Ctrl++)")
        self.btn_toggle_explorer = self._make_button(
            topbar, "btn_toggle_explorer", "Afficher/masquer l'explorateur"
        )
        self.btn_toggle_toc = self._make_button(
            topbar, "btn_toggle_toc", "Afficher/masquer le sommaire"
        )
        self.theme_toggle = self._make_button(topbar, "theme_toggle", "")

        self._icon_buttons: list[tuple[QToolButton, str]] = [
            (self.btn_open_file, "file-text"),
            (self.btn_open_folder, "folder-open"),
            (self.btn_recents, "history"),
            (self.btn_search, "search"),
            (self.btn_zoom_out, "zoom-out"),
            (self.btn_zoom_in, "zoom-in"),
            (self.btn_toggle_explorer, "panel-left"),
            (self.btn_toggle_toc, "panel-right"),
        ]

        self.recents_menu = QMenu(self)
        self.btn_recents.setMenu(self.recents_menu)
        self.btn_recents.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        for button, _ in self._icon_buttons:
            layout.addWidget(button)
        layout.addWidget(self.theme_toggle)

        return topbar

    def _make_button(self, parent: QFrame, name: str, tooltip: str) -> QToolButton:
        button = QToolButton(parent)
        button.setObjectName(name)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setIconSize(QSize(config.ICON_LG, config.ICON_LG))
        if tooltip:
            button.setToolTip(tooltip)
        return button

    def _build_splitter(self, theme: str) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.setObjectName("main_splitter")
        splitter.setChildrenCollapsible(False)

        self.explorer = ExplorerView(theme)
        self.document = DocumentView(theme)
        self.toc = TocView()
        # Largeur mini < sizeHint du contenu, sinon QSplitter ne peut pas appliquer
        # les largeurs voulues/persistées (l'explorateur reste bloqué à son sizeHint).
        self.explorer.setMinimumWidth(config.PANEL_MIN_WIDTH)
        self.toc.setMinimumWidth(config.PANEL_MIN_WIDTH)
        splitter.addWidget(self.explorer)
        splitter.addWidget(self.document)
        splitter.addWidget(self.toc)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([config.EXPLORER_WIDTH, config.WINDOW_DEFAULT_SIZE[0], config.TOC_WIDTH])
        self._splitter = splitter
        return splitter

    def _build_statusbar(self) -> None:
        status = self.statusBar()
        self._status_message = QLabel("Prêt", status)
        self._status_message.setObjectName("status_message")
        status.addWidget(self._status_message)
        self._status_info = QLabel("", status)
        self._status_info.setObjectName("status_info")
        status.addPermanentWidget(self._status_info)

    def _install_shortcuts(self) -> None:
        bindings: list[tuple[str, Callable[..., object]]] = [
            ("Ctrl+O", self.btn_open_file.click),
            ("Ctrl+Shift+O", self.btn_open_folder.click),
            ("Ctrl+F", self.btn_search.click),
            ("Ctrl++", self.btn_zoom_in.click),
            ("Ctrl+=", self.btn_zoom_in.click),
            ("Ctrl+-", self.btn_zoom_out.click),
            ("Ctrl+0", self.zoom_reset_requested.emit),
            ("Ctrl+W", self.close_tab_requested.emit),
            ("F5", self.reload_requested.emit),
        ]
        for sequence, slot in bindings:
            shortcut = QShortcut(QKeySequence(sequence), self)
            shortcut.activated.connect(slot)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Repositionne les toasts lors du redimensionnement."""
        super().resizeEvent(event)
        self._toast_manager.reposition()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Émet `closing` pendant que la fenêtre est encore visible (sauvegarde d'état).

        Sur `app.aboutToQuit`, la fenêtre est déjà masquée et `isVisible()` renvoie
        False pour les volets, ce qui corromprait l'état persisté (voir contrôleur).
        """
        self.closing.emit()
        super().closeEvent(event)

    def center_on_screen(self) -> None:
        """Centre la fenêtre sur l'écran principal."""
        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            geometry = screen.availableGeometry()
            self.move(
                geometry.center().x() - self.width() // 2,
                geometry.center().y() - self.height() // 2,
            )
