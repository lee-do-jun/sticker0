# src/sticker0/widgets/sticker_widget.py
from __future__ import annotations
import time
from textual.widget import Widget
from textual.widgets import Static, TextArea
from textual.app import ComposeResult
from textual.events import MouseDown, MouseMove, MouseUp, Click
from sticker0.sticker import Sticker, StickerColor, BorderType

COLOR_MAP: dict[StickerColor, tuple[str, str]] = {
    StickerColor.YELLOW: ("#000000", "#ffeb3b"),
    StickerColor.BLUE:   ("#ffffff", "#1565c0"),
    StickerColor.GREEN:  ("#000000", "#4caf50"),
    StickerColor.PINK:   ("#000000", "#f48fb1"),
    StickerColor.WHITE:  ("#000000", "#ffffff"),
    StickerColor.DARK:   ("#ffffff", "#212121"),
}

BORDER_MAP: dict[BorderType, str] = {
    BorderType.ROUNDED: "round",
    BorderType.SHARP:   "solid",
    BorderType.DOUBLE:  "double",
    BorderType.THICK:   "heavy",
    BorderType.ASCII:   "ascii",
}


class StickerWidget(Widget):
    DEFAULT_CSS = """
    StickerWidget {
        position: absolute;
        padding: 0 1;
        min-width: 20;
        min-height: 5;
    }
    StickerWidget .sticker-title {
        text-style: bold;
        height: 1;
    }
    StickerWidget .sticker-content {
        height: 1fr;
    }
    """

    can_focus = True

    def __init__(self, sticker: Sticker, **kwargs) -> None:
        super().__init__(**kwargs)
        self.sticker = sticker
        self._drag_start: tuple[int, int] | None = None
        self._drag_origin: tuple[int, int] = (0, 0)
        self._resizing: bool = False
        self._last_click: float = 0.0
        self._editing: bool = False

    def on_mount(self) -> None:
        self._apply_sticker_styles()

    def _apply_sticker_styles(self) -> None:
        text_color, bg_color = COLOR_MAP.get(
            self.sticker.color, COLOR_MAP[StickerColor.YELLOW]
        )
        border_style = BORDER_MAP.get(self.sticker.border, "round")
        self.styles.background = bg_color
        self.styles.color = text_color
        self.styles.border = (border_style, text_color)
        self.styles.offset = (self.sticker.position.x, self.sticker.position.y)
        self.styles.width = self.sticker.size.width
        self.styles.height = self.sticker.size.height

    def compose(self) -> ComposeResult:
        title = self.sticker.title or "📌 메모"
        yield Static(title, classes="sticker-title")
        yield Static(self.sticker.content, classes="sticker-content")

    def refresh_display(self) -> None:
        """스티커 데이터 변경 후 화면 갱신."""
        self._apply_sticker_styles()
        self.query_one(".sticker-title", Static).update(
            self.sticker.title or "📌 메모"
        )
        self.query_one(".sticker-content", Static).update(self.sticker.content)
