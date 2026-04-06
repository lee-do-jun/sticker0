# src/sticker0/config.py
from __future__ import annotations
import os
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from sticker0.presets import (
    BOARD_PRESETS,
    STICKER_PRESETS,
    BoardThemePreset,
    DEFAULT_BOARD_PRESET,
    DEFAULT_STICKER_PRESET,
    StickerPreset,
)
from sticker0.sticker import DEFAULT_BORDER_LINE

CONFIG_PATH = Path.home() / ".stkrc"
SETTINGS_PATH = Path.home() / ".local" / "share" / "sticker0" / "settings.toml"

_G_THEME_STICKER = STICKER_PRESETS[DEFAULT_STICKER_PRESET]
_G_THEME_BOARD = BOARD_PRESETS[DEFAULT_BOARD_PRESET]


def _replace_toml_section(content: str, section: str, new_block: str) -> str:
    """content에서 [section] 블록을 new_block으로 교체. 없으면 끝에 추가."""
    lines = content.split("\n")
    result: list[str] = []
    in_target = False
    found = False
    for line in lines:
        stripped = line.strip()
        if stripped == f"[{section}]":
            in_target = True
            found = True
            result.extend(new_block.rstrip("\n").split("\n"))
            continue
        if in_target and stripped.startswith("[") and not stripped.startswith(f"[{section}]"):
            in_target = False
        if not in_target:
            result.append(line)
    if not found:
        if result and result[-1] != "":
            result.append("")
        result.extend(new_block.rstrip("\n").split("\n"))
    return "\n".join(result)


@dataclass
class BoardTheme:
    """보드 배경/강조색 + 새 스티커 기본 색·라인. settings.toml [theme]에 저장."""
    background: str = _G_THEME_BOARD.background
    indicator: str = _G_THEME_BOARD.indicator
    sticker_border: str = _G_THEME_STICKER.border
    sticker_text: str = _G_THEME_STICKER.text
    sticker_area: str = _G_THEME_STICKER.area
    sticker_line: str = DEFAULT_BORDER_LINE


@dataclass
class DefaultsConfig:
    width: int = 30
    height: int = 10
    preset: str = "Graphite"


@dataclass
class AppConfig:
    board_theme: BoardTheme = field(default_factory=BoardTheme)
    defaults: DefaultsConfig = field(default_factory=DefaultsConfig)
    sticker_presets: dict[str, StickerPreset] = field(default_factory=dict)
    board_presets: dict[str, BoardThemePreset] = field(default_factory=dict)

    @classmethod
    def load(
        cls,
        path: Path = CONFIG_PATH,
        settings_path: Path = SETTINGS_PATH,
    ) -> AppConfig:
        config = cls()
        config._settings_path = settings_path

        if path.exists():
            with open(path, "rb") as f:
                data = tomllib.load(f)
            if (d := data.get("defaults")) is not None:
                config.defaults.width = d.get("width", 30)
                config.defaults.height = d.get("height", 10)
                config.defaults.preset = d.get("preset", "Graphite")
            presets_data = data.get("presets", {})
            if (sp := presets_data.get("sticker")) is not None:
                for name, vals in sp.items():
                    config.sticker_presets[name] = StickerPreset(
                        name=name,
                        border=vals.get("border", "white"),
                        text=vals.get("text", "white"),
                        area=vals.get("area", "transparent"),
                    )
            if (bp := presets_data.get("board")) is not None:
                for name, vals in bp.items():
                    config.board_presets[name] = BoardThemePreset(
                        name=name,
                        background=vals.get("background", "transparent"),
                        indicator=vals.get("indicator", "white"),
                    )

        if settings_path.exists():
            with open(settings_path, "rb") as f:
                sdata = tomllib.load(f)
            if (t := sdata.get("theme")) is not None:
                config.board_theme.background = t.get("background", _G_THEME_BOARD.background)
                config.board_theme.indicator = t.get("indicator", _G_THEME_BOARD.indicator)
                config.board_theme.sticker_border = t.get("border", _G_THEME_STICKER.border)
                config.board_theme.sticker_text = t.get("text", _G_THEME_STICKER.text)
                config.board_theme.sticker_area = t.get("area", _G_THEME_STICKER.area)
                config.board_theme.sticker_line = t.get("line", DEFAULT_BORDER_LINE)

        return config

    def save_board_theme(self, path: Path | None = None) -> None:
        actual_path = path if path is not None else getattr(self, "_settings_path", SETTINGS_PATH)
        actual_path.parent.mkdir(parents=True, exist_ok=True)
        bt = self.board_theme
        theme_block = (
            "[theme]\n"
            f'background = "{bt.background}"\n'
            f'indicator = "{bt.indicator}"\n'
            f'border = "{bt.sticker_border}"\n'
            f'text = "{bt.sticker_text}"\n'
            f'area = "{bt.sticker_area}"\n'
            f'line = "{bt.sticker_line}"\n'
        )
        if actual_path.exists():
            content = _replace_toml_section(
                actual_path.read_text(encoding="utf-8"), "theme", theme_block
            )
        else:
            content = theme_block
        fd, tmp_path_str = tempfile.mkstemp(dir=actual_path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path_str, str(actual_path))
        except BaseException:
            try:
                os.unlink(tmp_path_str)
            except OSError:
                pass
            raise
