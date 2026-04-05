# tests/test_app.py
import pytest
from sticker0.app import Sticker0App
from sticker0.sticker import Sticker, StickerColor
from sticker0.storage import StickerStorage


@pytest.fixture
def tmp_storage(tmp_path):
    return StickerStorage(data_dir=tmp_path)


@pytest.mark.asyncio
async def test_app_launches(tmp_storage):
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        assert app.is_running


@pytest.mark.asyncio
async def test_sticker_widget_renders_title(tmp_storage):
    s = Sticker(title="My Note", content="Hello")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        from sticker0.widgets.sticker_widget import StickerWidget
        widgets = app.query(StickerWidget)
        assert len(widgets) == 1
        assert widgets.first().sticker.title == "My Note"


@pytest.mark.asyncio
async def test_sticker_drag_moves_position(tmp_storage):
    s = Sticker(title="Drag me")
    s.position.x = 5
    s.position.y = 5
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        from sticker0.widgets.sticker_widget import StickerWidget
        widget = app.query_one(StickerWidget)
        # 타이틀바에서 드래그: widget 위치 기준 offset (2, 0) 에서 mouse down
        # widget.region = (5, 6) 이므로 screen_down = (7, 6)
        await pilot.mouse_down(widget, offset=(2, 0))
        await pilot.pause()
        # screen 절대좌표 (17, 11) 에서 mouse up -> delta (+10, +5)
        # new position = (5+10, 5+5) = (15, 10)
        await pilot.mouse_up(offset=(17, 11))
        await pilot.pause()
        assert widget.sticker.position.x == 15
        assert widget.sticker.position.y == 10
