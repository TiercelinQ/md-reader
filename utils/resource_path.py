"""Résolution des chemins de ressources et du dossier de données inscriptible.

En mode packagé (PyInstaller), les ressources vivent dans `sys._MEIPASS` et les
données inscriptibles (préférences, logs) dans `%APPDATA%/MD Reader`. En développement,
tout est relatif à la racine du projet.
"""

import os
import sys
from pathlib import Path

import config

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def resource_path(relative: str) -> str:
    """Résout le chemin d'une ressource embarquée (lecture seule)."""
    base = getattr(sys, "_MEIPASS", None)
    root = Path(base) if base else _PROJECT_ROOT
    return str(root / relative)


def user_data_dir() -> Path:
    """Dossier inscriptible pour préférences et logs (APPDATA si packagé)."""
    if getattr(sys, "frozen", False):
        base = os.environ.get("APPDATA") or str(Path.home())
        return Path(base) / config.APP_NAME
    return _PROJECT_ROOT
