# src/sticker0/widgets/menu_button.py
"""팝업 메뉴용 버튼: 좌클릭만 Pressed, 우클릭은 무시."""
from __future__ import annotations

from textual import events
from textual.widgets import Button


class PrimaryOnlyButton(Button):
    """팝업 메뉴 전용. compact 기본값으로 입체 테두리(음영) 제거."""

    def __init__(
        self,
        *args,
        menu_indicator: str | None = None,
        menu_panel_bg: str | None = None,
        menu_idle_bg: str | None = None,
        menu_idle_color: str | None = None,
        **kwargs,
    ) -> None:
        compact = kwargs.pop("compact", True)
        super().__init__(*args, compact=compact, **kwargs)
        self._menu_indicator = menu_indicator
        self._menu_panel_bg = menu_panel_bg
        self._menu_idle_bg = menu_idle_bg
        self._menu_idle_color = menu_idle_color

    def on_mount(self) -> None:
        if self._menu_indicator is not None and self._menu_panel_bg is not None:
            self._swap_hover_off()

    def _swap_hover_on(self) -> None:
        if self._menu_indicator is None or self._menu_panel_bg is None:
            return
        self.styles.background = self._menu_indicator
        self.styles.color = self._menu_panel_bg

    def _swap_hover_off(self) -> None:
        if self._menu_indicator is None or self._menu_panel_bg is None:
            return
        bg = (
            self._menu_idle_bg
            if self._menu_idle_bg is not None
            else "transparent"
        )
        color = (
            self._menu_idle_color
            if self._menu_idle_color is not None
            else self._menu_indicator
        )
        self.styles.background = bg
        self.styles.color = color

    def on_enter(self, event: events.Enter) -> None:
        if event.node is not self:
            return
        self._swap_hover_on()

    def on_leave(self, event: events.Leave) -> None:
        if event.node is not self:
            return
        self._swap_hover_off()

    async def _on_click(self, event: events.Click) -> None:
        # Textual은 MRO에서 서브클래스·Button 양쪽 _on_click을 모두 호출한다.
        # 우클릭 등 비주 버튼에서는 prevent_default로 Button._on_click(press)를 막는다.
        if event.button != 1:
            event.prevent_default()
            event.stop()
            return
        event.prevent_default()
        await super()._on_click(event)
