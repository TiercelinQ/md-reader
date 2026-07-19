"""Tests du modèle de document (conversion Markdown, sommaire, mermaid)."""

import pytest

from models.document_model import DocumentModel
from models.exceptions import FileError


def test_render_fichier_inexistant_leve_file_error(tmp_path):
    with pytest.raises(FileError):
        DocumentModel().render(str(tmp_path / "absent.md"))


def test_render_type_non_supporte_leve_file_error(tmp_path):
    path = tmp_path / "note.txt"
    path.write_text("x", encoding="utf-8")
    with pytest.raises(FileError):
        DocumentModel().render(str(path))


def test_render_produit_le_titre_et_du_html(sample_markdown):
    doc = DocumentModel().render(str(sample_markdown))
    assert doc.title == "Titre"
    assert "<h1" in doc.body_html


def test_render_extrait_le_sommaire_hierarchique(sample_markdown):
    doc = DocumentModel().render(str(sample_markdown))
    assert doc.heading_count == 2
    assert doc.toc[0].text == "Titre"
    assert doc.toc[0].children[0].text == "Sous-titre"


def test_render_isole_les_blocs_mermaid(sample_markdown):
    doc = DocumentModel().render(str(sample_markdown))
    assert 'class="mermaid"' in doc.body_html
    assert "graph TD" in doc.body_html


def test_render_colore_les_blocs_de_code(sample_markdown):
    doc = DocumentModel().render(str(sample_markdown))
    assert "codehilite" in doc.body_html


def test_render_compte_les_mots(sample_markdown):
    doc = DocumentModel().render(str(sample_markdown))
    assert doc.word_count > 0
