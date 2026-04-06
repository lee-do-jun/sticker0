# src/sticker0/widgets/sticker_widget.py
from __future__ import annotations
import time
from dataclasses import replace

from rich.style import Style
from textual.widget import Widget
from textual.widgets import TextArea
from textual.widgets.text_area import TextAreaTheme
from textual.app import ComposeResult
from textual.events import MouseDown, MouseMove, MouseUp
from textual.css.query import NoMatches
from sticker0.sticker import Sticker

# 테두리 스타일 이름 → Textual border 스타일
BORDER_STYLE_MAP: dict[str, str] = {
    "single": "solid",
    "double": "double",
    "heavy": "heavy",
    "simple": "ascii",
}

_DRAG_MOVE = "move"
_DRAG_RESIZE_RIGHT = "resize_right"
_DRAG_RESIZE_LEFT = "resize_left"
_DRAG_RESIZE_H = "resize_h"

DOUBLE_CLICK_INTERVAL = 0.4


class StickerWidget(Widget):
    DEFAULT_CSS = """
    StickerWidget {
        position: absolute;
        min-width: 20;
        min-height: 3;
        background: transparent;
    }
    StickerWidget TextArea {
        height: 1fr;
        border: none;
        padding: 0 2 0 1;
    }
    StickerWidget TextArea:focus {
        border: none;
    }
    """

    MIN_WIDTH = 20
    MIN_HEIGHT = 5
    MINIMIZED_HEIGHT = 3
    can_focus = True

    def __init__(self, sticker: Sticker, **kwargs) -> None:
        super().__init__(**kwargs)
        self.sticker = sticker
        self._drag_start: tuple[int, int] | None = None
        self._drag_origin: tuple[int, int] = (0, 0)
        self._drag_mode: str = _DRAG_MOVE
        self._last_top_click: float = 0.0

    def on_mount(self) -> None:
        self._apply_sticker_styles()

    def _get_board_background(self) -> str:
        """보드 테마의 background 색상 조회."""
        try:
            board = self.app.query_one("StickerBoard")
            return getattr(board, "board_bg", "transparent")
        except NoMatches:
            return "transparent"

    def _get_border_config(self) -> tuple[str, str]:
        """config에서 border top/sides 스타일 조회. (top_textual, sides_textual) 반환."""
        try:
            config = self.app.config
            top = BORDER_STYLE_MAP.get(config.border.top, "double")
            sides = BORDER_STYLE_MAP.get(config.border.sides, "solid")
            return (top, sides)
        except AttributeError:
            return ("double", "solid")

    def _apply_sticker_styles(self) -> None:
        colors = self.sticker.colors
        # Area color: transparent → 보드 배경 상속
        area_color = colors.area
        if area_color == "transparent":
            area_color = self._get_board_background()
        self.styles.background = area_color
        self.styles.color = colors.text

        # Border style from config
        top_style, sides_style = self._get_border_config()
        self.styles.border = (sides_style, colors.border)
        self.styles.border_top = (top_style, colors.border)

        # Position and size
        self.styles.offset = (self.sticker.position.x, self.sticker.position.y)
        self.styles.width = self.sticker.size.width
        if self.sticker.minimized:
            self.styles.height = self.MINIMIZED_HEIGHT
        else:
            self.styles.height = self.sticker.size.height

        # TextArea: 기본 $surface/$foreground가 부모를 가리지 않으므로 편집 영역에 직접 반영.
        # 커서(.text-area--cursor)는 본문 color와 별도라서 css 테마 복제 + cursor_style으로 맞춘다.
        # theme 설정 시 TextArea가 color/background를 초기화하므로 테마 적용 뒤에 스타일을 다시 준다.
        try:
            editor = self._get_editor()
            base_theme = TextAreaTheme.get_builtin_theme("css")
            if base_theme is not None:
                theme_name = f"sticker-ta-{self.sticker.id}"
                # 일반 글자와 동일한 (text + area) 조합은 커서 칸이 안 보임. 역전시켜 텍스트 색이 블록에 쓰이게 함.
                cursor_style = Style(color=area_color, bgcolor=colors.text)
                editor.register_theme(
                    replace(base_theme, name=theme_name, cursor_style=cursor_style)
                )
                editor.theme = theme_name
            editor.styles.background = area_color
            editor.styles.color = colors.text
            editor.styles.scrollbar_color = colors.text
            editor.styles.scrollbar_background = colors.area if colors.area != "transparent" else area_color
        except NoMatches:
            pass

    def compose(self) -> ComposeResult:
        editor_id = f"sticker-editor-{self.sticker.id}"
        yield TextArea(self.sticker.content, id=editor_id)

    def _get_editor(self) -> TextArea:
        return self.query_one(f"#sticker-editor-{self.sticker.id}", TextArea)

    def _classify_border(self, x: int, y: int) -> str | None:
        w = self.outer_size.width
        h = self.outer_size.height
        if y == 0:
            return _DRAG_MOVE
        if self.sticker.minimized:
            return None  # 최소화 상태에서 리사이즈 불가
        if x == 0:
            return _DRAG_RESIZE_LEFT
        if x == w - 1:
            return _DRAG_RESIZE_RIGHT
        if y == h - 1:
            return _DRAG_RESIZE_H
        return None

    def _move_to_front(self) -> None:
        parent = self.parent
        if parent is not None:
            children = list(parent.children)
            if children and children[-1] is not self:
                parent.move_child(self, after=children[-1])

    def on_mouse_down(self, event: MouseDown) -> None:
        if event.button == 1:
            try:
                board = self.app.query_one("StickerBoard")
                board.close_all_menus()
            except NoMatches:
                pass
        self._move_to_front()
        mode = self._classify_border(event.x, event.y)

        # 상단 테두리 더블클릭 → 최소화/복원 토글
        if mode == _DRAG_MOVE:
            now = time.monotonic()
            if now - self._last_top_click < DOUBLE_CLICK_INTERVAL:
                self._toggle_minimize()
                self._last_top_click = 0.0
                event.stop()
                return
            self._last_top_click = now

        if mode is None:
            if self.sticker.minimized:
                event.stop()  # 최소화 시 내부 클릭 차단
            return

        event.stop()
        self._drag_start = (event.screen_x, event.screen_y)
        self._drag_mode = mode
        if mode == _DRAG_MOVE:
            self._drag_origin = (self.sticker.position.x, self.sticker.position.y)
        elif mode == _DRAG_RESIZE_LEFT:
            self._drag_origin = (self.sticker.position.x, self.sticker.size.width)
        else:
            self._drag_origin = (self.sticker.size.width, self.sticker.size.height)
        self.capture_mouse()

    def on_mouse_move(self, event: MouseMove) -> None:
        if self._drag_start is None:
            return
        event.stop()
        dx = event.screen_x - self._drag_start[0]
        dy = event.screen_y - self._drag_start[1]
        self._apply_drag(dx, dy)

    def _clamp_position(self) -> None:
        """스티커 중앙점이 화면 우변/하변을 넘지 않도록 보정."""
        try:
            screen_w = self.screen.size.width
            screen_h = self.screen.size.height
        except Exception:
            return
        cx = self.sticker.position.x + self.sticker.size.width // 2
        cy = self.sticker.position.y + self.sticker.size.height // 2
        if cx > screen_w:
            self.sticker.position.x = screen_w - self.sticker.size.width // 2
        if cy > screen_h:
            self.sticker.position.y = screen_h - self.sticker.size.height // 2
        self.sticker.position.x = max(0, self.sticker.position.x)
        self.sticker.position.y = max(0, self.sticker.position.y)
        self.styles.offset = (self.sticker.position.x, self.sticker.position.y)

    def _apply_drag(self, dx: int, dy: int) -> None:
        if self._drag_mode == _DRAG_MOVE:
            new_x = max(0, self._drag_origin[0] + dx)
            new_y = max(0, self._drag_origin[1] + dy)
            self.sticker.position.x = new_x
            self.sticker.position.y = new_y
            self.styles.offset = (new_x, new_y)
            self._clamp_position()
        elif self._drag_mode == _DRAG_RESIZE_RIGHT:
            new_w = max(self.MIN_WIDTH, self._drag_origin[0] + dx)
            self.sticker.size.width = new_w
            self.styles.width = new_w
        elif self._drag_mode == _DRAG_RESIZE_LEFT:
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
            try:
                board = self.app.query_one("StickerBoard")
                if board._pointer_is_on_popup_layer(event):
                    event.stop()
                    return
            except NoMatches:
                pass
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
            try:
                board = self.app.query_one("StickerBoard")
                board.save_sticker(self.sticker)
            except NoMatches:
                pass

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self.sticker.content = event.text_area.text
        try:
            board = self.app.query_one("StickerBoard")
            board.save_sticker(self.sticker)
        except NoMatches:
            pass

    def _toggle_minimize(self) -> None:
        """최소화/복원 토글."""
        self._set_minimized(not self.sticker.minimized)

    def _set_minimized(self, minimized: bool) -> None:
        from textual.widgets import Static
        self.sticker.minimized = minimized
        if minimized:
            self.styles.height = self.MINIMIZED_HEIGHT
            try:
                editor = self._get_editor()
                editor.display = False
            except NoMatches:
                pass
            # 첫 줄 텍스트 + ellipsis 표시
            first_line = self.sticker.content.split("\n")[0] if self.sticker.content else ""
            max_w = max(1, self.sticker.size.width - 4)
            if len(first_line) > max_w:
                first_line = first_line[: max_w - 3] + "..."
            try:
                self.query_one("#minimized-label").remove()
            except NoMatches:
                pass
            self.mount(Static(first_line, id="minimized-label"))
        else:
            self.styles.height = self.sticker.size.height
            try:
                editor = self._get_editor()
                editor.display = True
            except NoMatches:
                pass
            try:
                self.query_one("#minimized-label").remove()
            except NoMatches:
                pass
        try:
            board = self.app.query_one("StickerBoard")
            board.save_sticker(self.sticker)
        except NoMatches:
            pass

    def _show_context_menu(self, screen_x: int, screen_y: int) -> None:
        from sticker0.widgets.context_menu import ContextMenu
        board = self.app.query_one("StickerBoard")
        # 메뉴 상호 배제: 모든 기존 메뉴 닫기
        board.close_all_menus()
        local_x = screen_x - board.region.x
        local_y = screen_y - board.region.y
        indicator = getattr(board, "indicator", "white")
        board_bg = getattr(board, "board_bg", "transparent")
        menu = ContextMenu(
            sticker_id=self.sticker.id,
            x=local_x,
            y=local_y,
            indicator=indicator,
            board_background=board_bg,
            minimized=self.sticker.minimized,
        )
        board.mount(menu)

    def _enter_edit_mode(self) -> None:
        if not self.sticker.minimized:
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
