# src/sticker0/widgets/context_menu.py
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


class ContextMenu(Widget):
    """스티커 우클릭 팝업 메뉴."""

    DEFAULT_CSS = """
    ContextMenu {
        position: absolute;
        width: 20;
        height: auto;
        background: transparent;
        layer: menu;
    }
    ContextMenu Button {
        width: 1fr;
        height: auto;
        min-height: 1;
        border: none;
        background: transparent;
    }
    """

    class MenuAction(Message):
        def __init__(
            self, action: str, sticker_id: str, x: int = 0, y: int = 0
        ) -> None:
            super().__init__()
            self.action = action
            self.sticker_id = sticker_id
            self.x = x
            self.y = y

    def __init__(
        self,
        sticker_id: str,
        x: int,
        y: int,
        indicator: str = "white",
        board_background: str = "transparent",
        minimized: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.sticker_id = sticker_id
        self._menu_x = x
        self._menu_y = y
        self._indicator = indicator
        self._board_background = board_background
        self._minimized = minimized

    def on_mount(self) -> None:
        self.styles.offset = (self._menu_x, self._menu_y)
        self.styles.border = ("round", self._indicator)
        apply_popup_board_theme(self, self._board_background, self._indicator)
        self.call_after_refresh(self._clamp_to_parent)

    def _clamp_to_parent(self) -> None:
        apply_clamp_popup_to_parent(self)

    def compose(self) -> ComposeResult:
        mi, mb = self._indicator, self._board_background
        if self._minimized:
            yield PrimaryOnlyButton(
                "Expand", id="menu-restore", menu_indicator=mi, menu_panel_bg=mb
            )
        else:
            yield PrimaryOnlyButton(
                "Minimize", id="menu-minimize", menu_indicator=mi, menu_panel_bg=mb
            )
        yield PrimaryOnlyButton("Copy", id="menu-copy", menu_indicator=mi, menu_panel_bg=mb)
        yield PrimaryOnlyButton("Paste", id="menu-paste", menu_indicator=mi, menu_panel_bg=mb)
        yield PrimaryOnlyButton("Change Color", id="menu-preset", menu_indicator=mi, menu_panel_bg=mb)
        yield PrimaryOnlyButton("Change Border", id="menu-border", menu_indicator=mi, menu_panel_bg=mb)
        yield PrimaryOnlyButton("Delete", id="menu-delete", menu_indicator=mi, menu_panel_bg=mb)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        action_map = {
            "menu-delete": "delete",
            "menu-border": "border",
            "menu-preset": "preset",
            "menu-minimize": "minimize",
            "menu-restore": "restore",
            "menu-copy": "copy",
            "menu-paste": "paste",
        }
        action = action_map.get(event.button.id or "", "")
        if action:
            self.post_message(
                self.MenuAction(
                    action,
                    self.sticker_id,
                    x=int(self.offset.x),
                    y=int(self.offset.y),
                )
            )
            self.remove()
