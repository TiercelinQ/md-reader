"""Modèle document — lecture d'un fichier Markdown et conversion en HTML rendu.

Pipeline : lecture (validation → FileError) → extraction/isolation des blocs
```mermaid (placeholder) → conversion Markdown→HTML (markdown + codehilite/Pygments)
→ réinjection des blocs mermaid en `<pre class="mermaid">` → extraction du sommaire
(toc_tokens) et des compteurs. Zéro PySide6.
"""

import html
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import markdown

import config
from models.exceptions import FileError, RenderError

logger = logging.getLogger(__name__)

# Blocs mermaid : ```mermaid ... ``` (fence sans indentation). Le contenu brut est
# conservé tel quel — mermaid.js parse sa propre syntaxe, il ne doit pas être échappé.
_MERMAID_RE = re.compile(r"```[ \t]*mermaid[ \t]*\r?\n(.*?)\r?\n```", re.DOTALL)
_PLACEHOLDER = "MERMAIDBLOCKPLACEHOLDER{}"
_WORD_RE = re.compile(r"\w+", re.UNICODE)


@dataclass
class TocEntry:
    """Un titre du document (niveau, texte, ancre) et ses sous-titres."""

    level: int
    text: str
    anchor: str
    children: list["TocEntry"] = field(default_factory=list)


@dataclass
class RenderedDocument:
    """Résultat du rendu d'un document Markdown."""

    body_html: str
    toc: list[TocEntry]
    title: str
    heading_count: int
    word_count: int


class DocumentModel:
    """Convertit un fichier Markdown en HTML rendu prêt pour la vue web."""

    def render(self, path: str) -> RenderedDocument:
        """Rend le fichier `path` en `RenderedDocument`.

        Args:
            path: Chemin du fichier Markdown.

        Raises:
            FileError: fichier introuvable, illisible ou de type non pris en charge.
            RenderError: échec de la conversion Markdown.
        """
        source = self._read_source(path)
        source, mermaid_blocks = self._extract_mermaid(source)

        md = markdown.Markdown(
            extensions=config.MARKDOWN_EXTENSIONS,
            extension_configs={
                "codehilite": {"guess_lang": False, "css_class": "codehilite"},
                "toc": {"anchorlink": False, "permalink": False},
            },
            output_format="html",
        )
        try:
            body_html = md.convert(source)
        except Exception as e:  # noqa: BLE001 — conversion tierce : on encapsule proprement
            logger.exception("Échec de conversion Markdown : %s", path)
            raise RenderError(str(e)) from e

        body_html = self._reinject_mermaid(body_html, mermaid_blocks)

        toc = self._build_toc(getattr(md, "toc_tokens", []))
        heading_count = self._count_headings(toc)
        title = toc[0].text if toc else Path(path).stem
        word_count = len(_WORD_RE.findall(source))

        logger.info("Document rendu : %s (%d titres, %d mots)", path, heading_count, word_count)
        return RenderedDocument(
            body_html=body_html,
            toc=toc,
            title=title,
            heading_count=heading_count,
            word_count=word_count,
        )

    @staticmethod
    def _read_source(path: str) -> str:
        """Valide le chemin et lit le contenu UTF-8. Lève FileError sur anomalie."""
        p = Path(path).resolve()
        if not p.is_file():
            raise FileError(f"Fichier introuvable : {p}")
        if p.suffix.lower() not in config.MARKDOWN_SUFFIXES:
            suffix = p.suffix or "(sans extension)"
            raise FileError(f"Type de fichier non pris en charge : {suffix}")
        try:
            return p.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            raise FileError(f"Encodage non lisible (UTF-8 attendu) : {p.name}") from e
        except OSError as e:
            raise FileError(f"Lecture impossible : {p.name}") from e

    @staticmethod
    def _extract_mermaid(source: str) -> tuple[str, list[str]]:
        """Remplace chaque bloc mermaid par un placeholder ; renvoie (texte, blocs bruts)."""
        blocks: list[str] = []

        def _stash(match: re.Match[str]) -> str:
            blocks.append(match.group(1))
            return f"\n\n{_PLACEHOLDER.format(len(blocks) - 1)}\n\n"

        return _MERMAID_RE.sub(_stash, source), blocks

    @staticmethod
    def _reinject_mermaid(body_html: str, blocks: list[str]) -> str:
        """Restitue les blocs mermaid bruts en `<pre class="mermaid">` dans le HTML."""
        for i, raw in enumerate(blocks):
            token = _PLACEHOLDER.format(i)
            # markdown enveloppe le placeholder isolé dans un <p> ; on couvre les deux cas.
            replacement = f'<pre class="mermaid">{html.escape(raw)}</pre>'
            body_html = body_html.replace(f"<p>{token}</p>", replacement)
            body_html = body_html.replace(token, replacement)
        return body_html

    def _build_toc(self, tokens: list[dict[str, Any]]) -> list[TocEntry]:
        """Convertit la structure `toc_tokens` de markdown en arbre de TocEntry."""
        entries: list[TocEntry] = []
        for token in tokens:
            entries.append(
                TocEntry(
                    level=int(token.get("level", 1)),
                    text=str(token.get("name", "")),
                    anchor=str(token.get("id", "")),
                    children=self._build_toc(token.get("children", [])),
                )
            )
        return entries

    def _count_headings(self, toc: list[TocEntry]) -> int:
        """Compte récursivement le nombre de titres du sommaire."""
        return sum(1 + self._count_headings(entry.children) for entry in toc)
