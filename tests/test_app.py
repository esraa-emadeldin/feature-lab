"""Tests for the one-page Streamlit app."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

# AppTest looks for relative paths next to THIS test file, so give it a full path.
APP = str(Path(__file__).parent.parent / "app.py")


def start():
    return AppTest.from_file(APP, default_timeout=120).run()


def shown_values(at):
    return [m.value for m in at.metric]


def test_app_loads():
    at = start()
    assert not at.exception
    # The simple version has exactly one of each control.
    assert len(at.toggle) == 1
    assert len(at.button) == 1
    assert len(at.slider) == 1


def test_select_with_noise():
    at = start()
    at.toggle[0].set_value(True).run()
    at.button[0].click().run()
    assert "86.7%" in shown_values(at)


def test_result_survives_slider():
    at = start()
    at.toggle[0].set_value(True).run()
    at.button[0].click().run()
    at.slider[0].set_value(20).run()  # moving PCA must not hide the selection result
    assert "86.7%" in shown_values(at)


def test_toggle_clears_result():
    at = start()
    at.toggle[0].set_value(True).run()
    at.button[0].click().run()
    at.toggle[0].set_value(False).run()  # data changed -> old result must disappear
    assert "86.7%" not in shown_values(at)
