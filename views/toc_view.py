"""Volet sommaire — arborescence cliquable des titres du document courant.

PySide6 uniquement. Le contrôleur fournit la structure via `TocNode` (DTO possédé
par la vue) ; le clic émet l'ancre du titre visé.
"""

from dataclasses import dataclass

from PySide6.QtCore import QModelIndex, Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QFrame, QLabel, QTreeView, QVBoxLayout

_ANCHOR_ROLE = Qt.ItemDataRole.UserRole


@dataclass(frozen=True)
class TocNode:
    """Un titre du sommaire (texte, ancre HTML) et ses sous-titres."""

    text: str
    anchor: str
    children: list["TocNode"]


class TocView(QFrame):
    """Panneau droit : titres du document, clic → défilement vers l'ancre."""

    heading_selected = Signal(str)

    def __init__(self, parent: QFrame | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("toc_panel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel("Sommaire", self)
        header.setObjectName("toc_header")
        header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout.addWidget(header)

        self._model = QStandardItemModel(self)
        self._tree = QTreeView(self)
        self._tree.setObjectName("toc_tree")
        self._tree.setModel(self._model)
        self._tree.setHeaderHidden(True)
        self._tree.clicked.connect(self._on_clicked)
        self._tree.hide()
        layout.addWidget(self._tree, 1)

        self._empty_label = QLabel("Aucun titre", self)
        self._empty_label.setObjectName("toc_empty")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._empty_label, 1)

    def set_toc(self, nodes: list[TocNode]) -> None:
        """Remplace le sommaire par la structure fournie."""
        self._model.clear()
        for node in nodes:
            self._model.appendRow(self._build_item(node))
        has_content = bool(nodes)
        self._tree.setVisible(has_content)
        self._empty_label.setVisible(not has_content)
        if has_content:
            self._tree.expandAll()

    def _build_item(self, node: TocNode) -> QStandardItem:
        """Construit un QStandardItem (avec son ancre) et ses enfants récursivement."""
        item = QStandardItem(node.text)
        item.setEditable(False)
        item.setData(node.anchor, _ANCHOR_ROLE)
        for child in node.children:
            item.appendRow(self._build_item(child))
        return item

    def _on_clicked(self, index: QModelIndex) -> None:
        """Émet l'ancre du titre cliqué."""
        anchor = self._model.data(index, _ANCHOR_ROLE)
        if isinstance(anchor, str) and anchor:
            self.heading_selected.emit(anchor)
