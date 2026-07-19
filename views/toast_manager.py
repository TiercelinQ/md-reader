"""Système de toasts — notifications superposées, ancrées en haut à droite.

Aucune animation (motion policy design-system §6). Durées : success/info 4s,
warning 6s (fermable), danger persistant (fermable, obligatoire). Les couleurs et
polices viennent des feuilles QSS (objectName `toast_*`) ; les icônes de config.ICON_COLORS.
"""

from collections.abc import Callable

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QVBoxLayout, QWidget

import config
from utils.icons import get_icon


def _noop() -> None:
    """Callback de fermeture par défaut (aucun effet)."""


# Géométrie de superposition (non exprimable en QSS — couche peinte par-dessus le contenu).
_WIDTH = 320  # token : toast width (layout.md §5)
_MARGIN = 16  # token : spacing-4
_GAP = 8  # token : spacing-2
_TOP_OFFSET = 64  # topbar-height (48) + spacing-4 (16)

_DURATIONS_MS = {"success": 4000, "info": 4000, "warning": 6000, "danger": 0}
_CLOSABLE = {"warning", "danger"}
_ICONS = {
    "success": "circle-check",
    "warning": "triangle-alert",
    "danger": "circle-x",
    "info": "info",
}


class _Toast(QFrame):
    """Un toast : icône + message (+ description) (+ bouton fermer)."""

    def __init__(self, toast_type: str, message: str, description: str | None, theme: str) -> None:
        super().__init__()
        self.setObjectName(f"toast_{toast_type}")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(_WIDTH)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 12, 12)
        layout.setSpacing(12)

        icon_label = QLabel(self)
        icon_label.setObjectName("toast_icon")
        icon_label.setPixmap(
            get_icon(_ICONS[toast_type], toast_type, theme, config.ICON_MD).pixmap(
                config.ICON_MD, config.ICON_MD
            )
        )
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(icon_label)

        text_box = QVBoxLayout()
        text_box.setContentsMargins(0, 0, 0, 0)
        text_box.setSpacing(2)
        message_label = QLabel(message, self)
        message_label.setObjectName("toast_message")
        message_label.setWordWrap(True)
        text_box.addWidget(message_label)
        if description:
            description_label = QLabel(description, self)
            description_label.setObjectName("toast_description")
            description_label.setWordWrap(True)
            text_box.addWidget(description_label)
        layout.addLayout(text_box, 1)

        if toast_type in _CLOSABLE:
            close_button = QToolButton(self)
            close_button.setObjectName("toast_close")
            close_button.setCursor(Qt.CursorShape.PointingHandCursor)
            close_button.setIcon(get_icon("x", "muted", theme, config.ICON_SM))
            close_button.setIconSize(QSize(config.ICON_SM, config.ICON_SM))
            close_button.clicked.connect(self._request_close)
            layout.addWidget(close_button, 0, Qt.AlignmentFlag.AlignTop)

        self._on_close: Callable[[], object] = _noop

    def bind_close(self, callback: Callable[[], object]) -> None:
        """Enregistre le callback appelé quand l'utilisateur ferme le toast."""
        self._on_close = callback

    def _request_close(self) -> None:
        self._on_close()


class ToastManager:
    """Crée, empile et retire les toasts par-dessus la fenêtre hôte."""

    def __init__(self, host: QWidget, theme: str) -> None:
        self._host = host
        self._theme = theme
        self._toasts: list[_Toast] = []

    def set_theme(self, theme: str) -> None:
        """Met à jour le thème utilisé pour les futurs toasts."""
        self._theme = theme

    def show(self, toast_type: str, message: str, description: str | None = None) -> None:
        """Affiche un toast (type = success|info|warning|danger)."""
        if toast_type not in _DURATIONS_MS:
            toast_type = "info"
        toast = _Toast(toast_type, message, description, self._theme)
        toast.setParent(self._host)
        toast.bind_close(lambda: self._dismiss(toast))
        self._toasts.append(toast)
        toast.show()
        toast.raise_()
        self._reposition()

        duration = _DURATIONS_MS[toast_type]
        if duration:
            QTimer.singleShot(duration, lambda: self._dismiss(toast))

    def reposition(self) -> None:
        """Repositionne la pile (appelé au redimensionnement de la fenêtre)."""
        self._reposition()

    def _dismiss(self, toast: _Toast) -> None:
        if toast not in self._toasts:
            return
        self._toasts.remove(toast)
        toast.deleteLater()
        self._reposition()

    def _reposition(self) -> None:
        x = self._host.width() - _WIDTH - _MARGIN
        y = _TOP_OFFSET
        for toast in self._toasts:
            toast.adjustSize()
            toast.move(x, y)
            toast.raise_()
            y += toast.height() + _GAP
