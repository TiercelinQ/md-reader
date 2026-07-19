"""Tests des fonctions pures de utils/helpers.py."""

import pytest

from utils import helpers


def test_get_preference_defaut_si_absent(temp_preferences):
    assert helpers.get_preference("inexistant", "defaut") == "defaut"


def test_set_puis_get_preference(temp_preferences):
    helpers.set_preference("cle", 42)
    assert helpers.get_preference("cle") == 42


def test_set_preference_conserve_les_autres_cles(temp_preferences):
    helpers.set_preference("a", 1)
    helpers.set_preference("b", 2)
    assert helpers.get_preference("a") == 1
    assert helpers.get_preference("b") == 2


def test_load_preferences_vide_si_fichier_absent(temp_preferences):
    assert helpers.load_preferences() == {}


@pytest.mark.parametrize(
    "name,expected",
    [("doc.md", True), ("doc.markdown", True), ("doc.txt", False), ("doc", False)],
)
def test_is_markdown_file(tmp_path, name, expected):
    path = tmp_path / name
    path.write_text("x", encoding="utf-8")
    assert helpers.is_markdown_file(str(path)) is expected


def test_is_markdown_file_dossier_est_faux(tmp_path):
    assert helpers.is_markdown_file(str(tmp_path)) is False


def test_read_stylesheet_light_contient_qmainwindow():
    assert "QMainWindow" in helpers.read_stylesheet("light")


def test_read_stylesheet_dark_contient_qmainwindow():
    assert "QMainWindow" in helpers.read_stylesheet("dark")
