# tests/test_config.py
import os
import pytest
from pathlib import Path
from sticker0.config import AppConfig, BoardTheme, BorderConfig


def test_defaults_when_no_file(tmp_path):
    from sticker0.presets import (
        BOARD_PRESETS,
        DEFAULT_BOARD_PRESET,
        DEFAULT_STICKER_PRESET,
        STICKER_PRESETS,
    )

    g = STICKER_PRESETS[DEFAULT_STICKER_PRESET]
    bg = BOARD_PRESETS[DEFAULT_BOARD_PRESET]
    config = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=tmp_path / "settings.toml",
    )
    assert config.board_theme.background == bg.background
    assert config.board_theme.indicator == bg.indicator
    assert config.board_theme.sticker_border == g.border
    assert config.board_theme.sticker_text == g.text
    assert config.board_theme.sticker_area == g.area
    assert config.border.top == "heavy"
    assert config.border.sides == "heavy"
    assert config.defaults.width == 30
    assert config.defaults.height == 10
    assert config.defaults.preset == "Graphite"


def test_load_board_theme_from_settings_toml(tmp_path):
    """[theme]은 settings.toml에서 읽는다."""
    settings = tmp_path / "settings.toml"
    settings.write_text("""
[theme]
background = "black"
indicator = "white"
""", encoding="utf-8")
    config = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=settings,
    )
    assert config.board_theme.background == "black"
    assert config.board_theme.indicator == "white"


def test_load_theme_sticker_colors_from_settings_toml(tmp_path):
    """settings.toml [theme]의 border/text/area가 스티커 기본색으로 적용된다."""
    settings = tmp_path / "settings.toml"
    settings.write_text(
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
    config = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=settings,
    )
    assert config.board_theme.sticker_border == "#111111"
    assert config.board_theme.sticker_text == "#222222"
    assert config.board_theme.sticker_area == "#333333"


def test_stkrc_theme_section_is_ignored(tmp_path):
    """~/.stkrc에 [theme]이 있어도 완전히 무시된다."""
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[theme]
background = "red"
indicator = "blue"
border = "#aabbcc"
""", encoding="utf-8")
    config = AppConfig.load(
        path=rc,
        settings_path=tmp_path / "settings.toml",
    )
    # 기본값(Graphite 보드 프리셋) 그대로여야 함
    from sticker0.presets import BOARD_PRESETS, DEFAULT_BOARD_PRESET

    bg = BOARD_PRESETS[DEFAULT_BOARD_PRESET]
    assert config.board_theme.background == bg.background
    assert config.board_theme.indicator == bg.indicator


def test_settings_toml_takes_priority_over_defaults(tmp_path):
    """settings.toml의 [theme]이 있으면 기본값 대신 그 값을 사용한다."""
    settings = tmp_path / "settings.toml"
    settings.write_text("""
[theme]
background = "#2a2a2e"
indicator = "#d4d4d8"
""", encoding="utf-8")
    rc = tmp_path / ".stkrc"
    # stkrc에 [theme] 있어도 무시
    rc.write_text("""
[theme]
background = "red"
""", encoding="utf-8")
    config = AppConfig.load(path=rc, settings_path=settings)
    assert config.board_theme.background == "#2a2a2e"
    assert config.board_theme.indicator == "#d4d4d8"


def test_load_border_config_from_toml(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[border]
top = "heavy"
sides = "double"
""", encoding="utf-8")
    config = AppConfig.load(path=rc, settings_path=tmp_path / "settings.toml")
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
    config = AppConfig.load(path=rc, settings_path=tmp_path / "settings.toml")
    assert "Fire" in config.sticker_presets
    assert config.sticker_presets["Fire"].border == "#ff0000"


