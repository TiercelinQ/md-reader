"""Assemblage de la page HTML thématisée affichée dans la vue web.

Combine le corps HTML rendu (document_model) avec le CSS de contenu et le CSS de
coloration Pygments (inlinés, petits). `mermaid.min.js` (~3 Mo) est référencé en
script EXTERNE via une URL file:// : `QWebEngineView.setHtml()` est limité à ~2 Mo,
inliner mermaid dépasserait la limite et rendrait une page blanche.
Zéro PySide6, zéro valeur visuelle en dur : les couleurs vivent dans les CSS.
"""

import logging
import re
from functools import cache
from pathlib import Path

import config
from utils.resource_path import resource_path

logger = logging.getLogger(__name__)

_MERMAID_THEME = {"light": "neutral", "dark": "dark"}
_STROKE_RE = re.compile(r'stroke-width="[^"]*"')

# Légende de la barre d'outils (nom d'icône Lucide, libellé) pour la page d'accueil.
_TOOLBAR_LEGEND = [
    ("file-text", "Ouvrir un fichier"),
    ("folder-open", "Ouvrir un dossier"),
    ("history", "Fichiers récents"),
    ("search", "Rechercher dans le document"),
    ("zoom-out", "Réduire le zoom du contenu"),
    ("zoom-in", "Agrandir le zoom du contenu"),
    ("panel-left", "Afficher / masquer l'explorateur"),
    ("panel-right", "Afficher / masquer le sommaire"),
    ("moon", "Basculer entre thème clair et sombre"),
]

# Raccourcis clavier (combinaison, action) pour la page d'accueil.
_SHORTCUTS = [
    ("Ctrl + O", "Ouvrir un fichier"),
    ("Ctrl + Maj + O", "Ouvrir un dossier"),
    ("Ctrl + F", "Rechercher dans le document"),
    ("Ctrl + +", "Agrandir le zoom"),
    ("Ctrl + -", "Réduire le zoom"),
    ("Ctrl + 0", "Réinitialiser le zoom"),
    ("Échap", "Fermer la barre de recherche"),
    ("F5", "Recharger le document"),
]


@cache
def _read_resource(relative: str) -> str:
    """Lit une ressource texte (CSS/JS) une seule fois puis la met en cache."""
    path = Path(resource_path(relative))
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        logger.warning("Ressource introuvable : %s", relative)
        return ""


def build_page(body_html: str, theme: str) -> str:
    """Construit la page HTML complète pour le thème donné.

    Args:
        body_html: Corps HTML rendu du document (issu de DocumentModel).
        theme: "light" ou "dark".

    Returns:
        Le document HTML complet, prêt pour `QWebEngineView.setHtml`.
    """
    content_css = _read_resource(f"resources/content_{theme}.css")
    pygments_css = _read_resource(f"resources/pygments_{theme}.css")
    mermaid_src = Path(resource_path("resources/mermaid.min.js")).resolve().as_uri()
    mermaid_theme = _MERMAID_THEME.get(theme, "neutral")

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{content_css}</style>
<style>{pygments_css}</style>
</head>
<body>
<article class="markdown-body">
{body_html}
</article>
<script src="{mermaid_src}"></script>
<script>
// run() explicite : fiable même si le DOM est déjà analysé (contrairement à startOnLoad).
if (window.mermaid) {{
  window.mermaid.initialize({{
    startOnLoad: false, theme: "{mermaid_theme}", securityLevel: "strict"
  }});
  window.mermaid.run({{ querySelector: ".mermaid" }});
}}
</script>
</body>
</html>"""


def _inline_icon(name: str, color: str) -> str:
    """Renvoie le SVG Lucide `name` recoloré, prêt à être inséré inline (20 px)."""
    svg = _read_resource(f"resources/icons/{name}.svg")
    if not svg:
        return ""
    svg = svg.replace("currentColor", color)
    svg = _STROKE_RE.sub(f'stroke-width="{config.ICON_STROKE}"', svg)
    return svg.replace('width="24" height="24"', 'width="20" height="20"')


def build_welcome_page(theme: str) -> str:
    """Construit la page d'accueil (présentation, légende des icônes, raccourcis)."""
    content_css = _read_resource(f"resources/content_{theme}.css")
    icon_color = config.ICON_COLORS.get(theme, config.ICON_COLORS["light"])["default"]

    legend_rows = "\n".join(
        f'<tr><td class="icon-cell">{_inline_icon(name, icon_color)}</td><td>{label}</td></tr>'
        for name, label in _TOOLBAR_LEGEND
    )
    shortcut_rows = "\n".join(
        f"<tr><td><kbd>{keys}</kbd></td><td>{label}</td></tr>" for keys, label in _SHORTCUTS
    )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{content_css}</style>
<style>
.welcome-lead {{ color: var(--text-subtle); font-size: 1.05em; }}
table.legend {{ border-collapse: collapse; margin: 0 0 1.5em; }}
table.legend td {{ border: none; padding: 6px 14px 6px 0; vertical-align: middle; }}
table.legend td.icon-cell {{ width: 28px; text-align: center; padding-right: 12px; }}
table.legend svg {{ vertical-align: middle; }}
</style>
</head>
<body>
<article class="markdown-body">
<h1>MD Reader</h1>
<p class="welcome-lead">Visionneuse Markdown en lecture seule. Ouvrez un fichier ou un dossier
pour afficher son rendu, avec coloration du code et diagrammes Mermaid.</p>
<h2>Barre d'outils</h2>
<table class="legend">{legend_rows}</table>
<h2>Raccourcis clavier</h2>
<table class="legend">{shortcut_rows}</table>
<h2>Astuces</h2>
<ul>
<li>Cliquez un fichier <code>.md</code> dans l'explorateur pour l'afficher.</li>
<li>Cliquez un titre du sommaire pour vous y rendre dans le document.</li>
<li>Les liens externes s'ouvrent dans votre navigateur système.</li>
<li>Le code est coloré et les diagrammes Mermaid sont rendus automatiquement.</li>
</ul>
</article>
</body>
</html>"""
