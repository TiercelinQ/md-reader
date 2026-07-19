"""Rendu des icônes Lucide en QIcon thématisés.

Les SVG Lucide utilisent `stroke="currentColor"` (que QIcon ne résout pas). On lit le
SVG, on substitue la couleur (config.ICON_COLORS) et l'épaisseur de trait (ICON_STROKE),
puis on rend via QSvgRenderer. Les couleurs d'icônes sont l'exception documentée au
principe « toutes les valeurs visuelles en QSS » (design-system §10).
"""

import logging
import re
from functools import cache

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

import config
from utils.resource_path import resource_path

logger = logging.getLogger(__name__)

_STROKE_RE = re.compile(r'stroke-width="[^"]*"')


@cache
def _svg_source(name: str) -> str:
    """Lit et met en cache le texte SVG d'une icône (chaîne vide si absente)."""
    from pathlib import Path

    path = Path(resource_path(f"resources/icons/{name}.svg"))
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        logger.warning("Icône introuvable : %s", name)
        return ""


@cache
def get_icon(name: str, color_key: str, theme: str, size: int) -> QIcon:
    """Renvoie l'icône `name` recolorée pour `color_key`/`theme`, rendue à `size` px."""
    source = _svg_source(name)
    if not source:
        return QIcon()

    color = config.ICON_COLORS.get(theme, config.ICON_COLORS["light"]).get(color_key, "#000000")
    svg = source.replace("currentColor", color)
    svg = _STROKE_RE.sub(f'stroke-width="{config.ICON_STROKE}"', svg)

    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    try:
        renderer.render(painter, QRectF(0, 0, size, size))
    finally:
        painter.end()
    return QIcon(pixmap)
