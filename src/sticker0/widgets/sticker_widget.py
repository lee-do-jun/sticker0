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

    MIN_WIDTH = 20
    MIN_HEIGHT = 5
    DOUBLE_CLICK_INTERVAL = 0.4

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

    def _is_resize_handle(self, x: int, y: int) -> bool:
        """우하단 모서리(2x2 영역) 클릭 여부."""
        w = self.sticker.size.width
        h = self.sticker.size.height
        return x >= w - 2 and y >= h - 2

    def on_mouse_down(self, event: MouseDown) -> None:
        event.stop()
        self._drag_start = (event.screen_x, event.screen_y)
        if self._is_resize_handle(event.x, event.y):
            self._resizing = True
            self._drag_origin = (self.sticker.size.width, self.sticker.size.height)
        else:
            self._resizing = False
            self._drag_origin = (self.sticker.position.x, self.sticker.position.y)
        self.capture_mouse()

    def _apply_drag(self, dx: int, dy: int) -> None:
        """드래그 델타를 적용하여 리사이즈 또는 이동 상태를 업데이트."""
        if self._resizing:
            new_w = max(self.MIN_WIDTH, self._drag_origin[0] + dx)
            new_h = max(self.MIN_HEIGHT, self._drag_origin[1] + dy)
            self.sticker.size.width = new_w
            self.sticker.size.height = new_h
            self.styles.width = new_w
            self.styles.height = new_h
        else:
            new_x = max(0, self._drag_origin[0] + dx)
            new_y = max(0, self._drag_origin[1] + dy)
            self.sticker.position.x = new_x
            self.sticker.position.y = new_y
            self.styles.offset = (new_x, new_y)

    def on_mouse_move(self, event: MouseMove) -> None:
        if self._drag_start is None:
            return
        event.stop()
        dx = event.screen_x - self._drag_start[0]
        dy = event.screen_y - self._drag_start[1]
        self._apply_drag(dx, dy)

    def on_mouse_up(self, event: MouseUp) -> None:
        if self._drag_start is not None:
            dx = event.screen_x - self._drag_start[0]
            dy = event.screen_y - self._drag_start[1]
            self._apply_drag(dx, dy)
            self._drag_start = None
            self.release_mouse()
            board = self.app.query_one("StickerBoard")
            board.save_sticker(self.sticker)

    def refresh_display(self) -> None:
        """스티커 데이터 변경 후 화면 갱신."""
        self._apply_sticker_styles()
        self.query_one(".sticker-title", Static).update(
            self.sticker.title or "📌 메모"
        )
        self.query_one(".sticker-content", Static).update(self.sticker.content)

    def on_click(self, event: Click) -> None:
        now = time.monotonic()
        if now - self._last_click < self.DOUBLE_CLICK_INTERVAL:
            self._enter_edit_mode()
            event.stop()
        self._last_click = now

    def _enter_edit_mode(self) -> None:
        if self._editing:
            return
        self._editing = True
        try:
            content_widget = self.query_one(".sticker-content", Static)
            content_widget.remove()
        except Exception:
            pass
        editor_id = f"sticker-editor-{self.sticker.id}"
        editor = TextArea(
            self.sticker.content,
            classes="sticker-content",
            id=editor_id,
        )
        self.mount(editor)
        editor.focus()

    def _exit_edit_mode(self) -> None:
        if not self._editing:
            return
        self._editing = False
        editor_id = f"sticker-editor-{self.sticker.id}"
        try:
            editor = self.query_one(f"#{editor_id}", TextArea)
            self.sticker.content = editor.text
            editor.remove()
        except Exception:
            pass
        self.mount(Static(self.sticker.content, classes="sticker-content"))
        try:
            board = self.app.query_one("StickerBoard")
            board.save_sticker(self.sticker)
        except Exception:
            pass

    def on_key(self, event) -> None:
        if self._editing:
            if event.key == "escape":
                self._exit_edit_mode()
                event.stop()
        else:
            if event.key in ("d", "delete"):
                try:
                    board = self.app.query_one("StickerBoard")
                    board.delete_sticker(self.sticker.id)
                except Exception:
                    pass
                event.stop()
            elif event.key == "enter":
                self._enter_edit_mode()
                event.stop()