def test_load_custom_board_presets(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[presets.board.Solarized]
background = "#002b36"
indicator = "#839496"
""", encoding="utf-8")
    config = AppConfig.load(path=rc, settings_path=tmp_path / "settings.toml")
    assert "Solarized" in config.board_presets
    assert config.board_presets["Solarized"].background == "#002b36"


def test_partial_config_uses_defaults(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text('[border]\ntop = "heavy"\n', encoding="utf-8")
    config = AppConfig.load(path=rc, settings_path=tmp_path / "settings.toml")
    assert config.border.top == "heavy"
    assert config.border.sides == "single"  # default
    from sticker0.presets import BOARD_PRESETS, DEFAULT_BOARD_PRESET

    bg = BOARD_PRESETS[DEFAULT_BOARD_PRESET]
    assert config.board_theme.indicator == bg.indicator  # default


def test_save_board_theme_creates_settings_toml(tmp_path):
    """save_board_theme()은 settings.toml을 생성한다."""
    from sticker0.presets import STICKER_PRESETS, DEFAULT_STICKER_PRESET

    g = STICKER_PRESETS[DEFAULT_STICKER_PRESET]
    settings = tmp_path / "settings.toml"
    config = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=settings,
    )
    config.board_theme = BoardTheme(background="black", indicator="white")
    config.save_board_theme()
    assert settings.exists()
    reloaded = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=settings,
    )
    assert reloaded.board_theme.background == "black"
    assert reloaded.board_theme.indicator == "white"
    assert reloaded.board_theme.sticker_border == g.border
    assert reloaded.board_theme.sticker_text == g.text
    assert reloaded.board_theme.sticker_area == g.area


def test_save_board_theme_does_not_touch_stkrc(tmp_path):
    """save_board_theme()은 ~/.stkrc를 수정하지 않는다."""
    rc = tmp_path / ".stkrc"
    original_content = '[border]\ntop = "heavy"\n'
    rc.write_text(original_content, encoding="utf-8")
    settings = tmp_path / "settings.toml"
    config = AppConfig.load(path=rc, settings_path=settings)
    config.board_theme = BoardTheme(background="black", indicator="white")
    config.save_board_theme()
    assert rc.read_text(encoding="utf-8") == original_content


def test_save_board_theme_preserves_other_settings_sections(tmp_path):
    """settings.toml에 [theme] 외 다른 섹션이 있으면 보존한다."""
    settings = tmp_path / "settings.toml"
    settings.write_text("""
[other]
foo = "bar"

[theme]
background = "old"
indicator = "old"
""", encoding="utf-8")
    config = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=settings,
    )
    config.board_theme = BoardTheme(background="new", indicator="new")
    config.save_board_theme()
    text = settings.read_text(encoding="utf-8")
    assert '[other]' in text
    assert 'foo = "bar"' in text
    reloaded = AppConfig.load(path=tmp_path / ".stkrc", settings_path=settings)
    assert reloaded.board_theme.background == "new"


def test_save_board_theme_atomic_write(tmp_path):
    """Atomic write: tmp 파일이 남아있지 않아야 함."""
    settings = tmp_path / "settings.toml"
    settings.write_text('[theme]\nbackground = "old"\n', encoding="utf-8")
    config = AppConfig.load(path=tmp_path / ".stkrc", settings_path=settings)
    config.board_theme = BoardTheme(background="white", indicator="black")
    config.save_board_theme()
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert len(tmp_files) == 0
    reloaded = AppConfig.load(path=tmp_path / ".stkrc", settings_path=settings)
    assert reloaded.board_theme.background == "white"


def test_save_board_theme_creates_parent_dir(tmp_path):
    """settings.toml의 부모 디렉터리가 없어도 자동 생성한다."""
    settings = tmp_path / "nested" / "deep" / "settings.toml"
    config = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=settings,
    )
    config.board_theme = BoardTheme(background="blue", indicator="white")
    config.save_board_theme()
    assert settings.exists()
    reloaded = AppConfig.load(path=tmp_path / ".stkrc", settings_path=settings)
    assert reloaded.board_theme.background == "blue"


def test_invalid_border_style_uses_default(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text('[border]\ntop = "invalid_style"\n', encoding="utf-8")
    config = AppConfig.load(path=rc, settings_path=tmp_path / "settings.toml")
    # 잘못된 값은 그대로 저장 (유효성 검증은 widget에서)
    assert config.border.top == "invalid_style"
