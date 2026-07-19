"""Fixtures partagées pour la suite de tests.

qapp est fournie automatiquement par pytest-qt — ne pas redéfinir.
"""

from pathlib import Path

import pytest

_SAMPLE = (
    "# Titre\n\n"
    "Un paragraphe avec du **gras** et un [lien](https://example.com).\n\n"
    "## Sous-titre\n\n"
    "- item 1\n- item 2\n\n"
    "```python\nprint('bonjour')\n```\n\n"
    "```mermaid\ngraph TD; A-->B;\n```\n"
)


@pytest.fixture
def temp_preferences(tmp_path, monkeypatch):
    """Redirige le fichier de préférences vers un fichier temporaire isolé."""
    from utils import helpers

    pref = tmp_path / "preferences.json"
    monkeypatch.setattr(helpers, "_preferences_path", lambda: pref)
    return pref


@pytest.fixture
def sample_markdown(tmp_path) -> Path:
    """Écrit un document Markdown d'exemple (titres, code, mermaid) et renvoie son chemin."""
    path = tmp_path / "doc.md"
    path.write_text(_SAMPLE, encoding="utf-8")
    return path
