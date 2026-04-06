# src/sticker0/widgets/board_menu.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Button
from textual.message import Message

from sticker0.widgets.menu_button import PrimaryOnlyButton
from sticker0.widgets.popup_geometry import apply_clamp_popup_to_parent


class BoardMenu(Widget):
    """빈 보드 영역 우클릭 팝업 메뉴."""

    DEFAULT_CSS = """
    BoardMenu {
        position: absolute;
        width: 24;
        height: auto;
        background: $surface;
        color: $text;
        layer: menu;
    }
    BoardMenu Button {
        width: 1fr;
        height: auto;
        min-height: 1;
        border: none;
        background: transparent;
        color: $text;
    }
    BoardMenu Button:hover {
        background: $accent 20%;
    }
    """

    class MenuAction(Message):
        def __init__(self, action: str, x: int = 0, y: int = 0) -> None:
            super().__init__()
            self.action = action
            self.x = x
            self.y = y

    def __init__(
        self,
        x: int,
        y: int,
        indicator: str = "white",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._menu_x = x
        self._menu_y = y
        self._indicator = indicator

    def on_mount(self) -> None:
        self.styles.offset = (self._menu_x, self._menu_y)
        self.styles.border = ("round", self._indicator)
        self.call_after_refresh(self._clamp_to_parent)

    def _clamp_to_parent(self) -> None:
        apply_clamp_popup_to_parent(self)

    def compose(self) -> ComposeResult:
        yield PrimaryOnlyButton("Create Sticker", id="board-create")
        yield PrimaryOnlyButton("Change Theme", id="board-theme")
        yield PrimaryOnlyButton("Quit Application", id="board-quit")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        action_map = {
            "board-create": "create",
            "board-theme": "theme",
            "board-quit": "quit",
        }
        action = action_map.get(event.button.id or "", "")
        if action:
            self.post_message(
                self.MenuAction(
                    action, x=int(self.offset.x), y=int(self.offset.y)
                )
            )
        self.remove()
