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
        # widget.region = (5, 5) 이므로 screen_down = (7, 5)
        await pilot.mouse_down(widget, offset=(2, 0))
        await pilot.pause()
        # screen 절대좌표 (17, 10) 에서 mouse up -> delta (+10, +5)
        # new position = (5+10, 5+5) = (15, 10)
        await pilot.mouse_up(offset=(17, 10))
        await pilot.pause()
        assert widget.sticker.position.x == 15
        assert widget.sticker.position.y == 10


@pytest.mark.asyncio
async def test_textarea_always_present(tmp_storage):
    """TextArea is always rendered (no separate view/edit modes)."""
    from sticker0.widgets.sticker_widget import StickerWidget
    from textual.widgets import TextArea
    s = Sticker(content="hello")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        assert len(app.query(TextArea)) == 1


@pytest.mark.asyncio
async def test_single_click_focuses_textarea(tmp_storage):
    """Single click focuses the TextArea."""
    from sticker0.widgets.sticker_widget import StickerWidget
    from textual.widgets import TextArea
    s = Sticker(title="Edit me", content="original")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        await pilot.click(widget, offset=(5, 2))
        await pilot.pause(0.1)
        assert len(app.query(TextArea)) >= 1


@pytest.mark.asyncio
async def test_textarea_content_saves_on_change(tmp_storage):
    """TextArea content changes are reflected in sticker data."""
    from sticker0.widgets.sticker_widget import StickerWidget
    from textual.widgets import TextArea
    s = Sticker(content="original")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        await pilot.click(widget, offset=(5, 2))
        await pilot.pause(0.1)
        await pilot.press("a", "b", "c")
        await pilot.pause(0.1)
        assert "abc" in widget.sticker.content


@pytest.mark.asyncio
async def test_sticker_resize_right_border(tmp_storage):
    """Right border drag changes width."""
    from sticker0.widgets.sticker_widget import StickerWidget
    s = Sticker(content="Resize me")
    s.size.width = 30
    s.size.height = 10
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        right_border_x = s.size.width - 1
        mid_y = s.size.height // 2
        await pilot.mouse_down(widget, offset=(right_border_x, mid_y))
        right_screen_x = widget.region.x + right_border_x
        mid_screen_y = widget.region.y + mid_y
        await pilot.mouse_up(offset=(right_screen_x + 10, mid_screen_y))
        await pilot.pause(0.1)
        assert widget.sticker.size.width == 40


@pytest.mark.asyncio
async def test_sticker_resize_bottom_border(tmp_storage):
    """Bottom border drag changes height."""
    from sticker0.widgets.sticker_widget import StickerWidget
    s = Sticker(content="Resize me")
    s.size.width = 30
    s.size.height = 10
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        bottom_border_y = s.size.height - 1
        mid_x = s.size.width // 2
        await pilot.mouse_down(widget, offset=(mid_x, bottom_border_y))
        mid_screen_x = widget.region.x + mid_x
        bottom_screen_y = widget.region.y + bottom_border_y
        await pilot.mouse_up(offset=(mid_screen_x, bottom_screen_y + 5))
        await pilot.pause(0.1)
        assert widget.sticker.size.height == 15


@pytest.mark.asyncio
async def test_click_brings_sticker_to_front(tmp_storage):
    """Clicking a sticker moves it to the end of DOM (z-index front)."""
    from sticker0.widgets.sticker_widget import StickerWidget
    s1 = Sticker(content="first")
    s1.position.x = 0
    s1.position.y = 0
    s2 = Sticker(content="second")
    s2.position.x = 50
    s2.position.y = 0
    tmp_storage.save(s1)
    tmp_storage.save(s2)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widgets = list(app.query(StickerWidget))
        assert len(widgets) == 2
        first_widget = widgets[0]
        first_id = first_widget.sticker.id
        await pilot.mouse_down(first_widget, offset=(2, 0))
        await pilot.mouse_up(first_widget, offset=(2, 0))
        await pilot.pause(0.1)
        board = app.query_one("StickerBoard")
        last_widget = list(board.query(StickerWidget))[-1]
        assert last_widget.sticker.id == first_id


@pytest.mark.asyncio
async def test_right_click_shows_context_menu(tmp_storage):
    from sticker0.widgets.sticker_widget import StickerWidget
    from sticker0.widgets.context_menu import ContextMenu
    s = Sticker(title="Menu test")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        await pilot.click(widget, button=3, offset=(5, 2))
        await pilot.pause(0.1)
        assert len(app.query(ContextMenu)) == 1


