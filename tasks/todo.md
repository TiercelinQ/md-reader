# CI/CD md-reader - plan

## Contexte
- Depot public GitHub : TiercelinQ/md-reader (vrai projet, pas un test).
- App Python/PySide6 livree par le generateur python, version 1.0.0.
- Specificite : rendu Mermaid via QtWebEngine (Chromium) -> CI Linux headless plus lourde que Tasky.
- Opt-ins : tests (pytest-qt), packaging PyInstaller onefile, changelog. Pas d'i18n, pas de Salesforce.

## Decisions
- Runner CI : ubuntu-latest (24.04).
- Perimetre : CI + CD.
- CI (quality) : ruff check, ruff format --check, mypy strict, pytest, sur ubuntu-latest + QT_QPA_PLATFORM=offscreen + flags QtWebEngine.
- CD : build .exe PyInstaller sur windows-latest, declenchee par tag v*.
- Nom exe : "MD Reader.exe" (espace) -> chemin quote dans la CD.
- Source de version : config.py APP_VERSION ; changelog docs/release/CHANGELOG.md.
- Flux : branche + PR ; l'utilisateur merge (classifier bloque le merge cote Claude).

## Etapes
- [ ] Branche `feat/ci-cd`
- [ ] `.github/workflows/ci.yml` : quality + libs Chromium + flags QtWebEngine (--no-sandbox)
- [ ] `.github/workflows/release.yml` : verif version, pyinstaller, extraction changelog, Release (files quote)
- [ ] Badge CI dans le README
- [ ] Commit + push + PR via gh
- [ ] CI verte sur la PR (prevoir iterations rouge->correctif sur QtWebEngine)
- [ ] Squash merge (utilisateur) + resync local
- [ ] Protection de main (ruleset : PR obligatoire, check quality) une fois la CI passee
- [ ] Test CD : tag v1.0.0 -> Release + MD Reader.exe

## Verification
- CI : run Actions vert sur la PR (ruff, format, mypy, pytest OK, y compris tests QtWebEngine).
- CD : Release GitHub v1.0.0 avec "MD Reader.exe" attache + corps = bloc CHANGELOG 1.0.0.
- Gate : une PR rouge ne peut pas etre mergee dans main (apres protection).

## Risques identifies
- QtWebEngine headless : libs systeme et flags Chromium a ajuster ; non reproductible depuis Windows -> verifier par le run reel.
- PyInstaller onefile + QtWebEngine : le build .exe peut necessiter le mode onedir (voir docstring build.spec) ; a verifier au 1er tag.

## Result
- (a remplir en fin de tache)
