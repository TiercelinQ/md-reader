# MD Reader

[![CI](https://github.com/TiercelinQ/md-reader/actions/workflows/ci.yml/badge.svg)](https://github.com/TiercelinQ/md-reader/actions/workflows/ci.yml)

A Windows desktop viewer for Markdown files, **preview-only** (no editing). Clean Markdown rendering and polished **Mermaid diagrams**, in a master-detail interface (explorer, document, table of contents).

Generated with the Python App Generator framework v1.1.0 · Design system v2.0.

## Features

- **Open a .md file** and view it rendered (Ctrl+O).
- **Multiple files open in tabs**: each document has its own tab, close via the close button or Ctrl+W, tabs restored on the next launch.
- **Side explorer**: open a folder and browse the tree of .md files (Ctrl+Shift+O).
- **Clean Markdown rendering**: headings, lists, tables, blockquotes, images, links, footnotes.
- **Mermaid diagrams** (` ```mermaid ` blocks), rendered client-side.
- **Syntax highlighting** for code blocks (Pygments).
- **Clickable table of contents (TOC)** built from the headings, with scroll-to-section.
- **Search** within the current document (Ctrl+F).
- **Content zoom** (Ctrl++, Ctrl+-, Ctrl+0).
- **Light/dark theme**: the rendered content follows the theme.
- **Recent files** (persisted).
- **External links** open in the system browser.
- **Welcome screen** at startup: introduction, toolbar icon legend, keyboard shortcuts.

### Out of scope (v1.0)

- File editing (read-only by design).
- Automatic reload on file change (deferred).
- Copy-code button (deferred).
- File drag-and-drop (dropped).

## Tech stack

| Item         | Choice                                                                                       |
| ------------ | -------------------------------------------------------------------------------------------- |
| Language     | Python 3.12+                                                                                 |
| UI           | PySide6 (Windows)                                                                            |
| Rendering    | QtWebEngine (`QWebEngineView`) — **provided by the `PySide6` meta-package** (bundles Chromium) |
| Markdown     | `markdown` (Python-Markdown) + extensions                                                    |
| Code         | `Pygments`                                                                                   |
| Diagrams     | mermaid.js **vendored** (`resources/mermaid.min.js`, v11)                                    |
| Icons        | Lucide (SVG vendored in `resources/icons/`)                                                  |
| Architecture | Strict MVC                                                                                   |
| Style        | Centralized QSS + palette-derived content CSS                                                |

No network connection at runtime: mermaid.js and the icons are bundled locally.

## Architecture (strict MVC)

```
md-reader/
├── main.py                  Entry point (strict init, splash, wiring)
├── config.py                Constants (palette, zoom, dimensions…)
├── models/
│   ├── document_model.py    Markdown → HTML + Mermaid extraction + TOC
│   ├── html_builder.py      Themed HTML page assembly
│   ├── recent_files_model.py Recent files (persisted)
│   └── exceptions.py        FileError, RenderError
├── views/
│   ├── main_window.py       Topbar + QSplitter (3 panels) + statusbar
│   ├── explorer_view.py     .md file tree
│   ├── document_view.py     Document tabs (web view) + search bar
│   ├── toc_view.py          Clickable TOC
│   ├── toast_manager.py     Notifications
│   └── splash_screen.py     Splash screen
├── controllers/
│   ├── main_controller.py   Chrome, navigation, theme, recents, window state
│   └── document_controller.py Rendering, zoom, search, links
├── utils/                   helpers, logger, icons, resource_path
├── resources/               QSS, content CSS, Pygments CSS, mermaid.js, icons, icon.ico
├── scripts/build.ps1        PyInstaller build
├── docs/                    generation specs + CHANGELOG
└── tests/                   pytest + pytest-qt
```

## Requirements

- Windows, Python 3.12 or later.
- QtWebEngine is included in the `PySide6` package (no separate install).

## Installation and running

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Debug mode (console logs): set the environment variable `MDREADER_DEBUG=1`.

## Palette — Anthracite (custom)

Accent `#374151` (slate gray) + overrides provided for both themes. Neutrals and semantics derived (design-system v2.0). WCAG AA contrast verified.

| Role               | Light     | Dark      |
| ------------------ | --------- | --------- |
| Main background    | `#FBFBFC` | `#17191C` |
| Secondary background | `#F2F3F5` | `#202327` |
| Accent             | `#374151` | `#374151` |
| Text               | `#111318` | `#EFF0F0` |
| Border             | `#DEE1E6` | `#454B54` |

## Tests and quality

```powershell
pip install -r requirements-dev.txt
ruff check .        # lint
ruff format .       # format
mypy .              # strict typing
pytest              # tests (pytest + pytest-qt)
```

A `Stop` hook (`.claude/settings.json`) runs `ruff check .` at the end of a maintenance session; it assumes `ruff` is installed. Adjustable or removable.

Dependencies (Python packages and GitHub actions) are tracked by [Dependabot](.github/dependabot.yml), which opens a weekly PR for each available update.

## Windows packaging (.exe)

```powershell
pip install -r requirements-dev.txt
powershell -ExecutionPolicy Bypass -File scripts\build.ps1
```

The executable is produced at `dist\MD Reader.exe`. QtWebEngine (Chromium) is bundled via the PySide6 hooks. If onefile mode fails (extraction of `QtWebEngineProcess`), switch to onedir mode (see the comment in `build.spec`). In packaged mode, `preferences.json` and `logs/` live in `%APPDATA%\MD Reader`.
