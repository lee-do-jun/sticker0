# src/sticker0/widgets/sticker_widget.py
from __future__ import annotations
from textual.widget import Widget
from textual.widgets import TextArea
from textual.app import ComposeResult
from textual.events import MouseDown, MouseMove, MouseUp
from textual.css.query import NoMatches
from sticker0.sticker import Sticker, StickerColor, BorderType

COLOR_MAP: dict[StickerColor, tuple[str, str]] = {
    StickerColor.YELLOW: ("#000000", "#ffeb3b"),
    StickerColor.BLUE:   ("#ffffff", "#1565c0"),
    StickerColor.GREEN:  ("#000000", "#4caf50"),
    StickerColor.PINK:   ("#000000", "#f48fb1"),
    StickerColor.WHITE:  ("#000000", "#ffffff"),
    StickerColor.DARK:   ("#ffffff", "#212121"),
    StickerColor.NONE:   ("", ""),
}

BORDER_MAP: dict[BorderType, str] = {
    BorderType.ROUNDED: "round",
    BorderType.SHARP:   "solid",
    BorderType.DOUBLE:  "double",
    BorderType.THICK:   "heavy",
    BorderType.ASCII:   "ascii",
}

_DRAG_MOVE = "move"
_DRAG_RESIZE_RIGHT = "resize_right"
_DRAG_RESIZE_LEFT = "resize_left"
_DRAG_RESIZE_H = "resize_h"


