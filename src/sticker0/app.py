# src/sticker0/app.py
from __future__ import annotations
from textual.app import App, ComposeResult
from sticker0.config import AppConfig
from sticker0.storage import StickerStorage
from sticker0.widgets.board import StickerBoard


class Sticker0App(App):
    CSS = """
    Screen {
        layers: base stickers menu;
    }
    """

    def __init__(self, storage: StickerStorage | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = AppConfig.load()
        self.storage = storage or StickerStorage()

    def compose(self) -> ComposeResult:
        yield StickerBoard(storage=self.storage, config=self.config)

    def on_mount(self) -> None:
        kb = self.config.keybindings
        self.bind(kb.new, "new_sticker", description="새 스티커")

    def action_new_sticker(self) -> None:
        self.query_one(StickerBoard).add_new_sticker()
