# tests/test_presets.py
from sticker0.presets import (
    STICKER_PRESETS,
    BOARD_PRESETS,
    DEFAULT_STICKER_PRESET,
    DEFAULT_BOARD_PRESET,
    get_sticker_preset,
    get_board_preset,
)


def test_builtin_sticker_presets_exist():
    assert "Graphite" in STICKER_PRESETS
    assert "Mist" in STICKER_PRESETS
    assert "Sky" in STICKER_PRESETS
    assert "Banana" in STICKER_PRESETS


def test_graphite_preset_values():
    g = STICKER_PRESETS["Graphite"]
    assert g.border == "#d4d4d8"
    assert g.text == "#d4d4d8"
    assert g.area == "#2a2a2e"


def test_mist_preset_values():
    m = STICKER_PRESETS["Mist"]
    assert m.border == "#2f2f2f"
    assert m.text == "#2f2f2f"
    assert m.area == "#f2f2f0"


def test_sky_preset_values():
    sky = STICKER_PRESETS["Sky"]
    assert sky.border == "white"
    assert sky.text == "white"
    assert sky.area == "#1565c0"


def test_banana_preset_values():
    banana = STICKER_PRESETS["Banana"]
    assert banana.border == "black"
    assert banana.text == "black"
    assert banana.area == "#ffeb3b"


def test_builtin_board_presets_exist():
    assert "Graphite" in BOARD_PRESETS
    assert "Ivory" in BOARD_PRESETS
    assert "Slate" in BOARD_PRESETS
    assert "Dust" in BOARD_PRESETS
    assert "Forest" in BOARD_PRESETS
    assert "Amber" in BOARD_PRESETS


def test_graphite_board_preset_values():
    g = BOARD_PRESETS["Graphite"]
    assert g.background == "#1e1e22"
    assert g.indicator == "#d4d4d8"


def test_default_sticker_preset():
    assert DEFAULT_STICKER_PRESET == "Clear"


def test_default_board_preset():
    assert DEFAULT_BOARD_PRESET == "Slate"


def test_clear_preset_values():
    c = STICKER_PRESETS["Clear"]
    assert c.border == "inherit"
    assert c.text == "inherit"
    assert c.area == "transparent"


def test_get_sticker_preset_found():
    preset = get_sticker_preset("Graphite")
    assert preset is not None
    assert preset.name == "Graphite"


def test_get_sticker_preset_not_found():
    assert get_sticker_preset("Nonexistent") is None


def test_get_board_preset_found():
    preset = get_board_preset("Ivory")
    assert preset is not None
    assert preset.name == "Ivory"
