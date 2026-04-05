# tests/test_config.py
import pytest
from pathlib import Path
from sticker0.config import AppConfig
from sticker0.sticker import StickerColor, BorderType


def test_defaults_when_no_file(tmp_path):
    config = AppConfig.load(path=tmp_path / ".stkrc")
    assert config.theme.default_color == StickerColor.YELLOW
    assert config.border.border_type == BorderType.ROUNDED
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
    assert config.border.border_type == BorderType.DOUBLE
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
    assert config.border.border_type == BorderType.ROUNDED  # default


def test_invalid_enum_raises_value_error(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text('[theme]\ndefault_color = "invalid"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid default_color"):
        AppConfig.load(path=rc)


def test_invalid_border_type_raises_value_error(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text('[border]\ntype = "hexagon"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid border type"):
        AppConfig.load(path=rc)