class StickerWidget(Widget):
    DEFAULT_CSS = """
    StickerWidget {
        position: absolute;
        min-width: 20;
        min-height: 5;
        background: transparent;
    }
    StickerWidget TextArea {
        height: 1fr;
        border: none;
        padding: 0 1;
    }
    StickerWidget TextArea:focus {
        border: none;
    }
    """

    MIN_WIDTH = 20
    MIN_HEIGHT = 5
    can_focus = True

    def __init__(self, sticker: Sticker, **kwargs) -> None:
        super().__init__(**kwargs)
        self.sticker = sticker
        self._drag_start: tuple[int, int] | None = None
        self._drag_origin: tuple[int, int] = (0, 0)
        self._drag_mode: str = _DRAG_MOVE

    def on_mount(self) -> None:
        self._apply_sticker_styles()

    def _apply_sticker_styles(self) -> None:
        border_style = BORDER_MAP.get(self.sticker.border, "round")
        if self.sticker.color == StickerColor.NONE:
            self.styles.background = "transparent"
            self.styles.border = (border_style, "#888888")
            self.styles.border_top = ("double", "#888888")
        else:
            text_color, bg_color = COLOR_MAP.get(
                self.sticker.color, ("#000000", "#ffeb3b")
            )
            self.styles.background = bg_color
            self.styles.color = text_color
            self.styles.border = (border_style, text_color)
            self.styles.border_top = ("double", text_color)
        self.styles.offset = (self.sticker.position.x, self.sticker.position.y)
        self.styles.width = self.sticker.size.width
        self.styles.height = self.sticker.size.height

    def compose(self) -> ComposeResult:
        editor_id = f"sticker-editor-{self.sticker.id}"
        yield TextArea(self.sticker.content, id=editor_id)

    def _get_editor(self) -> TextArea:
        return self.query_one(f"#sticker-editor-{self.sticker.id}", TextArea)

    def _classify_border(self, x: int, y: int) -> str | None:
        """Return which border region the click is in, or None for interior."""
        w = self.outer_size.width
        h = self.outer_size.height
        if y == 0:
            return _DRAG_MOVE
        if x == 0:
            return _DRAG_RESIZE_LEFT
        if x == w - 1:
            return _DRAG_RESIZE_RIGHT
        if y == h - 1:
            return _DRAG_RESIZE_H
        return None

    def _move_to_front(self) -> None:
        """Move this widget to be the last child of its parent (highest z-index)."""
        parent = self.parent
        if parent is not None:
            children = list(parent.children)
            if children and children[-1] is not self:
                parent.move_child(self, after=children[-1])

    def on_mouse_down(self, event: MouseDown) -> None:
        self._move_to_front()
        mode = self._classify_border(event.x, event.y)
        if mode is None:
            return
        event.stop()
        self._drag_start = (event.screen_x, event.screen_y)
        self._drag_mode = mode
        if mode == _DRAG_MOVE:
            self._drag_origin = (self.sticker.position.x, self.sticker.position.y)
        elif mode == _DRAG_RESIZE_LEFT:
            # 좌측 가장자리 이동: position.x와 width 모두 origin 저장
            self._drag_origin = (self.sticker.position.x, self.sticker.size.width)
        else:
            # resize_right, resize_h: width 또는 height origin
            self._drag_origin = (self.sticker.size.width, self.sticker.size.height)
        self.capture_mouse()

    def on_mouse_move(self, event: MouseMove) -> None:
        if self._drag_start is None:
            return
        event.stop()
        dx = event.screen_x - self._drag_start[0]
        dy = event.screen_y - self._drag_start[1]
        self._apply_drag(dx, dy)

    def _apply_drag(self, dx: int, dy: int) -> None:
        if self._drag_mode == _DRAG_MOVE:
            new_x = max(0, self._drag_origin[0] + dx)
            new_y = max(0, self._drag_origin[1] + dy)
            self.sticker.position.x = new_x
            self.sticker.position.y = new_y
            self.styles.offset = (new_x, new_y)
        elif self._drag_mode == _DRAG_RESIZE_RIGHT:
            new_w = max(self.MIN_WIDTH, self._drag_origin[0] + dx)
            self.sticker.size.width = new_w
            self.styles.width = new_w
        elif self._drag_mode == _DRAG_RESIZE_LEFT:
            # origin_x = position.x, origin_w = width (stored in tuple)
            new_x = max(0, self._drag_origin[0] + dx)
            new_w = max(self.MIN_WIDTH, self._drag_origin[1] - dx)
            self.sticker.position.x = new_x
            self.sticker.size.width = new_w
            self.styles.offset = (new_x, self.sticker.position.y)
            self.styles.width = new_w
        elif self._drag_mode == _DRAG_RESIZE_H:
            new_h = max(self.MIN_HEIGHT, self._drag_origin[1] + dy)
            self.sticker.size.height = new_h
            self.styles.height = new_h

    def on_mouse_up(self, event: MouseUp) -> None:
        if event.button == 3:
            event.stop()
            self._drag_start = None
            self.release_mouse()
            self._show_context_menu(event.screen_x, event.screen_y)
            return
        if self._drag_start is not None:
            dx = event.screen_x - self._drag_start[0]
            dy = event.screen_y - self._drag_start[1]
            self._apply_drag(dx, dy)
            self._drag_start = None
            self.release_mouse()
            board = self.app.query_one("StickerBoard")
            board.save_sticker(self.sticker)

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self.sticker.content = event.text_area.text
        try:
            board = self.app.query_one("StickerBoard")
            board.save_sticker(self.sticker)
        except NoMatches:
            pass

    def _show_context_menu(self, screen_x: int, screen_y: int) -> None:
        from sticker0.widgets.context_menu import ContextMenu
        for menu in self.app.query(ContextMenu):
            menu.remove()
        board = self.app.query_one("StickerBoard")
        local_x = screen_x - board.region.x
        local_y = screen_y - board.region.y
        menu = ContextMenu(
            sticker_id=self.sticker.id,
            x=local_x,
            y=local_y,
        )
        board.mount(menu)

    def _enter_edit_mode(self) -> None:
        """Enter edit mode: just focus the TextArea (board.py compatibility)."""
        self._get_editor().focus()

    def on_key(self, event) -> None:
        if event.key in ("d", "delete"):
            try:
                board = self.app.query_one("StickerBoard")
                board.delete_sticker(self.sticker.id)
            except NoMatches:
                pass
            event.stop()
        elif event.key == "enter":
            self._enter_edit_mode()
            event.stop()
