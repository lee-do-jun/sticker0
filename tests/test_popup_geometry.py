# tests/test_popup_geometry.py
from sticker0.widgets.popup_geometry import clamp_offset_to_parent


def test_clamp_offset_keeps_widget_inside_parent():
    assert clamp_offset_to_parent(0, 0, 10, 5, 100, 40) == (0, 0)
    assert clamp_offset_to_parent(200, 100, 10, 5, 100, 40) == (90, 35)


def test_clamp_offset_when_popup_larger_than_parent():
    assert clamp_offset_to_parent(5, 5, 100, 50, 80, 30) == (0, 0)
