# tests/test_presets.py
from sticker0.presets import (
    StickerPreset,
    BoardThemePreset,
    STICKER_PRESETS,
    BOARD_PRESETS,
    DEFAULT_STICKER_PRESET,
    DEFAULT_BOARD_PRESET,
    get_sticker_preset,
    get_board_preset,
)


def test_builtin_sticker_presets_exist():
    assert "Snow" in STICKER_PRESETS
    assert "Ink" in STICKER_PRESETS
    assert "Sky" in STICKER_PRESETS
    assert "Banana" in STICKER_PRESETS


def test_snow_preset_values():
    snow = STICKER_PRESETS["Snow"]
    assert snow.border == "white"
    assert snow.text == "white"
    assert snow.area == "transparent"


def test_ink_preset_values():
    ink = STICKER_PRESETS["Ink"]
    assert ink.border == "black"
    assert ink.text == "black"
    assert ink.area == "transparent"


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
    assert "Dark Base" in BOARD_PRESETS
    assert "Light Base" in BOARD_PRESETS
    assert "Dark Mode" in BOARD_PRESETS
    assert "White Mode" in BOARD_PRESETS


def test_dark_mode_preset_values():
    dm = BOARD_PRESETS["Dark Mode"]
    assert dm.background == "transparent"
    assert dm.indicator == "white"


def test_default_sticker_preset():
    assert DEFAULT_STICKER_PRESET == "Snow"


def test_default_board_preset():
    assert DEFAULT_BOARD_PRESET == "Dark Mode"


def test_get_sticker_preset_found():
    preset = get_sticker_preset("Snow")
    assert preset is not None
    assert preset.name == "Snow"


def test_get_sticker_preset_not_found():
    assert get_sticker_preset("Nonexistent") is None


def test_get_board_preset_found():
    preset = get_board_preset("Dark Base")
    assert preset is not None
    assert preset.name == "Dark Base"
