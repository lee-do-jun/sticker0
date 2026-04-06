# src/sticker0/widgets/picker_labels.py
"""프리셋/테마 피커: 이름 한 줄(Rich 굵게), 행 배경·글자색은 PrimaryOnlyButton에 위임."""
from __future__ import annotations

from rich.style import Style
from rich.text import Text

from sticker0.presets import BoardThemePreset, StickerPreset

_NO_STYLE_COLOR = frozenset({"", "transparent", "inherit", "default"})


def sticker_preset_picker_label(preset: StickerPreset) -> Text:
    return Text(preset.name, style=Style(bold=True))


def board_theme_picker_label(preset: BoardThemePreset) -> Text:
    return Text(preset.name, style=Style(bold=True))


def resolve_sticker_picker_idle(
    preset: StickerPreset,
    board_background: str,
    board_indicator: str,
) -> tuple[str, str]:
    """행 기본 배경(area)·글자색(text), 투명/상속은 보드 테마로 대체."""
    area = preset.area
    if not area or area in _NO_STYLE_COLOR:
        bg = board_background
    else:
        bg = area

    text = preset.text
    if not text or text in _NO_STYLE_COLOR:
        fg = board_indicator
    else:
        fg = text
    return bg, fg


def resolve_board_theme_picker_idle(
    preset: BoardThemePreset,
    board_background: str,
    board_indicator: str,
) -> tuple[str, str]:
    """행 기본 배경(background)·글자색(indicator)."""
    bg = preset.background
    if not bg or bg in _NO_STYLE_COLOR:
        bg = board_background

    ind = preset.indicator
    if not ind or ind in _NO_STYLE_COLOR:
        fg = board_indicator
    else:
        fg = ind
    return bg, fg
