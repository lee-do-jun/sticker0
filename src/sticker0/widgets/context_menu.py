# src/sticker0/widgets/context_menu.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Button
from textual.message import Message


class ContextMenu(Widget):
    """우클릭 팝업 메뉴."""

    DEFAULT_CSS = """
    ContextMenu {
        position: absolute;
        width: 20;
        height: auto;
        border: round $accent;
        background: $surface;
        layer: menu;
    }
    ContextMenu Button {
        width: 1fr;
        height: 1;
        border: none;
        background: transparent;
    }
    ContextMenu Button:hover {
        background: $accent 20%;
    }
    """

    class MenuAction(Message):
        def __init__(self, action: str, sticker_id: str) -> None:
            super().__init__()
            self.action = action
            self.sticker_id = sticker_id

    def __init__(self, sticker_id: str, x: int, y: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.sticker_id = sticker_id
        self._menu_x = x
        self._menu_y = y

    def on_mount(self) -> None:
        self.styles.offset = (self._menu_x, self._menu_y)

    def compose(self) -> ComposeResult:
        yield Button("편집", id="menu-edit", variant="default")
        yield Button("삭제", id="menu-delete", variant="error")
        yield Button("색상 변경", id="menu-color", variant="default")
        yield Button("닫기", id="menu-close", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "menu-close":
            self.remove()
            return
        action_map = {
            "menu-edit": "edit",
            "menu-delete": "delete",
            "menu-color": "color",
        }
        action = action_map.get(event.button.id or "", "")
        if action:
            self.post_message(self.MenuAction(action, self.sticker_id))
            self.remove()
