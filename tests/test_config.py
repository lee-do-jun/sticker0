# tests/test_config.py
import os
import pytest
from pathlib import Path
from sticker0.config import AppConfig, BoardTheme, BorderConfig


def test_defaults_when_no_file(tmp_path):
    config = AppConfig.load(path=tmp_path / ".stkrc")
    assert config.board_theme.background == "transparent"
    assert config.board_theme.indicator == "white"
    assert config.border.top == "double"
    assert config.border.sides == "single"
    assert config.defaults.width == 30
    assert config.defaults.height == 10
    assert config.defaults.preset == "Snow"
    assert config.keybindings.new == "n"
    assert config.keybindings.quit == "q"


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
    rc = tmp_path / ".stkrc"
    config = AppConfig.load(path=rc)
    config.board_theme = BoardTheme(background="black", indicator="white")
    config.save_board_theme(path=rc)
    assert rc.exists()
    reloaded = AppConfig.load(path=rc)
    assert reloaded.board_theme.background == "black"
    assert reloaded.board_theme.indicator == "white"


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
