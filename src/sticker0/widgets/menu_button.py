# src/sticker0/widgets/menu_button.py
"""팝업 메뉴용 버튼: 좌클릭만 Pressed, 우클릭은 무시."""
from __future__ import annotations

from textual import events
from textual.widgets import Button


class PrimaryOnlyButton(Button):
    async def _on_click(self, event: events.Click) -> None:
        # Textual은 MRO에서 서브클래스·Button 양쪽 _on_click을 모두 호출한다.
        # 우클릭 등 비주 버튼에서는 prevent_default로 Button._on_click(press)를 막는다.
        if event.button != 1:
            event.prevent_default()
            event.stop()
            return
        event.prevent_default()
        await super()._on_click(event)
