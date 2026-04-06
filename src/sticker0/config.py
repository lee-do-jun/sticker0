# src/sticker0/config.py
from __future__ import annotations
import os
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from sticker0.presets import (
    STICKER_PRESETS,
    BoardThemePreset,
    DEFAULT_STICKER_PRESET,
    StickerPreset,
)

CONFIG_PATH = Path.home() / ".stkrc"

_G_THEME_STICKER = STICKER_PRESETS[DEFAULT_STICKER_PRESET]


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
            # 새 블록 삽입 (trailing newline 제거 후)
            result.extend(new_block.rstrip("\n").split("\n"))
            continue
        if in_target and stripped.startswith("[") and not stripped.startswith(f"[{section}]"):
            in_target = False
        if not in_target:
            result.append(line)
    if not found:
        # 파일 끝에 추가
        if result and result[-1] != "":
            result.append("")
        result.extend(new_block.rstrip("\n").split("\n"))
    return "\n".join(result)


@dataclass
class BoardTheme:
    """[theme]: 보드 배경/강조색 + 새 스티커 기본 색(border/text/area)."""

    background: str = "transparent"
    indicator: str = "white"
    sticker_border: str = _G_THEME_STICKER.border
    sticker_text: str = _G_THEME_STICKER.text
    sticker_area: str = _G_THEME_STICKER.area


@dataclass
class BorderConfig:
    top: str = "heavy"
    sides: str = "heavy"


@dataclass
class DefaultsConfig:
    width: int = 30
    height: int = 10
    preset: str = "Graphite"


@dataclass
class KeybindingsConfig:
    new: str = "n"


@dataclass
class AppConfig:
    board_theme: BoardTheme = field(default_factory=BoardTheme)
    border: BorderConfig = field(default_factory=BorderConfig)
    defaults: DefaultsConfig = field(default_factory=DefaultsConfig)
    keybindings: KeybindingsConfig = field(default_factory=KeybindingsConfig)
    sticker_presets: dict[str, StickerPreset] = field(default_factory=dict)
    board_presets: dict[str, BoardThemePreset] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path = CONFIG_PATH) -> AppConfig:
        if not path.exists():
            return cls()
        with open(path, "rb") as f:
            data = tomllib.load(f)
        config = cls()
        # Board theme
        if (t := data.get("theme")) is not None:
            config.board_theme.background = t.get("background", "transparent")
            config.board_theme.indicator = t.get("indicator", "white")
            config.board_theme.sticker_border = t.get(
                "border", _G_THEME_STICKER.border
            )
            config.board_theme.sticker_text = t.get("text", _G_THEME_STICKER.text)
            config.board_theme.sticker_area = t.get("area", _G_THEME_STICKER.area)
        # Border
        if (b := data.get("border")) is not None:
            config.border.top = b.get("top", "double")
            config.border.sides = b.get("sides", "single")
        # Defaults
        if (d := data.get("defaults")) is not None:
            config.defaults.width = d.get("width", 30)
            config.defaults.height = d.get("height", 10)
            config.defaults.preset = d.get("preset", "Graphite")
        # Keybindings
        if (kb := data.get("keybindings")) is not None:
            config.keybindings.new = kb.get("new", "n")
        # Custom presets
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
        return config

    def save_board_theme(self, path: Path = CONFIG_PATH) -> None:
        """[theme] 섹션에 보드 배경/indicator와 새 스티커 기본 색을 atomic write."""
        bt = self.board_theme
        theme_block = (
            "[theme]\n"
            f'background = "{bt.background}"\n'
            f'indicator = "{bt.indicator}"\n'
            f'border = "{bt.sticker_border}"\n'
            f'text = "{bt.sticker_text}"\n'
            f'area = "{bt.sticker_area}"\n'
        )
        if path.exists():
            content = _replace_toml_section(
                path.read_text(encoding="utf-8"), "theme", theme_block
            )
        else:
            content = theme_block
        # Atomic write
        fd, tmp_path_str = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path_str, str(path))
        except BaseException:
            try:
                os.unlink(tmp_path_str)
            except OSError:
                pass
            raise
