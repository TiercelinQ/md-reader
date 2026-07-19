"""Modèle des fichiers récents — liste persistée dans preferences.json.

Ordre du plus récent au plus ancien, dédupliqué, plafonné à `config.RECENT_MAX`.
Les chemins disparus du disque sont filtrés à la lecture. Zéro PySide6.
"""

import logging
from pathlib import Path

import config
from utils import helpers

logger = logging.getLogger(__name__)

_PREF_KEY = "recent_files"


class RecentFilesModel:
    """Gère la liste des fichiers récemment ouverts."""

    def __init__(self) -> None:
        raw = helpers.get_preference(_PREF_KEY, [])
        self._items: list[str] = [str(p) for p in raw if isinstance(p, str)]

    def add(self, path: str) -> None:
        """Ajoute (ou remonte) un chemin en tête de liste, puis persiste."""
        resolved = str(Path(path).resolve())
        self._items = [p for p in self._items if p != resolved]
        self._items.insert(0, resolved)
        del self._items[config.RECENT_MAX :]
        self._save()

    def get_all(self) -> list[str]:
        """Renvoie les récents existants encore présents sur le disque (persiste si purge)."""
        existing = [p for p in self._items if Path(p).is_file()]
        if existing != self._items:
            self._items = existing
            self._save()
        return list(self._items)

    def clear(self) -> None:
        """Vide la liste des récents et persiste."""
        self._items = []
        self._save()

    def _save(self) -> None:
        """Écrit la liste courante dans les préférences."""
        helpers.set_preference(_PREF_KEY, self._items)
