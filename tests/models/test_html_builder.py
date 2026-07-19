"""Tests de l'assembleur de page HTML."""

from models.html_builder import build_page, build_welcome_page


def test_build_page_contient_le_corps_et_le_doctype():
    page = build_page("<p>Bonjour</p>", "light")
    assert "<p>Bonjour</p>" in page
    assert "<!DOCTYPE html>" in page


def test_build_page_inclut_le_conteneur_et_mermaid():
    page = build_page("<p>x</p>", "light")
    assert "markdown-body" in page
    assert "mermaid" in page


def test_build_page_theme_sombre_diffère_du_clair():
    light = build_page("<p>x</p>", "light")
    dark = build_page("<p>x</p>", "dark")
    assert light != dark
    assert 'theme: "neutral"' in light
    assert 'theme: "dark"' in dark


def test_build_welcome_page_contient_les_sections_et_icones():
    page = build_welcome_page("light")
    assert "MD Reader" in page
    assert "Raccourcis clavier" in page
    assert "Ctrl + O" in page
    assert "<svg" in page
