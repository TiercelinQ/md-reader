# Changelog

All notable changes to this project are documented in this file.
The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [Unreleased]

## [1.1.0] - 2026-07-19
### Added
- Multiple documents can be open at once in tabs: opening a file adds a tab (or focuses it if already open), tabs close with the close button or Ctrl+W, and open tabs are restored on the next launch.
- The explorer and table-of-contents panels now persist their open/closed state and their width, kept even after the panel is hidden and restored on the next launch.

## [1.0.1] - 2026-07-19
### Changed
- Faster startup: the splash screen is now dismissed as soon as the welcome page is ready instead of after a fixed delay.
- Faster document rendering: the Mermaid script is loaded only for documents that actually contain a diagram.

### Fixed
- Removed content flicker when resizing the window: the web view background now matches the active theme.

## [1.0.0] - 2026-07-18
### Added
- Initial release.
- Read-only Markdown viewer with a clean, palette-themed rendering (Python-Markdown + Pygments).
- Mermaid diagram rendering (client-side, vendored mermaid.js).
- Master-detail layout: file explorer, document view, clickable table of contents.
- Light/dark theme toggle, in-document search, content zoom, recent files, external links open in the system browser.
- Welcome screen at startup: app introduction, toolbar icon legend, and keyboard shortcuts.
### Fixed
- Splash screen now shows only the app icon (transparent background, no frame or app name).
