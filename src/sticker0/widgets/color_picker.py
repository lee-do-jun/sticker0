# src/sticker0/widgets/color_picker.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Button
from textual.message import Message
from sticker0.sticker import StickerColor

COLOR_LABELS: dict[StickerColor, str] = {
    StickerColor.YELLOW: "🟡 노랑",
    StickerColor.BLUE:   "🔵 파랑",
    StickerColor.GREEN:  "🟢 초록",
    StickerColor.PINK:   "🩷 분홍",
    StickerColor.WHITE:  "⬜ 흰색",
    StickerColor.DARK:   "⬛ 어두움",
}


class ColorPicker(Widget):
    """색상 선택 팝업."""

    DEFAULT_CSS = """
    ColorPicker {
        position: absolute;
        width: 20;
        height: auto;
        border: round $accent;
        background: $surface;
        layer: menu;
    }
    ColorPicker Button {
        width: 1fr;
        height: 1;
        border: none;
        background: transparent;
    }
    ColorPicker Button:hover {
        background: $accent 20%;
    }
    """

    class ColorSelected(Message):
        def __init__(self, sticker_id: str, color: StickerColor) -> None:
            super().__init__()
            self.sticker_id = sticker_id
            self.color = color

    def __init__(self, sticker_id: str, x: int, y: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.sticker_id = sticker_id
        self._picker_x = x
        self._picker_y = y

    def on_mount(self) -> None:
        self.styles.offset = (self._picker_x, self._picker_y)

    def compose(self) -> ComposeResult:
        for color, label in COLOR_LABELS.items():
            yield Button(label, id=f"color-{color.value}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        color_value = (event.button.id or "").removeprefix("color-")
        try:
            color = StickerColor(color_value)
            self.post_message(self.ColorSelected(self.sticker_id, color))
        except ValueError:
            pass
        self.remove()
