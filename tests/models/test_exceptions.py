"""Tests smoke des exceptions métier."""

from models.exceptions import FileError, RenderError


def test_file_error_herite_exception():
    assert issubclass(FileError, Exception)


def test_render_error_herite_exception():
    assert issubclass(RenderError, Exception)
