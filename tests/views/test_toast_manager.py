"""Tests smoke du gestionnaire de toasts."""

from PySide6.QtWidgets import QWidget

from views.toast_manager import ToastManager


def test_toast_manager_show_ne_crash_pas(qtbot):
    host = QWidget()
    qtbot.addWidget(host)
    host.resize(800, 600)
    manager = ToastManager(host, "light")
    manager.show("success", "Enregistré", "Tout va bien")


def test_toast_manager_toast_danger_reste_affiche(qtbot):
    host = QWidget()
    qtbot.addWidget(host)
    host.resize(800, 600)
    manager = ToastManager(host, "dark")
    manager.show("danger", "Erreur", "Détail technique")
