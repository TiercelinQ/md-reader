"""Volet document — vue web du rendu Markdown + barre de recherche incrustée.

PySide6 uniquement. Intercepte les clics de liens (→ signal, ouverture externe côté
contrôleur) et n'effectue aucune navigation interne. La coloration/le style du contenu
sont portés par le HTML/CSS injecté, pas par le QSS.
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
    QToolButton,
    QVBoxLayout,
)

import config
from utils.icons import get_icon


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
    """Panneau central : QWebEngineView + barre de recherche (#find_bar)."""

    external_link_clicked = Signal(QUrl)
    load_finished = Signal(bool)

    def __init__(self, theme: str, parent: QFrame | None = None) -> None:
        super().__init__(parent)
        self._theme = theme
        self.setObjectName("document_panel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._find_bar = self._build_find_bar()
        self._find_bar.hide()
        layout.addWidget(self._find_bar)

        self._web_view = QWebEngineView(self)
        self._page = _NavigationPage(self._web_view)
        self._web_view.setPage(self._page)
        self._page.external_link.connect(self.external_link_clicked)
        self._web_view.loadFinished.connect(self.load_finished)
        settings = self._web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, False)
        layout.addWidget(self._web_view, 1)

        escape = QShortcut(QKeySequence(Qt.Key.Key_Escape), self._find_input)
        escape.activated.connect(self.hide_find_bar)

        self.apply_theme(theme)

    # -- API publique --------------------------------------------------------

    def set_html(self, html: str, base_url: QUrl) -> None:
        """Charge le HTML rendu, `base_url` servant à résoudre les images relatives."""
        self._web_view.setHtml(html, base_url)

    def set_zoom(self, factor: float) -> None:
        """Applique le facteur de zoom au contenu."""
        self._web_view.setZoomFactor(factor)

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
        """Masque la barre, efface la surbrillance et rend le focus à la vue."""
        self._find_bar.hide()
        self._web_view.findText("")
        self._web_view.setFocus()

    def scroll_to_anchor(self, anchor: str) -> None:
        """Défile le document vers l'élément d'ancre donné."""
        target = json.dumps(anchor)
        self._web_view.page().runJavaScript(
            f"var el=document.getElementById({target});"
            f"if(el){{el.scrollIntoView({{behavior:'smooth',block:'start'}});}}"
        )

    def apply_theme(self, theme: str) -> None:
        """Recolore les icônes de la barre de recherche et aligne le fond de la vue web."""
        self._theme = theme
        self._btn_find_prev.setIcon(get_icon("chevron-up", "default", theme, config.ICON_SM))
        self._btn_find_next.setIcon(get_icon("chevron-down", "default", theme, config.ICON_SM))
        self._btn_find_close.setIcon(get_icon("x", "muted", theme, config.ICON_SM))
        self._apply_web_background(theme)

    def _apply_web_background(self, theme: str) -> None:
        """Aligne le fond de la vue web sur le neutre `bg` du thème.

        La surface peinte par Chromium n'est pas stylable via QSS ; sans cet
        alignement, les zones exposées pendant un redimensionnement affichent un
        fond blanc ou des pixels périmés (clignotement). La valeur `bg` par thème
        est réutilisée depuis `config.SPLASH_COLORS` (même neutre, surface peinte).
        """
        bg = config.SPLASH_COLORS.get(theme, config.SPLASH_COLORS["light"])["bg"]
        self._page.setBackgroundColor(QColor(bg))

    # -- Construction interne ------------------------------------------------

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

    def _on_text_changed(self, text: str) -> None:
        self._web_view.findText(text)

    def _find_next(self) -> None:
        self._web_view.findText(self._find_input.text())

    def _find_previous(self) -> None:
        self._web_view.findText(self._find_input.text(), QWebEnginePage.FindFlag.FindBackward)
