# src/sticker0/widgets/board_menu.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Button
from textual.message import Message

from sticker0.widgets.menu_button import PrimaryOnlyButton
from sticker0.widgets.popup_geometry import (
    apply_clamp_popup_to_parent,
    apply_popup_board_theme,
)


class BoardMenu(Widget):
    """빈 보드 영역 우클릭 팝업 메뉴."""

    DEFAULT_CSS = """
    BoardMenu {
        position: absolute;
        width: 28;
        height: auto;
        background: transparent;
        layer: menu;
    }
    BoardMenu Button {
        width: 1fr;
        height: auto;
        min-height: 1;
        border: none;
        background: transparent;
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
        board_background: str = "transparent",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._menu_x = x
        self._menu_y = y
        self._indicator = indicator
        self._board_background = board_background

    def on_mount(self) -> None:
        self.styles.offset = (self._menu_x, self._menu_y)
        self.styles.border = ("round", self._indicator)
        apply_popup_board_theme(self, self._board_background, self._indicator)
        self.call_after_refresh(self._clamp_to_parent)

    def _clamp_to_parent(self) -> None:
        apply_clamp_popup_to_parent(self)

    def compose(self) -> ComposeResult:
        yield PrimaryOnlyButton(
            "New Sticker",
            id="board-create",
            menu_indicator=self._indicator,
            menu_panel_bg=self._board_background,
        )
        yield PrimaryOnlyButton(
            "New from Clipboard",
            id="board-new-from-clipboard",
            menu_indicator=self._indicator,
            menu_panel_bg=self._board_background,
        )
        yield PrimaryOnlyButton(
            "Change Theme",
            id="board-theme",
            menu_indicator=self._indicator,
            menu_panel_bg=self._board_background,
        )
        yield PrimaryOnlyButton(
            "Quit",
            id="board-quit",
            menu_indicator=self._indicator,
            menu_panel_bg=self._board_background,
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        action_map = {
            "board-create": "create",
            "board-new-from-clipboard": "new_from_clipboard",
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
