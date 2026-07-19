"""Tests du modèle des fichiers récents."""

import config
from models.recent_files_model import RecentFilesModel


def _make_file(directory, name: str) -> str:
    path = directory / name
    path.write_text("x", encoding="utf-8")
    return str(path)


def test_add_insere_en_tete(temp_preferences, tmp_path):
    from pathlib import Path

    a = _make_file(tmp_path, "a.md")
    b = _make_file(tmp_path, "b.md")
    model = RecentFilesModel()
    model.add(a)
    model.add(b)
    items = model.get_all()
    assert items[0] == str(Path(b).resolve())
    assert items[1] == str(Path(a).resolve())


def test_add_deduplique(temp_preferences, tmp_path):
    a = _make_file(tmp_path, "a.md")
    model = RecentFilesModel()
    model.add(a)
    model.add(a)
    assert len(model.get_all()) == 1


def test_plafond_respecte(temp_preferences, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "RECENT_MAX", 3)
    model = RecentFilesModel()
    for i in range(5):
        model.add(_make_file(tmp_path, f"f{i}.md"))
    assert len(model.get_all()) == 3


def test_get_all_filtre_les_fichiers_disparus(temp_preferences, tmp_path):
    from pathlib import Path

    a = _make_file(tmp_path, "a.md")
    model = RecentFilesModel()
    model.add(a)
    Path(a).unlink()
    assert model.get_all() == []


def test_clear_vide_la_liste(temp_preferences, tmp_path):
    model = RecentFilesModel()
    model.add(_make_file(tmp_path, "a.md"))
    model.clear()
    assert model.get_all() == []


def test_persistance_entre_instances(temp_preferences, tmp_path):
    from pathlib import Path

    a = _make_file(tmp_path, "a.md")
    RecentFilesModel().add(a)
    assert RecentFilesModel().get_all() == [str(Path(a).resolve())]
