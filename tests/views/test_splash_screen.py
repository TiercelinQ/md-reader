"""Tests smoke de l'écran de démarrage."""

from PySide6.QtWidgets import QSplashScreen

from views.splash_screen import create_splash


def test_create_splash_light_retourne_splashscreen(qtbot):
    splash = create_splash("light")
    assert isinstance(splash, QSplashScreen)


def test_create_splash_dark_retourne_splashscreen(qtbot):
    splash = create_splash("dark")
    assert isinstance(splash, QSplashScreen)
