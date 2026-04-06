# src/sticker0/config.py
from __future__ import annotations
import os
import re
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from sticker0.presets import StickerPreset, BoardThemePreset

CONFIG_PATH = Path.home() / ".stkrc"


@dataclass
class BoardTheme:
    background: str = "transparent"
    indicator: str = "white"


@dataclass
class BorderConfig:
    top: str = "double"
    sides: str = "single"


@dataclass
class DefaultsConfig:
    width: int = 30
    height: int = 10
    preset: str = "Snow"


@dataclass
class KeybindingsConfig:
    new: str = "n"
    delete: str = "d"
    quit: str = "q"


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
        # Border
        if (b := data.get("border")) is not None:
            config.border.top = b.get("top", "double")
            config.border.sides = b.get("sides", "single")
        # Defaults
        if (d := data.get("defaults")) is not None:
            config.defaults.width = d.get("width", 30)
            config.defaults.height = d.get("height", 10)
            config.defaults.preset = d.get("preset", "Snow")
        # Keybindings
        if (kb := data.get("keybindings")) is not None:
            config.keybindings.new = kb.get("new", "n")
            config.keybindings.delete = kb.get("delete", "d")
            config.keybindings.quit = kb.get("quit", "q")
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
        """보드 테마를 .stkrc [theme] 섹션에 atomic write."""
        theme_lines = (
            "[theme]\n"
            f'background = "{self.board_theme.background}"\n'
            f'indicator = "{self.board_theme.indicator}"\n'
        )
        if path.exists():
            content = path.read_text(encoding="utf-8")
            # [theme] 섹션 찾기 및 교체
            pattern = r"\[theme\]\n(?:[^\[]*?)(?=\n\[|\Z)"
            if re.search(pattern, content):
                content = re.sub(pattern, theme_lines.rstrip(), content)
            else:
                content = content.rstrip() + "\n\n" + theme_lines
        else:
            content = theme_lines
        # Atomic write
        fd, tmp_path_str = tempfile.mkstemp(
            dir=path.parent, suffix=".tmp"
        )
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
