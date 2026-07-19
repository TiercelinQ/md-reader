"""Tests de l'assembleur de page HTML."""

from models.html_builder import build_page, build_welcome_page


def test_build_page_contient_le_corps_et_le_doctype():
    page = build_page("<p>Bonjour</p>", "light")
    assert "<p>Bonjour</p>" in page
    assert "<!DOCTYPE html>" in page


def test_build_page_inclut_le_conteneur():
    page = build_page("<p>x</p>", "light")
    assert "markdown-body" in page


def test_build_page_inclut_mermaid_si_diagramme_present():
    page = build_page('<pre class="mermaid">graph TD; A--&gt;B;</pre>', "light")
    assert "mermaid.min.js" in page


def test_build_page_omet_mermaid_sans_diagramme():
    page = build_page("<p>x</p>", "light")
    assert "mermaid.min.js" not in page


def test_build_page_theme_sombre_diffère_du_clair():
    body = '<pre class="mermaid">graph TD; A--&gt;B;</pre>'
    light = build_page(body, "light")
    dark = build_page(body, "dark")
    assert light != dark
    assert 'theme: "neutral"' in light
    assert 'theme: "dark"' in dark


def test_build_welcome_page_contient_les_sections_et_icones():
    page = build_welcome_page("light")
    assert "MD Reader" in page
    assert "Raccourcis clavier" in page
    assert "Ctrl + O" in page
    assert "<svg" in page