@pytest.mark.asyncio
async def test_context_menu_delete_removes_sticker(tmp_storage):
    from sticker0.widgets.sticker_widget import StickerWidget
    from sticker0.widgets.context_menu import ContextMenu
    s = Sticker(title="Delete via menu")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        await pilot.click(widget, button=3, offset=(5, 2))
        await pilot.pause(0.1)
        menu = app.query_one(ContextMenu)
        await pilot.click(menu.query_one("#menu-delete"))
        await pilot.pause(0.1)
        assert len(app.query(StickerWidget)) == 0
        assert tmp_storage.load_all() == []


@pytest.mark.asyncio
async def test_press_n_creates_sticker(tmp_storage):
    from sticker0.widgets.sticker_widget import StickerWidget
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("n")
        await pilot.pause(0.1)
        assert len(app.query(StickerWidget)) == 1
        assert len(tmp_storage.load_all()) == 1


@pytest.mark.asyncio
async def test_color_change_via_context_menu(tmp_storage):
    from sticker0.widgets.sticker_widget import StickerWidget
    from sticker0.widgets.color_picker import ColorPicker
    from sticker0.sticker import StickerColor
    s = Sticker(title="Color test", color=StickerColor.YELLOW)
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        # 우클릭으로 컨텍스트 메뉴 열기
        await pilot.click(widget, button=3, offset=(5, 2))
        await pilot.pause(0.1)
        from sticker0.widgets.context_menu import ContextMenu
        menu = app.query_one(ContextMenu)
        # 색상 변경 버튼 클릭
        await pilot.click(menu.query_one("#menu-color"))
        await pilot.pause(0.1)
        # ColorPicker가 표시되어야 함
        assert len(app.query(ColorPicker)) == 1
        # 파란색 선택
        picker = app.query_one(ColorPicker)
        await pilot.click(picker.query_one("#color-blue"))
        await pilot.pause(0.1)
        # 스티커 색상이 변경되어야 함
        loaded = tmp_storage.load(s.id)
        assert loaded.color == StickerColor.BLUE


@pytest.mark.asyncio
async def test_context_menu_buttons_have_text_color(tmp_storage):
    """ContextMenu CSS에 color: $text 가 있어야 버튼 텍스트가 보임."""
    from sticker0.widgets.context_menu import ContextMenu
    s = Sticker(title="Menu test")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        from sticker0.widgets.sticker_widget import StickerWidget
        widget = app.query_one(StickerWidget)
        await pilot.click(widget, button=3, offset=(5, 2))
        await pilot.pause(0.1)
        menu = app.query_one(ContextMenu)
        css = menu.DEFAULT_CSS
        assert "color: $text" in css


@pytest.mark.asyncio
async def test_app_has_no_header_or_footer(tmp_storage):
    from textual.widgets import Header, Footer
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        assert len(app.query(Header)) == 0
        assert len(app.query(Footer)) == 0


@pytest.mark.asyncio
async def test_focused_sticker_delete_with_d_key(tmp_storage):
    from sticker0.widgets.sticker_widget import StickerWidget
    s = Sticker(title="Press d")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        widget.focus()
        await pilot.pause(0.1)
        await pilot.press("d")
        await pilot.pause(0.1)
        assert len(app.query(StickerWidget)) == 0
        assert tmp_storage.load_all() == []


@pytest.mark.asyncio
async def test_empty_board_right_click_shows_board_menu(tmp_storage):
    """빈 보드 영역 우클릭 → BoardMenu 표시."""
    from sticker0.widgets.board_menu import BoardMenu
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        board = app.query_one("StickerBoard")
        await pilot.click(board, button=3, offset=(60, 20))
        await pilot.pause(0.1)
        assert len(app.query(BoardMenu)) == 1


@pytest.mark.asyncio
async def test_board_menu_create_adds_sticker(tmp_storage):
    """BoardMenu Create → 새 스티커 생성."""
    from sticker0.widgets.board_menu import BoardMenu
    from sticker0.widgets.sticker_widget import StickerWidget
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        board = app.query_one("StickerBoard")
        await pilot.click(board, button=3, offset=(60, 20))
        await pilot.pause(0.1)
        menu = app.query_one(BoardMenu)
        await pilot.click(menu.query_one("#board-create"))
        await pilot.pause(0.1)
        assert len(app.query(StickerWidget)) == 1
        assert len(tmp_storage.load_all()) == 1


@pytest.mark.asyncio
async def test_board_menu_quit_exits_app(tmp_storage):
    """BoardMenu Quit → 앱 종료."""
    from sticker0.widgets.board_menu import BoardMenu
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        board = app.query_one("StickerBoard")
        await pilot.click(board, button=3, offset=(60, 20))
        await pilot.pause(0.1)
        menu = app.query_one(BoardMenu)
        await pilot.click(menu.query_one("#board-quit"))
        await pilot.pause(0.1)
    assert not app.is_running
