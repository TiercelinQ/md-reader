"""Exceptions métier nommées — levées par les modèles, interceptées par les contrôleurs."""


class FileError(Exception):
    """Erreur de lecture/accès à un fichier (introuvable, illisible, type non pris en charge)."""


class RenderError(Exception):
    """Erreur lors de la conversion Markdown → HTML."""
