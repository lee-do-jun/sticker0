# tests/test_config.py
import os
import pytest
from pathlib import Path
from sticker0.config import AppConfig, BoardTheme, BorderConfig


def test_defaults_when_no_file(tmp_path):
    from sticker0.presets import STICKER_PRESETS, DEFAULT_STICKER_PRESET

    g = STICKER_PRESETS[DEFAULT_STICKER_PRESET]
    config = AppConfig.load(path=tmp_path / ".stkrc")
    assert config.board_theme.background == "transparent"
    assert config.board_theme.indicator == "white"
    assert config.board_theme.sticker_border == g.border
    assert config.board_theme.sticker_text == g.text
    assert config.board_theme.sticker_area == g.area
    assert config.border.top == "heavy"
    assert config.border.sides == "heavy"
    assert config.defaults.width == 30
    assert config.defaults.height == 10
    assert config.defaults.preset == "Graphite"
    assert config.keybindings.new == "n"


def test_load_board_theme_from_toml(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[theme]
background = "black"
indicator = "white"
""", encoding="utf-8")
    config = AppConfig.load(path=rc)
    assert config.board_theme.background == "black"
    assert config.board_theme.indicator == "white"


def test_load_theme_sticker_colors_from_toml(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text(
        """
[theme]
background = "black"
indicator = "white"
border = "#111111"
text = "#222222"
area = "#333333"
""",
        encoding="utf-8",
    )
    config = AppConfig.load(path=rc)
    assert config.board_theme.sticker_border == "#111111"
    assert config.board_theme.sticker_text == "#222222"
    assert config.board_theme.sticker_area == "#333333"


def test_load_border_config_from_toml(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[border]
top = "heavy"
sides = "double"
""", encoding="utf-8")
    config = AppConfig.load(path=rc)
    assert config.border.top == "heavy"
    assert config.border.sides == "double"


def test_load_custom_sticker_presets(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[presets.sticker.Fire]
border = "#ff0000"
text = "#ffffff"
area = "#330000"
""", encoding="utf-8")
    config = AppConfig.load(path=rc)
    assert "Fire" in config.sticker_presets
    assert config.sticker_presets["Fire"].border == "#ff0000"


def test_load_custom_board_presets(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[presets.board.Solarized]
background = "#002b36"
indicator = "#839496"
""", encoding="utf-8")
    config = AppConfig.load(path=rc)
    assert "Solarized" in config.board_presets
    assert config.board_presets["Solarized"].background == "#002b36"


def test_partial_config_uses_defaults(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text('[border]\ntop = "heavy"\n', encoding="utf-8")
    config = AppConfig.load(path=rc)
    assert config.border.top == "heavy"
    assert config.border.sides == "single"  # default
    assert config.board_theme.indicator == "white"  # default


def test_save_board_theme_creates_file(tmp_path):
    from sticker0.presets import STICKER_PRESETS, DEFAULT_STICKER_PRESET

    g = STICKER_PRESETS[DEFAULT_STICKER_PRESET]
    rc = tmp_path / ".stkrc"
    config = AppConfig.load(path=rc)
    config.board_theme = BoardTheme(background="black", indicator="white")
    config.save_board_theme(path=rc)
    assert rc.exists()
    reloaded = AppConfig.load(path=rc)
    assert reloaded.board_theme.background == "black"
    assert reloaded.board_theme.indicator == "white"
    assert reloaded.board_theme.sticker_border == g.border
    assert reloaded.board_theme.sticker_text == g.text
    assert reloaded.board_theme.sticker_area == g.area


def test_save_board_theme_preserves_other_sections(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[border]
top = "heavy"
sides = "double"

[keybindings]
new = "a"
""", encoding="utf-8")
    config = AppConfig.load(path=rc)
    config.board_theme = BoardTheme(background="black", indicator="white")
    config.save_board_theme(path=rc)
    reloaded = AppConfig.load(path=rc)
    assert reloaded.board_theme.background == "black"
    assert reloaded.border.top == "heavy"
    assert reloaded.keybindings.new == "a"


def test_save_board_theme_atomic_write(tmp_path):
    """Atomic write: tmp 파일이 남아있지 않아야 함."""
    rc = tmp_path / ".stkrc"
    rc.write_text('[border]\ntop = "heavy"\n', encoding="utf-8")
    config = AppConfig.load(path=rc)
    config.board_theme = BoardTheme(background="white", indicator="black")
    config.save_board_theme(path=rc)
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert len(tmp_files) == 0
    reloaded = AppConfig.load(path=rc)
    assert reloaded.board_theme.background == "white"


def test_invalid_border_style_uses_default(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text('[border]\ntop = "invalid_style"\n', encoding="utf-8")
    config = AppConfig.load(path=rc)
    # 잘못된 값은 그대로 저장 (유효성 검증은 widget에서)
    assert config.border.top == "invalid_style"
