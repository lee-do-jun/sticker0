# src/sticker0/widgets/board.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.events import MouseUp
from sticker0.config import AppConfig
from sticker0.sticker import Sticker, StickerSize
from sticker0.storage import StickerStorage
from sticker0.widgets.sticker_widget import StickerWidget


class StickerBoard(Widget):
    DEFAULT_CSS = """
    StickerBoard {
        width: 1fr;
        height: 1fr;
        layers: stickers menu;
    }
    StickerWidget {
        layer: stickers;
    }
    """

    def __init__(
        self,
        storage: StickerStorage,
        config: AppConfig,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.storage = storage
        self.config = config

    def compose(self) -> ComposeResult:
        for sticker in self.storage.load_all():
            yield StickerWidget(sticker)

    def save_sticker(self, sticker) -> None:
        self.storage.save(sticker)

    def add_new_sticker(self, x: int | None = None, y: int | None = None) -> None:
        cfg = self.config
        sticker = Sticker(
            color=cfg.theme.default_color,
            border=cfg.border.border_type,
            size=StickerSize(
                width=cfg.defaults.width,
                height=cfg.defaults.height,
            ),
        )
        if x is not None and y is not None:
            sticker.position.x = x
            sticker.position.y = y
        else:
            # 화면 중앙 배치
            try:
                screen = self.screen
                center_x = max(0, (screen.size.width - sticker.size.width) // 2)
                center_y = max(0, (screen.size.height - sticker.size.height) // 2)
                sticker.position.x = center_x
                sticker.position.y = center_y
            except Exception:
                pass
        self.storage.save(sticker)
        self.mount(StickerWidget(sticker))

    def delete_sticker(self, sticker_id: str) -> None:
        self.storage.delete(sticker_id)
        for widget in self.query(StickerWidget):
            if widget.sticker.id == sticker_id:
                widget.remove()
                break

    def on_context_menu_menu_action(self, message) -> None:
        if message.action == "delete":
            self.delete_sticker(message.sticker_id)
        elif message.action == "edit":
            for widget in self.query(StickerWidget):
                if widget.sticker.id == message.sticker_id:
                    widget._enter_edit_mode()
        elif message.action == "color":
            from sticker0.widgets.color_picker import ColorPicker
            # 기존 ColorPicker 닫기
            for picker in self.query(ColorPicker):
                picker.remove()
            picker = ColorPicker(
                sticker_id=message.sticker_id,
                x=22,
                y=3,
            )
            self.mount(picker)

    def on_mouse_up(self, event: MouseUp) -> None:
        """빈 영역 우클릭 감지 (StickerWidget이 stop하지 않은 경우)."""
        if event.button == 3:
            from sticker0.widgets.board_menu import BoardMenu
            from sticker0.widgets.context_menu import ContextMenu
            for menu in self.query(BoardMenu):
                menu.remove()
            for menu in self.query(ContextMenu):
                menu.remove()
            menu = BoardMenu(x=event.x, y=event.y)
            self.mount(menu)

    def on_board_menu_menu_action(self, message) -> None:
        if message.action == "create":
            self.add_new_sticker(x=message.x, y=message.y)
        elif message.action == "quit":
            self.app.exit()
        # "theme" is reserved for future use

    def on_color_picker_color_selected(self, message) -> None:
        from sticker0.widgets.color_picker import ColorPicker
        from sticker0.widgets.sticker_widget import StickerWidget
        for widget in self.query(StickerWidget):
            if widget.sticker.id == message.sticker_id:
                widget.sticker.color = message.color
                widget._apply_sticker_styles()
                widget.refresh()
                self.storage.save(widget.sticker)
                break
