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
    "Clear": StickerPreset("Clear", "white", "white", "transparent"),
    "Graphite": StickerPreset("Graphite", "#d4d4d8", "#d4d4d8", "#2a2a2e"),
    "Mist": StickerPreset("Mist", "#2f2f2f", "#2f2f2f", "#f2f2f0"),
    "Ocean": StickerPreset("Ocean", "#dbeafe", "#dbeafe", "#1e3a5f"),
    "Amber": StickerPreset("Amber", "#3a2e05", "#3a2e05", "#f6d96b"),
    "Forest": StickerPreset("Forest", "#d1fae5", "#d1fae5", "#1f3d2b"),
    "Crimson": StickerPreset("Crimson", "#ffe4e6", "#ffe4e6", "#5a1e24"),
    "Violet": StickerPreset("Violet", "#ede9fe", "#ede9fe", "#3b2f5a"),
    "Sky": StickerPreset("Sky", "white", "white", "#1565c0"),
    "Banana": StickerPreset("Banana", "black", "black", "#ffeb3b"),
}

BOARD_PRESETS: dict[str, BoardThemePreset] = {
    "Graphite": BoardThemePreset("Graphite", "#1e1e22", "#d4d4d8"),
    "Ivory": BoardThemePreset("Ivory", "#f5f3ef", "#2f2f2f"),
    "Slate": BoardThemePreset("Slate", "#2a2f45", "#cbd5ff"),
    "Dust": BoardThemePreset("Dust", "#f2e9e4", "#5c3a3a"),
    "Forest": BoardThemePreset("Forest", "#1f2a24", "#c7e7d3"),
    "Amber": BoardThemePreset("Amber", "#2b2418", "#ffcf99"),
}

DEFAULT_STICKER_PRESET = "Clear"
DEFAULT_BOARD_PRESET = "Slate"


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
