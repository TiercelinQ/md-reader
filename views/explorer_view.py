"""Volet explorateur — arborescence des fichiers Markdown d'un dossier.

PySide6 uniquement, aucune logique métier : émet des signaux, expose des méthodes.
"""

from pathlib import Path

from PySide6.QtCore import QModelIndex, QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFileSystemModel,
    QFrame,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QTreeView,
    QVBoxLayout,
)

import config
from utils.icons import get_icon


class ExplorerView(QFrame):
    """Panneau gauche : en-tête (dossier + rafraîchir) + QTreeView filtré *.md."""

    file_selected = Signal(str)
    refresh_requested = Signal()

    def __init__(self, theme: str, parent: QFrame | None = None) -> None:
        super().__init__(parent)
        self._theme = theme
        self.setObjectName("explorer_panel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame(self)
        header.setObjectName("explorer_header")
        header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 8, 8)
        self._header_label = QLabel("Aucun dossier ouvert", header)
        self._header_label.setObjectName("explorer_header_label")
        header_layout.addWidget(self._header_label, 1)
        self._refresh_button = QToolButton(header)
        self._refresh_button.setObjectName("btn_refresh")
        self._refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh_button.setToolTip("Rafraîchir")
        self._refresh_button.setIconSize(QSize(config.ICON_MD, config.ICON_MD))
        self._refresh_button.setEnabled(False)
        self._refresh_button.clicked.connect(self.refresh_requested)
        header_layout.addWidget(self._refresh_button)
        layout.addWidget(header)

        self._model = QFileSystemModel(self)
        self._model.setNameFilters([f"*{s}" for s in config.MARKDOWN_SUFFIXES])
        self._model.setNameFilterDisables(False)

        self._tree = QTreeView(self)
        self._tree.setObjectName("explorer_tree")
        self._tree.setModel(self._model)
        self._tree.setHeaderHidden(True)
        for column in range(1, self._model.columnCount()):
            self._tree.setColumnHidden(column, True)
        self._tree.clicked.connect(self._on_clicked)
        self._tree.hide()
        layout.addWidget(self._tree, 1)

        self._empty_label = QLabel("Ouvrez un dossier pour parcourir vos fichiers .md", self)
        self._empty_label.setObjectName("explorer_empty")
        self._empty_label.setWordWrap(True)
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._empty_label, 1)

        self.apply_theme(theme)

    def set_root_path(self, path: str) -> None:
        """Charge un dossier dans l'arborescence et affiche le nom du dossier."""
        self._model.setRootPath(path)
        self._tree.setRootIndex(self._model.index(path))
        self._header_label.setText(Path(path).name or path)
        self._refresh_button.setEnabled(True)
        self._empty_label.hide()
        self._tree.show()

    def apply_theme(self, theme: str) -> None:
        """Recolore les icônes selon le thème."""
        self._theme = theme
        self._refresh_button.setIcon(get_icon("refresh-cw", "default", theme, config.ICON_MD))

    def _on_clicked(self, index: QModelIndex) -> None:
        """Émet le chemin du fichier cliqué (ignore les dossiers)."""
        if self._model.isDir(index):
            return
        self.file_selected.emit(self._model.filePath(index))
