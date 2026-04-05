# src/sticker0/storage.py
from __future__ import annotations
import json
from pathlib import Path
from sticker0.sticker import Sticker

DATA_DIR = Path.home() / ".local" / "share" / "sticker0"


class StickerStorage:
    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, sticker_id: str) -> Path:
        return self.data_dir / f"{sticker_id}.json"

    def save(self, sticker: Sticker) -> None:
        sticker.touch()
        self._path(sticker.id).write_text(
            json.dumps(sticker.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load(self, sticker_id: str) -> Sticker:
        data = json.loads(self._path(sticker_id).read_text(encoding="utf-8"))
        return Sticker.from_dict(data)

    def load_all(self) -> list[Sticker]:
        stickers = []
        for path in sorted(self.data_dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                stickers.append(Sticker.from_dict(data))
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
        return stickers

    def delete(self, sticker_id: str) -> None:
        path = self._path(sticker_id)
        if path.exists():
            path.unlink()
