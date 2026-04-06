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

    def __init__(
        self,
        storage: StickerStorage | None = None,
        config: AppConfig | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.config = config if config is not None else AppConfig.load()
        self.storage = storage or StickerStorage()

    def compose(self) -> ComposeResult:
        yield StickerBoard(storage=self.storage, config=self.config)
