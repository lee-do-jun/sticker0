# src/sticker0/widgets/context_menu.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Button
from textual.message import Message


class ContextMenu(Widget):
    """스티커 우클릭 팝업 메뉴."""

    DEFAULT_CSS = """
    ContextMenu {
        position: absolute;
        width: 20;
        height: auto;
        background: $surface;
        color: $text;
        layer: menu;
    }
    ContextMenu Button {
        width: 1fr;
        height: auto;
        min-height: 1;
        border: none;
        background: transparent;
        color: $text;
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

    def __init__(
        self,
        sticker_id: str,
        x: int,
        y: int,
        indicator: str = "white",
        minimized: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.sticker_id = sticker_id
        self._menu_x = x
        self._menu_y = y
        self._indicator = indicator
        self._minimized = minimized

    def on_mount(self) -> None:
        self.styles.offset = (self._menu_x, self._menu_y)
        self.styles.border = ("round", self._indicator)

    def compose(self) -> ComposeResult:
        if self._minimized:
            yield Button("Expand", id="menu-restore")
        else:
            yield Button("Minimize", id="menu-minimize")
        yield Button("Color", id="menu-preset")
        yield Button("Delete", id="menu-delete")
        yield Button("Close", id="menu-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "menu-close":
            self.remove()
            return
        action_map = {
            "menu-delete": "delete",
            "menu-preset": "preset",
            "menu-minimize": "minimize",
            "menu-restore": "restore",
        }
        action = action_map.get(event.button.id or "", "")
        if action:
            self.post_message(self.MenuAction(action, self.sticker_id))
            self.remove()
