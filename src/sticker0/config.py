# src/sticker0/config.py
from __future__ import annotations
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from sticker0.sticker import StickerColor, BorderType

CONFIG_PATH = Path.home() / ".stkrc"


@dataclass
class ThemeConfig:
    default_color: StickerColor = StickerColor.YELLOW


@dataclass
class BorderConfig:
    type: BorderType = BorderType.ROUNDED


@dataclass
class DefaultsConfig:
    width: int = 30
    height: int = 10


@dataclass
class KeybindingsConfig:
    new: str = "n"
    delete: str = "d"
    quit: str = "q"


@dataclass
class AppConfig:
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    border: BorderConfig = field(default_factory=BorderConfig)
    defaults: DefaultsConfig = field(default_factory=DefaultsConfig)
    keybindings: KeybindingsConfig = field(default_factory=KeybindingsConfig)

    @classmethod
    def load(cls, path: Path = CONFIG_PATH) -> AppConfig:
        if not path.exists():
            return cls()
        with open(path, "rb") as f:
            data = tomllib.load(f)
        config = cls()
        if t := data.get("theme"):
            if v := t.get("default_color"):
                config.theme.default_color = StickerColor(v)
        if b := data.get("border"):
            if v := b.get("type"):
                config.border.type = BorderType(v)
        if d := data.get("defaults"):
            config.defaults.width = d.get("width", 30)
            config.defaults.height = d.get("height", 10)
        if kb := data.get("keybindings"):
            config.keybindings.new = kb.get("new", "n")
            config.keybindings.delete = kb.get("delete", "d")
            config.keybindings.quit = kb.get("quit", "q")
        return config
