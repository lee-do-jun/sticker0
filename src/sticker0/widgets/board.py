# src/sticker0/widgets/board.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from sticker0.config import AppConfig
from sticker0.sticker import Sticker
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

    def add_new_sticker(self) -> None:
        sticker = Sticker()
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
