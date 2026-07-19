"""Volet document — zone à onglets (une vue web par document) + barre de recherche.

PySide6 uniquement. Chaque document ouvert possède sa propre `QWebEngineView` dans un
`QTabWidget` ; une vue d'accueil dédiée occupe l'état vide (aucun onglet). Les clics de
liens sont interceptés (→ signal, ouverture externe côté contrôleur) : aucune navigation
interne. Le style/couleur du contenu est porté par le HTML/CSS injecté, pas par le QSS.
"""

import json
from collections.abc import Callable

from PySide6.QtCore import QSize, Qt, QUrl, Signal
from PySide6.QtGui import QColor, QKeySequence, QShortcut
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QStackedWidget,
    QTabBar,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

import config
from utils.icons import get_icon

_DOC_PATH_PROPERTY = "doc_path"


class _NavigationPage(QWebEnginePage):
    """Page web qui redirige les clics de liens vers un signal (aucune navigation interne)."""

    external_link = Signal(QUrl)

    def acceptNavigationRequest(  # noqa: N802
        self,
        url: QUrl | str,
        type: QWebEnginePage.NavigationType,  # noqa: A002
        isMainFrame: bool,  # noqa: N803
    ) -> bool:
        """Bloque les clics de liens et les émet ; laisse passer le chargement initial."""
        if type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            self.external_link.emit(QUrl(url))
            return False
        return super().acceptNavigationRequest(url, type, isMainFrame)


