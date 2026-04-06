# tests/test_sticker.py
from sticker0.sticker import Sticker, StickerColors, StickerPosition, StickerSize


def test_sticker_defaults():
    s = Sticker()
    assert s.title == ""
    assert s.content == ""
    assert s.colors.border == "white"
    assert s.colors.text == "white"
    assert s.colors.area == "transparent"
    assert s.minimized is False
    assert s.position.x == 0
    assert s.position.y == 0
    assert s.size.width == 30
    assert s.size.height == 10
    assert s.id != ""


def test_sticker_roundtrip():
    colors = StickerColors(border="black", text="black", area="#ffeb3b")
    s = Sticker(title="Test", content="Hello", colors=colors)
    d = s.to_dict()
    s2 = Sticker.from_dict(d)
    assert s2.id == s.id
    assert s2.title == "Test"
    assert s2.content == "Hello"
    assert s2.colors.border == "black"
    assert s2.colors.text == "black"
    assert s2.colors.area == "#ffeb3b"


def test_sticker_colors_roundtrip():
    colors = StickerColors(border="#ff0000", text="#00ff00", area="transparent")
    s = Sticker(colors=colors)
    d = s.to_dict()
    assert d["colors"]["border"] == "#ff0000"
    assert d["colors"]["text"] == "#00ff00"
    assert d["colors"]["area"] == "transparent"
    s2 = Sticker.from_dict(d)
    assert s2.colors.border == "#ff0000"
    assert s2.colors.text == "#00ff00"
    assert s2.colors.area == "transparent"


def test_sticker_minimized_roundtrip():
    s = Sticker(minimized=True)
    d = s.to_dict()
    assert d["minimized"] is True
    s2 = Sticker.from_dict(d)
    assert s2.minimized is True


def test_legacy_color_migration():
    """기존 v0.2.0 JSON 형식(color 필드)을 새 형식으로 마이그레이션."""
    legacy_data = {
        "id": "test-id",
        "title": "Old",
        "content": "Hello",
        "color": "yellow",
        "border": "rounded",
        "position": {"x": 10, "y": 20},
        "size": {"width": 30, "height": 10},
    }
    s = Sticker.from_dict(legacy_data)
    assert s.id == "test-id"
    assert s.content == "Hello"
    # 기존 color 필드 → 기본 StickerColors로 마이그레이션
    assert s.colors.border == "white"
    assert s.colors.text == "white"
    assert s.colors.area == "transparent"
    assert s.minimized is False


def test_sticker_touch_updates_timestamp():
    import time
    s = Sticker()
    before = s.updated_at
    time.sleep(0.01)
    s.touch()
    assert s.updated_at > before


def test_sticker_line_default():
    from sticker0.sticker import DEFAULT_BORDER_LINE
    s = Sticker()
    assert s.line == DEFAULT_BORDER_LINE
    assert s.line == "solid"


def test_sticker_line_roundtrip():
    s = Sticker(line="heavy")
    d = s.to_dict()
    assert d["line"] == "heavy"
    s2 = Sticker.from_dict(d)
    assert s2.line == "heavy"


def test_sticker_line_migration_from_old_json():
    """기존 JSON에 line 필드 없으면 DEFAULT_BORDER_LINE 적용."""
    old_data = {
        "id": "test-id",
        "title": "Old",
        "content": "Hello",
        "colors": {"border": "white", "text": "white", "area": "transparent"},
        "position": {"x": 0, "y": 0},
        "size": {"width": 30, "height": 10},
    }
    s = Sticker.from_dict(old_data)
    assert s.line == "solid"


def test_border_styles_constant():
    from sticker0.sticker import BORDER_STYLES
    assert "solid" in BORDER_STYLES
    assert "heavy" in BORDER_STYLES
    assert "round" in BORDER_STYLES
    assert "double" in BORDER_STYLES
    assert "ascii" in BORDER_STYLES
    assert "inner" in BORDER_STYLES
    assert "outer" in BORDER_STYLES
    assert "dashed" in BORDER_STYLES
    assert len(BORDER_STYLES) == 8
