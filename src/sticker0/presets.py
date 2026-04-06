# src/sticker0/presets.py
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class StickerPreset:
    name: str
    border: str
    text: str
    area: str


@dataclass(frozen=True)
class BoardThemePreset:
    name: str
    background: str
    indicator: str


STICKER_PRESETS: dict[str, StickerPreset] = {
    "Snow": StickerPreset("Snow", "white", "white", "transparent"),
    "Ink": StickerPreset("Ink", "black", "black", "transparent"),
    "Sky": StickerPreset("Sky", "white", "white", "#1565c0"),
    "Banana": StickerPreset("Banana", "black", "black", "#ffeb3b"),
}

BOARD_PRESETS: dict[str, BoardThemePreset] = {
    "Dark Base": BoardThemePreset("Dark Base", "black", "white"),
    "Light Base": BoardThemePreset("Light Base", "white", "black"),
    "Dark Mode": BoardThemePreset("Dark Mode", "transparent", "white"),
    "White Mode": BoardThemePreset("White Mode", "transparent", "black"),
}

DEFAULT_STICKER_PRESET = "Snow"
DEFAULT_BOARD_PRESET = "Dark Mode"


def get_sticker_preset(
    name: str,
    custom: dict[str, StickerPreset] | None = None,
) -> StickerPreset | None:
    if custom and name in custom:
        return custom[name]
    return STICKER_PRESETS.get(name)


def get_board_preset(
    name: str,
    custom: dict[str, BoardThemePreset] | None = None,
) -> BoardThemePreset | None:
    if custom and name in custom:
        return custom[name]
    return BOARD_PRESETS.get(name)
