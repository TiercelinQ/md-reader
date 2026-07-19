# MD Reader

[![CI](https://github.com/TiercelinQ/md-reader/actions/workflows/ci.yml/badge.svg)](https://github.com/TiercelinQ/md-reader/actions/workflows/ci.yml)

Visionneuse desktop Windows de fichiers Markdown en **prévisualisation seule** (aucune édition). Rendu Markdown propre et **diagrammes Mermaid** soignés, dans une interface master-detail (explorateur, document, sommaire).

Généré avec le framework Python App Generator v1.1.0 · Design system v2.0.

## Fonctionnalités

- **Ouvrir un fichier .md** et l'afficher rendu (Ctrl+O).
- **Explorateur latéral** : ouvrir un dossier et parcourir l'arborescence des fichiers .md (Ctrl+Maj+O).
- **Rendu Markdown** propre : titres, listes, tableaux, citations, images, liens, notes de bas de page.
- **Diagrammes Mermaid** (blocs ` ```mermaid `), rendus côté client.
- **Coloration syntaxique** des blocs de code (Pygments).
- **Sommaire (TOC)** cliquable généré depuis les titres, avec défilement vers la section.
- **Recherche** dans le document courant (Ctrl+F).
- **Zoom** du contenu (Ctrl++, Ctrl+-, Ctrl+0).
- **Thème clair/sombre** : le contenu rendu suit le thème.
- **Fichiers récents** (persistés).
- **Liens externes** ouverts dans le navigateur système.
- **Page d'accueil** au lancement : présentation, légende des icônes de la barre d'outils, raccourcis clavier.

### Hors périmètre (v1.0)

- Édition de fichiers (lecture seule assumée).
- Rechargement automatique au changement du fichier (différé).
- Bouton copier le code (différé).
- Glisser-déposer d'un fichier (abandonné).

## Pile technique

| Élément      | Choix                                                                                        |
| ------------ | -------------------------------------------------------------------------------------------- |
| Langage      | Python 3.12+                                                                                 |
| UI           | PySide6 (Windows)                                                                            |
| Rendu        | QtWebEngine (`QWebEngineView`) — **fourni par le méta-paquet `PySide6`** (embarque Chromium) |
| Markdown     | `markdown` (Python-Markdown) + extensions                                                    |
| Code         | `Pygments`                                                                                   |
| Diagrammes   | mermaid.js **vendored** (`resources/mermaid.min.js`, v11)                                    |
| Icônes       | Lucide (SVG vendored dans `resources/icons/`)                                                |
| Architecture | MVC strict                                                                                   |
| Style        | QSS centralisé + CSS de contenu dérivés de la palette                                        |

Aucune connexion réseau au runtime : mermaid.js et les icônes sont embarqués localement.

## Architecture (MVC strict)

```
md-reader/
├── main.py                  Point d'entrée (init strict, splash, câblage)
├── config.py                Constantes (palette, zoom, dimensions…)
├── models/
│   ├── document_model.py    Markdown → HTML + extraction Mermaid + sommaire
│   ├── html_builder.py      Assemblage de la page HTML thématisée
│   ├── recent_files_model.py Fichiers récents (persistés)
│   └── exceptions.py        FileError, RenderError
├── views/
│   ├── main_window.py       Topbar + QSplitter (3 volets) + statusbar
│   ├── explorer_view.py     Arborescence des .md
│   ├── document_view.py     Vue web + barre de recherche
│   ├── toc_view.py          Sommaire cliquable
│   ├── toast_manager.py     Notifications
│   └── splash_screen.py     Écran de démarrage
├── controllers/
│   ├── main_controller.py   Chrome, navigation, thème, récents, état fenêtre
│   └── document_controller.py Rendu, zoom, recherche, liens
├── utils/                   helpers, logger, icons, resource_path
├── resources/               QSS, CSS de contenu, Pygments CSS, mermaid.js, icônes, icon.ico
├── scripts/build.ps1        Build PyInstaller
├── docs/                    specs de génération + CHANGELOG
└── tests/                   pytest + pytest-qt
```

## Prérequis

- Windows, Python 3.12 ou plus.
- QtWebEngine est inclus dans le paquet `PySide6` (aucune installation séparée).

## Installation et lancement

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Mode debug (logs console) : définir la variable d'environnement `MDREADER_DEBUG=1`.

## Palette — Anthracite (custom)

Accent `#374151` (gris ardoise) + overrides fournis pour les deux thèmes. Neutres et sémantiques dérivés (design-system v2.0). Contraste WCAG AA vérifié.

| Rôle            | Clair     | Sombre    |
| --------------- | --------- | --------- |
| Fond principal  | `#FBFBFC` | `#17191C` |
| Fond secondaire | `#F2F3F5` | `#202327` |
| Accent          | `#374151` | `#374151` |
| Texte           | `#111318` | `#EFF0F0` |
| Bordure         | `#DEE1E6` | `#454B54` |

## Tests et qualité

```powershell
pip install -r requirements-dev.txt
ruff check .        # lint
ruff format .       # format
mypy .              # typage strict
pytest              # tests (pytest + pytest-qt)
```

Un hook `Stop` (`.claude/settings.json`) lance `ruff check .` en fin de session de maintenance ; il suppose `ruff` installé. Ajustable ou supprimable.

## Packaging Windows (.exe)

```powershell
pip install -r requirements-dev.txt
powershell -ExecutionPolicy Bypass -File scripts\build.ps1
```

L'exécutable est produit dans `dist\MD Reader.exe`. QtWebEngine (Chromium) est embarqué via les hooks PySide6. En cas d'échec du mode onefile (extraction de `QtWebEngineProcess`), passer en mode onedir (voir le commentaire dans `build.spec`). En mode packagé, `preferences.json` et `logs/` vivent dans `%APPDATA%\MD Reader`.
