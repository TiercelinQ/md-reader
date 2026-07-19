"""Constantes applicatives centralisées — MD Reader.

Toute valeur réutilisée dans plus d'un fichier vit ici. Les seules couleurs
présentes sont les stops d'accent, ICON_COLORS et SPLASH_COLORS (exceptions
documentées au principe « toutes les valeurs visuelles en QSS ») : les neutres
et sémantiques vivent dans les feuilles QSS et les CSS de contenu.
"""

# --- Identité ---------------------------------------------------------------
APP_NAME: str = "MD Reader"
APP_VERSION: str = "1.0.1"

# --- Préférences ------------------------------------------------------------
PREFERENCES_FILE: str = "preferences.json"

# --- Logging (voir utils/logger.py) -----------------------------------------
LOG_DIR: str = "logs"
LOG_LEVEL: str = "INFO"
LOG_MAX_BYTES: int = 1_000_000
LOG_BACKUP_COUNT: int = 5

# --- Toasts (voir layout.md §5) ---------------------------------------------
TOAST_POSITION: str = "top-right"

# --- Splash (peint programmatiquement, non stylable QSS — exception) --------
# Le splash se ferme dès que la page d'accueil a fini de charger (disponibilité
# réelle), en respectant ce plancher minimal. SPLASH_MAX_WAIT_MS est le repli si
# l'événement loadFinished ne survient pas, pour garantir la fermeture.
SPLASH_MIN_DURATION_MS: int = 500
SPLASH_MAX_WAIT_MS: int = 4000
SPLASH_COLORS: dict[str, dict[str, str]] = {
    "light": {"bg": "#FBFBFC", "text": "#111318"},
    "dark": {"bg": "#17191C", "text": "#EFF0F0"},
}

# --- Animation (design-system.md §6) ----------------------------------------
ANIM_DEFAULT_MS: int = 160
ANIM_SLOW_MS: int = 240
ANIMATIONS_ENABLED: bool = True

# --- Stops d'accent (palette Anthracite, dérivés) ---------------------------
# Accent très sombre (HSL 217°, 19 %, 27 %) : hover/pressed dérivés par
# assombrissement (et non par la règle L=50 %/42 % qui inverserait la rampe).
PRIMARY_50: str = "#F0F2F5"  # fond sélection (clair)
PRIMARY_400: str = "#A4AFC1"  # accent premier plan (sombre)
PRIMARY_600: str = "#374151"  # accent : actif clair, fond bouton primaire
PRIMARY_700: str = "#2B323F"  # hover bouton primaire
PRIMARY_800: str = "#202630"  # pressed bouton primaire
PRIMARY_900: str = "#343D4C"  # fond sélection (sombre)
ON_PRIMARY: str = "#FFFFFF"  # texte sur l'accent

# --- Icônes Lucide (config.py = exception documentée, non stylable QSS) ------
ICON_SM: int = 16
ICON_MD: int = 20
ICON_LG: int = 24
ICON_STROKE: float = 1.75
ICON_COLORS: dict[str, dict[str, str]] = {
    "light": {
        "default": "#6F7073",  # text-subtle
        "active": PRIMARY_600,
        "success": "#328F6D",  # success-600
        "warning": "#A58427",  # warning-600
        "danger": "#BA3B52",  # danger-600
        "info": PRIMARY_600,  # info = accent
        "muted": "#A2A3A5",  # text-muted
    },
    "dark": {
        "default": "#9FA0A2",  # text-subtle dark
        "active": PRIMARY_400,
        "success": "#6EC4A4",  # success-600 dark
        "warning": "#D2B460",  # warning-600 dark
        "danger": "#CB7282",  # danger-600 dark
        "info": PRIMARY_400,  # info = accent dark
        "muted": "#727375",  # text-muted dark
    },
}

# --- Fichiers récents -------------------------------------------------------
RECENT_MAX: int = 10

# --- Zoom du contenu (QWebEngineView.setZoomFactor) -------------------------
ZOOM_MIN: float = 0.5
ZOOM_MAX: float = 3.0
ZOOM_STEP: float = 0.1
ZOOM_DEFAULT: float = 1.0

# --- Dimensions de layout (structure, non stylable QSS) ---------------------
WINDOW_MIN_SIZE: tuple[int, int] = (1024, 768)
WINDOW_DEFAULT_SIZE: tuple[int, int] = (1280, 800)
EXPLORER_WIDTH: int = 280
TOC_WIDTH: int = 240

# --- Rendu Markdown ---------------------------------------------------------
# "extra" fournit fenced_code, tables, footnotes, attr_list, def_list, md_in_html.
MARKDOWN_EXTENSIONS: list[str] = ["extra", "codehilite", "toc", "sane_lists"]

# --- Extensions de fichier acceptées ----------------------------------------
MARKDOWN_SUFFIXES: tuple[str, ...] = (".md", ".markdown", ".mdown", ".mkd")
