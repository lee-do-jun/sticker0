# tests/test_storage.py
import pytest
from pathlib import Path
from sticker0.storage import StickerStorage
from sticker0.sticker import Sticker, StickerColor


def test_save_and_load(tmp_path):
    storage = StickerStorage(data_dir=tmp_path)
    s = Sticker(title="Hello", content="World", color=StickerColor.BLUE)
    storage.save(s)
    loaded = storage.load(s.id)
    assert loaded.id == s.id
    assert loaded.title == "Hello"
    assert loaded.content == "World"
    assert loaded.color == StickerColor.BLUE


def test_load_all(tmp_path):
    storage = StickerStorage(data_dir=tmp_path)
    s1 = Sticker(title="A")
    s2 = Sticker(title="B")
    storage.save(s1)
    storage.save(s2)
    all_stickers = storage.load_all()
    assert len(all_stickers) == 2
    titles = {s.title for s in all_stickers}
    assert titles == {"A", "B"}


def test_delete(tmp_path):
    storage = StickerStorage(data_dir=tmp_path)
    s = Sticker(title="To delete")
    storage.save(s)
    storage.delete(s.id)
    assert storage.load_all() == []


def test_delete_nonexistent_is_noop(tmp_path):
    storage = StickerStorage(data_dir=tmp_path)
    storage.delete("nonexistent-id")  # should not raise


def test_corrupted_file_is_skipped(tmp_path):
    storage = StickerStorage(data_dir=tmp_path)
    (tmp_path / "bad.json").write_text("not json", encoding="utf-8")
    assert storage.load_all() == []