class DocumentView(QFrame):
    """Panneau central : onglets de documents + vue d'accueil + barre de recherche."""

    external_link_clicked = Signal(QUrl)
    load_finished = Signal(bool)
    tab_activated = Signal(str)  # chemin du document actif ("" = accueil)
    tab_closed = Signal(str)  # chemin du document fermé

    def __init__(self, theme: str, parent: QFrame | None = None) -> None:
        super().__init__(parent)
        self._theme = theme
        self._zoom = config.ZOOM_DEFAULT
        self.setObjectName("document_panel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._find_bar = self._build_find_bar()
        self._find_bar.hide()
        layout.addWidget(self._find_bar)

        # Page 0 : accueil (état vide) ; page 1 : onglets de documents.
        self._stack = QStackedWidget(self)
        layout.addWidget(self._stack, 1)

        self._welcome_view = self._make_web_view()
        self._stack.addWidget(self._welcome_view)

        self._tabs = QTabWidget(self)
        self._tabs.setObjectName("doc_tab_widget")
        self._tabs.setDocumentMode(True)
        self._tabs.setMovable(False)
        self._tabs.setTabsClosable(False)  # croix personnalisée thématisée via setTabButton
        self._tabs.currentChanged.connect(self._on_current_changed)
        self._stack.addWidget(self._tabs)

        escape = QShortcut(QKeySequence(Qt.Key.Key_Escape), self._find_input)
        escape.activated.connect(self.hide_find_bar)

        self.apply_theme(theme)

    # -- API publique : onglets ----------------------------------------------

    def open_document(self, path: str, title: str, html: str, base_url: QUrl) -> None:
        """Ouvre `path` dans un nouvel onglet, ou l'active s'il est déjà ouvert."""
        if self.has_document(path):
            self.activate_document(path)
            return
        view = self._make_web_view()
        view.setProperty(_DOC_PATH_PROPERTY, path)
        view.setZoomFactor(self._zoom)
        view.setHtml(html, base_url)
        index = self._tabs.addTab(view, title)
        self._tabs.setTabToolTip(index, path)
        self._tabs.tabBar().setTabButton(
            index, QTabBar.ButtonPosition.RightSide, self._make_close_button(path)
        )
        self._stack.setCurrentWidget(self._tabs)
        self._tabs.setCurrentIndex(index)  # → _on_current_changed → tab_activated

    def activate_document(self, path: str) -> None:
        """Active l'onglet du document `path` (met à jour les surfaces via tab_activated)."""
        index = self._index_of(path)
        if index < 0:
            return
        self._stack.setCurrentWidget(self._tabs)
        if self._tabs.currentIndex() == index:
            self.tab_activated.emit(path)  # déjà courant : forcer le rafraîchissement
        else:
            self._tabs.setCurrentIndex(index)

    def update_document(self, path: str, html: str, base_url: QUrl) -> None:
        """Recharge le HTML d'un onglet existant (re-rendu au changement de thème)."""
        view = self._view_of(path)
        if view is not None:
            view.setHtml(html, base_url)

    def close_document(self, path: str) -> None:
        """Ferme l'onglet du document `path`. Le dernier onglet fermé revient à l'accueil."""
        index = self._index_of(path)
        if index < 0:
            return
        self.tab_closed.emit(path)
        view = self._tabs.widget(index)
        self._tabs.removeTab(index)
        if view is not None:
            view.deleteLater()
        if self._tabs.count() == 0:
            self._stack.setCurrentWidget(self._welcome_view)
            self.tab_activated.emit("")

    def set_welcome(self, html: str) -> None:
        """Charge le HTML de la page d'accueil (état vide)."""
        self._welcome_view.setHtml(html, QUrl())

    def has_document(self, path: str) -> bool:
        """Indique si un onglet est déjà ouvert pour `path`."""
        return self._index_of(path) >= 0

    def open_paths(self) -> list[str]:
        """Renvoie les chemins des documents ouverts, dans l'ordre des onglets."""
        return [self._path_at(i) for i in range(self._tabs.count())]

    def current_document_path(self) -> str | None:
        """Renvoie le chemin du document actif, ou None si l'accueil est affiché."""
        if self._stack.currentWidget() is self._tabs and self._tabs.count() > 0:
            return self._path_at(self._tabs.currentIndex())
        return None

    # -- API publique : contenu / recherche ----------------------------------

    def set_zoom(self, factor: float) -> None:
        """Applique le facteur de zoom à toutes les vues (zoom global)."""
        self._zoom = factor
        self._welcome_view.setZoomFactor(factor)
        for view in self._all_tab_views():
            view.setZoomFactor(factor)

    def toggle_find_bar(self) -> None:
        """Affiche/masque la barre de recherche."""
        if self._find_bar.isVisible():
            self.hide_find_bar()
        else:
            self.show_find_bar()

    def show_find_bar(self) -> None:
        """Affiche la barre de recherche et donne le focus au champ."""
        self._find_bar.show()
        self._find_input.setFocus()
        self._find_input.selectAll()

    def hide_find_bar(self) -> None:
        """Masque la barre, efface la surbrillance et rend le focus à la vue active."""
        self._find_bar.hide()
        active = self._active_view()
        active.findText("")
        active.setFocus()

    def scroll_to_anchor(self, anchor: str) -> None:
        """Défile le document actif vers l'élément d'ancre donné."""
        target = json.dumps(anchor)
        self._active_view().page().runJavaScript(
            f"var el=document.getElementById({target});"
            f"if(el){{el.scrollIntoView({{behavior:'smooth',block:'start'}});}}"
        )

    def apply_theme(self, theme: str) -> None:
        """Recolore les icônes (recherche + croix d'onglets) et le fond des vues web."""
        self._theme = theme
        self._btn_find_prev.setIcon(get_icon("chevron-up", "default", theme, config.ICON_SM))
        self._btn_find_next.setIcon(get_icon("chevron-down", "default", theme, config.ICON_SM))
        self._btn_find_close.setIcon(get_icon("x", "muted", theme, config.ICON_SM))

        color = self._background_color()
        self._welcome_view.page().setBackgroundColor(color)
        for view in self._all_tab_views():
            view.page().setBackgroundColor(color)

        close_icon = get_icon("x", "muted", theme, config.ICON_MD)
        for i in range(self._tabs.count()):
            holder = self._tabs.tabBar().tabButton(i, QTabBar.ButtonPosition.RightSide)
            inner = holder.findChild(QToolButton) if holder is not None else None
            if isinstance(inner, QToolButton):
                inner.setIcon(close_icon)

    # -- Construction interne ------------------------------------------------

    def _make_web_view(self) -> QWebEngineView:
        """Crée une QWebEngineView (page de navigation, fond thème, signaux reliés)."""
        view = QWebEngineView(self)
        page = _NavigationPage(view)
        view.setPage(page)
        page.external_link.connect(self.external_link_clicked)
        view.loadFinished.connect(self.load_finished)
        settings = view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, False)
        page.setBackgroundColor(self._background_color())
        return view

    def _make_close_button(self, path: str) -> QWidget:
        """Croix de fermeture d'un onglet, dans un conteneur avec marge droite.

        QTabBar place le bouton latéral au ras du bord et le dimensionne depuis son
        sizeHint (un min/max QSS n'est pas honoré ici). On fixe la taille du bouton
        (carré compact centré) et on l'enveloppe dans un conteneur dont la marge droite
        décale la croix du bord de l'onglet — hover propre et détaché de la ligne.
        """
        button = QToolButton(self)
        button.setObjectName("tab_close")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setIconSize(QSize(config.ICON_MD, config.ICON_MD))
        button.setFixedSize(QSize(config.ICON_LG, config.ICON_LG))
        button.setIcon(get_icon("x", "muted", self._theme, config.ICON_MD))
        button.setToolTip("Fermer l'onglet")
        button.clicked.connect(lambda: self.close_document(path))

        holder = QWidget(self)
        holder.setObjectName("tab_close_holder")
        holder_layout = QHBoxLayout(holder)
        holder_layout.setContentsMargins(0, 0, 8, 0)  # marge droite = écart au bord de l'onglet
        holder_layout.setSpacing(0)
        holder_layout.addWidget(button)
        return holder

    def _build_find_bar(self) -> QFrame:
        bar = QFrame(self)
        bar.setObjectName("find_bar")
        bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(12, 6, 12, 6)
        bar_layout.setSpacing(6)

        self._find_input = QLineEdit(bar)
        self._find_input.setObjectName("find_input")
        self._find_input.setPlaceholderText("Rechercher dans le document…")
        self._find_input.textChanged.connect(self._on_text_changed)
        self._find_input.returnPressed.connect(self._find_next)
        bar_layout.addWidget(self._find_input, 1)

        self._btn_find_prev = self._make_button(bar, "find_prev", "Précédent", self._find_previous)
        self._btn_find_next = self._make_button(bar, "find_next", "Suivant", self._find_next)
        self._btn_find_close = self._make_button(bar, "find_close", "Fermer", self.hide_find_bar)
        bar_layout.addWidget(self._btn_find_prev)
        bar_layout.addWidget(self._btn_find_next)
        bar_layout.addWidget(self._btn_find_close)

        return bar

    @staticmethod
    def _make_button(
        parent: QFrame, name: str, tooltip: str, slot: Callable[..., object]
    ) -> QToolButton:
        button = QToolButton(parent)
        button.setObjectName(name)
        button.setToolTip(tooltip)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setIconSize(QSize(config.ICON_SM, config.ICON_SM))
        button.clicked.connect(slot)
        return button

    # -- Helpers internes ----------------------------------------------------

    def _background_color(self) -> QColor:
        """Neutre `bg` du thème (fond des vues web, surface peinte non stylable QSS)."""
        bg = config.SPLASH_COLORS.get(self._theme, config.SPLASH_COLORS["light"])["bg"]
        return QColor(bg)

    def _active_view(self) -> QWebEngineView:
        """Vue web active : onglet courant si affiché, sinon l'accueil."""
        if self._stack.currentWidget() is self._tabs and self._tabs.count() > 0:
            widget = self._tabs.currentWidget()
            if isinstance(widget, QWebEngineView):
                return widget
        return self._welcome_view

    def _all_tab_views(self) -> list[QWebEngineView]:
        views: list[QWebEngineView] = []
        for i in range(self._tabs.count()):
            widget = self._tabs.widget(i)
            if isinstance(widget, QWebEngineView):
                views.append(widget)
        return views

    def _path_at(self, index: int) -> str:
        widget = self._tabs.widget(index)
        value = widget.property(_DOC_PATH_PROPERTY) if widget is not None else None
        return str(value) if value else ""

    def _index_of(self, path: str) -> int:
        for i in range(self._tabs.count()):
            if self._path_at(i) == path:
                return i
        return -1

    def _view_of(self, path: str) -> QWebEngineView | None:
        index = self._index_of(path)
        if index < 0:
            return None
        widget = self._tabs.widget(index)
        return widget if isinstance(widget, QWebEngineView) else None

    def _on_current_changed(self, index: int) -> None:
        """Émet le chemin de l'onglet devenu actif (index < 0 géré par close_document)."""
        if index < 0:
            return
        self.tab_activated.emit(self._path_at(index))

    def _on_text_changed(self, text: str) -> None:
        self._active_view().findText(text)

    def _find_next(self) -> None:
        self._active_view().findText(self._find_input.text())

    def _find_previous(self) -> None:
        self._active_view().findText(self._find_input.text(), QWebEnginePage.FindFlag.FindBackward)
