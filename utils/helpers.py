"""Fonctions pures — préférences JSON, validation de chemin, lecture des feuilles QSS.

Zéro PySide6, zéro logique métier.
"""

import json
import logging
from pathlib import Path
from typing import Any

import config
from utils.resource_path import resource_path, user_data_dir

logger = logging.getLogger(__name__)


def _preferences_path() -> Path:
    """Chemin du fichier de préférences (racine projet en dev, APPDATA si packagé)."""
    return user_data_dir() / config.PREFERENCES_FILE


def load_preferences() -> dict[str, Any]:
    """Charge les préférences ; renvoie un dict vide si absent ou illisible."""
    path = _preferences_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        logger.exception("Préférences illisibles : %s", path)
        return {}
    return data if isinstance(data, dict) else {}


def save_preferences(data: dict[str, Any]) -> None:
    """Écrit les préférences sur le disque (création du dossier au besoin)."""
    path = _preferences_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        logger.exception("Écriture des préférences impossible : %s", path)


def get_preference(key: str, default: Any = None) -> Any:
    """Renvoie la valeur d'une préférence, ou `default`."""
    return load_preferences().get(key, default)


def set_preference(key: str, value: Any) -> None:
    """Met à jour une préférence (lecture-modification-écriture)."""
    data = load_preferences()
    data[key] = value
    save_preferences(data)


def is_markdown_file(path: str) -> bool:
    """Vrai si le chemin désigne un fichier Markdown pris en charge."""
    p = Path(path)
    return p.is_file() and p.suffix.lower() in config.MARKDOWN_SUFFIXES


def read_stylesheet(theme: str) -> str:
    """Lit la feuille QSS du thème ("light"/"dark") ; chaîne vide si absente."""
    name = "dark" if theme == "dark" else "light"
    path = Path(resource_path(f"resources/styles_{name}.qss"))
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        logger.warning("Feuille QSS introuvable : %s", path)
        return ""
