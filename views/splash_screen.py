"""Écran de démarrage — fenêtre de lancement affichée jusqu'à ce que la fenêtre soit prête.

Splash « icône seule » : le pixmap est l'icône `resources/icon.ico` elle-même (son alpha
transparent), avec `WA_TranslucentBackground` — donc aucun rectangle de fond ni nom d'appli.
L'icône est rendue via `QIcon.pixmap` (et non `QPixmap` mis à l'échelle) pour rester nette,
et redimensionnée selon le `devicePixelRatio` pour le HiDPI. En l'absence d'icône, repli
texte peint avec `config.SPLASH_COLORS` (exception documentée, comme ICON_COLORS).
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QGuiApplication, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QSplashScreen

import config
from utils.resource_path import resource_path

_FALLBACK_SIZE = (420, 260)
_ICON_PX = 128


def create_splash(theme: str) -> QSplashScreen:
    """Construit le splash pour le thème donné ("light"/"dark").

    Affiche uniquement l'icône `resources/icon.ico` (fond translucide, sans rectangle
    ni nom d'application). Si aucune icône n'existe, replie sur le nom de l'application
    peint avec `config.SPLASH_COLORS`.
    """
    icon_path = Path(resource_path("resources/icon.ico"))
    if icon_path.exists():
        dpr = QGuiApplication.primaryScreen().devicePixelRatio()
        size = round(_ICON_PX * dpr)
        icon_pix = QIcon(str(icon_path)).pixmap(size, size)
        if not icon_pix.isNull():
            icon_pix.setDevicePixelRatio(dpr)
            splash = QSplashScreen(icon_pix)
            splash.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            return splash

    colors = config.SPLASH_COLORS.get(theme, config.SPLASH_COLORS["light"])
    pixmap = QPixmap(*_FALLBACK_SIZE)
    pixmap.fill(QColor(colors["bg"]))
    painter = QPainter(pixmap)
    try:
        painter.setPen(QColor(colors["text"]))
        painter.setFont(QFont("", 20, QFont.Weight.Medium))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, config.APP_NAME)
    finally:
        painter.end()

    return QSplashScreen(pixmap)
