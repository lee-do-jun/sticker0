# tests/test_config.py
import pytest
from pathlib import Path
from sticker0.config import AppConfig
from sticker0.sticker import StickerColor, BorderType


def test_defaults_when_no_file(tmp_path):
    config = AppConfig.load(path=tmp_path / ".stkrc")
    assert config.theme.default_color == StickerColor.YELLOW
    assert config.border.type == BorderType.ROUNDED
    assert config.defaults.width == 30
    assert config.defaults.height == 10
    assert config.keybindings.new == "n"
    assert config.keybindings.delete == "d"
    assert config.keybindings.quit == "q"


def test_load_from_toml(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[theme]
default_color = "blue"

[border]
type = "double"

[defaults]
width = 40
height = 15

[keybindings]
new = "a"
delete = "x"
quit = "ctrl+q"
""", encoding="utf-8")
    config = AppConfig.load(path=rc)
    assert config.theme.default_color == StickerColor.BLUE
    assert config.border.type == BorderType.DOUBLE
    assert config.defaults.width == 40
    assert config.defaults.height == 15
    assert config.keybindings.new == "a"
    assert config.keybindings.delete == "x"
    assert config.keybindings.quit == "ctrl+q"


def test_partial_config_uses_defaults(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text('[theme]\ndefault_color = "green"\n', encoding="utf-8")
    config = AppConfig.load(path=rc)
    assert config.theme.default_color == StickerColor.GREEN
    assert config.border.type == BorderType.ROUNDED  # default
