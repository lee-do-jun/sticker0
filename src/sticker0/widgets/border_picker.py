# src/sticker0/widgets/border_picker.py
from __future__ import annotations
from rich.style import Style
from rich.text import Text
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Button
from textual.message import Message
from sticker0.sticker import BORDER_STYLES
from sticker0.widgets.menu_button import PrimaryOnlyButton
from sticker0.widgets.popup_geometry import (
    apply_clamp_popup_to_parent,
    apply_popup_board_theme,
)

# 터미널에서 스타일을 한눈에 구분하기 위한 미리보기 (박스드로잉·블록 문자)
_BORDER_PICKER_PREVIEW: dict[str, str] = {
    "solid": "┌──┐",
    "heavy": "┏━━┓",
    "round": "╭──╮",
    "double": "╔══╗",
    "ascii": "+--+",
    "inner": "▗▄▄▖",
    "outer": "▛▀▀▜",
    "dashed": "┏╍╍┓",
}


def _border_picker_label(style_name: str) -> Text:
    """한 줄: `╭──╮  Round` 형식 — 미리보기 + 두 칸 공백 + 굵은 이름."""
    preview = _BORDER_PICKER_PREVIEW.get(style_name, "────")
    name = style_name.capitalize()
    t = Text()
    t.append(preview)
    t.append("  ")
    t.append(name, style=Style(bold=True))
    return t


class BorderPicker(Widget):
    """스티커 border 스타일 선택 팝업."""

    DEFAULT_CSS = """
    BorderPicker {
        position: absolute;
        width: 20;
        height: auto;
        background: transparent;
        layer: menu;
    }
    BorderPicker Button {
        width: 1fr;
        height: auto;
        min-height: 1;
        border: none;
        background: transparent;
        text-align: left;
        content-align: left middle;
    }
    """

    class BorderSelected(Message):
        def __init__(self, sticker_id: str, line: str) -> None:
            super().__init__()
            self.sticker_id = sticker_id
            self.line = line

    def __init__(
        self,
        sticker_id: str,
        x: int,
        y: int,
        indicator: str = "white",
        board_background: str = "transparent",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.sticker_id = sticker_id
        self._x = x
        self._y = y
        self._indicator = indicator
        self._board_background = board_background

    def on_mount(self) -> None:
        self.styles.offset = (self._x, self._y)
        self.styles.border = ("round", self._indicator)
        apply_popup_board_theme(self, self._board_background, self._indicator)
        self.call_after_refresh(self._clamp_to_parent)

    def _clamp_to_parent(self) -> None:
        apply_clamp_popup_to_parent(self)

    def compose(self) -> ComposeResult:
        mi, mb = self._indicator, self._board_background
        for style_name in BORDER_STYLES:
            label = _border_picker_label(style_name)
            yield PrimaryOnlyButton(
                label,
                id=f"border-{style_name}",
                menu_indicator=mi,
                menu_panel_bg=mb,
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        style_name = (event.button.id or "").removeprefix("border-")
        if style_name in BORDER_STYLES:
            self.post_message(self.BorderSelected(self.sticker_id, style_name))
        self.remove()
