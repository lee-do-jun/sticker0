# tests/test_app.py
import pytest
from sticker0.app import Sticker0App
from sticker0.sticker import Sticker, StickerColors
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
async def test_sticker_widget_renders(tmp_storage):
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
        await pilot.mouse_down(widget, offset=(2, 0))
        await pilot.pause()
        await pilot.mouse_up(offset=(17, 10))
        await pilot.pause()
        assert widget.sticker.position.x == 15
        assert widget.sticker.position.y == 10


@pytest.mark.asyncio
async def test_textarea_always_present(tmp_storage):
    from textual.widgets import TextArea
    s = Sticker(content="hello")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        assert len(app.query(TextArea)) == 1


@pytest.mark.asyncio
async def test_textarea_content_saves_on_change(tmp_storage):
    from sticker0.widgets.sticker_widget import StickerWidget
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
async def test_sticker_resize_corner_br(tmp_storage):
    """아래·오른쪽 2열 겹침 영역: 가로·세로 동시 리사이즈."""
    from sticker0.widgets.sticker_widget import StickerWidget

    s = Sticker(content="corner")
    s.size.width = 30
    s.size.height = 10
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        br_x = s.size.width - 1
        br_y = s.size.height - 1
        await pilot.mouse_down(widget, offset=(br_x, br_y))
        await pilot.mouse_up(
            offset=(widget.region.x + br_x + 5, widget.region.y + br_y + 5)
        )
        await pilot.pause(0.1)
        assert widget.sticker.size.width == 35
        assert widget.sticker.size.height == 15


@pytest.mark.asyncio
async def test_click_brings_sticker_to_front(tmp_storage):
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
async def test_preset_change_via_context_menu(tmp_storage):
    """우클릭 → 프리셋 변경 → Banana 선택 → 색상 변경 확인."""
    from sticker0.widgets.sticker_widget import StickerWidget
    from sticker0.widgets.preset_picker import PresetPicker
    s = Sticker(title="Preset test")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        await pilot.click(widget, button=3, offset=(5, 2))
        await pilot.pause(0.1)
        from sticker0.widgets.context_menu import ContextMenu
        menu = app.query_one(ContextMenu)
        await pilot.click(menu.query_one("#menu-preset"))
        await pilot.pause(0.1)
        assert len(app.query(PresetPicker)) == 1
        picker = app.query_one(PresetPicker)
        await pilot.click(picker.query_one("#preset-Banana"))
        await pilot.pause(0.1)
        loaded = tmp_storage.load(s.id)
        assert loaded.colors.border == "black"
        assert loaded.colors.text == "black"
        assert loaded.colors.area == "#ffeb3b"


@pytest.mark.asyncio
async def test_context_menu_has_visible_text(tmp_storage):
    """ContextMenu 텍스트가 동적 indicator 색상으로 표시됨."""
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
        # indicator 색상이 동적으로 적용되어야 함 (on_mount에서 self.styles.color 설정)
        assert menu._indicator != ""


@pytest.mark.asyncio
async def test_app_has_no_header_or_footer(tmp_storage):
    from textual.widgets import Header, Footer
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        assert len(app.query(Header)) == 0
        assert len(app.query(Footer)) == 0


@pytest.mark.asyncio
async def test_empty_board_right_click_shows_board_menu(tmp_storage):
    from sticker0.widgets.board_menu import BoardMenu
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        board = app.query_one("StickerBoard")
        await pilot.click(board, button=3, offset=(60, 20))
        await pilot.pause(0.1)
        assert len(app.query(BoardMenu)) == 1


@pytest.mark.asyncio
async def test_board_menu_create_adds_sticker(tmp_storage):
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


@pytest.mark.asyncio
async def test_board_theme_change(tmp_storage):
    """보드 테마 변경 → 배경색 + indicator 변경 확인."""
    from sticker0.widgets.board_menu import BoardMenu
    from sticker0.widgets.theme_picker import ThemePicker
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        board = app.query_one("StickerBoard")
        await pilot.click(board, button=3, offset=(60, 20))
        await pilot.pause(0.1)
        menu = app.query_one(BoardMenu)
        await pilot.click(menu.query_one("#board-theme"))
        await pilot.pause(0.1)
        assert len(app.query(ThemePicker)) == 1
        picker = app.query_one(ThemePicker)
        await pilot.click(picker.query_one("#theme-Graphite"))
        await pilot.pause(0.1)
        assert board.board_bg == "#1e1e22"
        assert board.indicator == "#d4d4d8"


@pytest.mark.asyncio
async def test_minimize_via_context_menu(tmp_storage):
    """우클릭 → 최소화 → 높이 3줄 + 최소화 상태."""
    from sticker0.widgets.sticker_widget import StickerWidget
    from sticker0.widgets.context_menu import ContextMenu
    s = Sticker(content="Hello\nWorld\nLine3")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        await pilot.click(widget, button=3, offset=(5, 2))
        await pilot.pause(0.1)
        menu = app.query_one(ContextMenu)
        await pilot.click(menu.query_one("#menu-minimize"))
        await pilot.pause(0.1)
        assert widget.sticker.minimized is True


@pytest.mark.asyncio
async def test_restore_via_context_menu(tmp_storage):
    """최소화 상태에서 우클릭 → 복원."""
    from sticker0.widgets.sticker_widget import StickerWidget
    from sticker0.widgets.context_menu import ContextMenu
    s = Sticker(content="Hello", minimized=True)
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        await pilot.click(widget, button=3, offset=(5, 0))
        await pilot.pause(0.1)
        menu = app.query_one(ContextMenu)
        await pilot.click(menu.query_one("#menu-restore"))
        await pilot.pause(0.1)
        assert widget.sticker.minimized is False


@pytest.mark.asyncio
async def test_menu_mutual_exclusion(tmp_storage):
    """스티커 메뉴와 보드 메뉴는 동시에 존재할 수 없음."""
    from sticker0.widgets.sticker_widget import StickerWidget
    from sticker0.widgets.context_menu import ContextMenu
    from sticker0.widgets.board_menu import BoardMenu
    s = Sticker(content="test")
    s.position.x = 0
    s.position.y = 0
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        # 스티커 우클릭 → ContextMenu
        await pilot.click(widget, button=3, offset=(5, 2))
        await pilot.pause(0.1)
        assert len(app.query(ContextMenu)) == 1
        # 보드 빈 영역 우클릭 → BoardMenu (ContextMenu는 닫혀야 함)
        board = app.query_one("StickerBoard")
        await pilot.click(board, button=3, offset=(100, 30))
        await pilot.pause(0.1)
        assert len(app.query(ContextMenu)) == 0
        assert len(app.query(BoardMenu)) == 1


@pytest.mark.asyncio
async def test_popup_menus_close_on_left_click_outside(tmp_storage):
    """보드 빈 영역 또는 스티커 좌클릭 시 ContextMenu·BoardMenu가 닫힘."""
    from sticker0.widgets.sticker_widget import StickerWidget
    from sticker0.widgets.context_menu import ContextMenu
    from sticker0.widgets.board_menu import BoardMenu
    s = Sticker(content="test")
    s.position.x = 0
    s.position.y = 0
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        board = app.query_one("StickerBoard")
        await pilot.click(widget, button=3, offset=(5, 2))
        await pilot.pause(0.1)
        assert len(app.query(ContextMenu)) == 1
        await pilot.click(board, button=1, offset=(100, 30))
        await pilot.pause(0.1)
        assert len(app.query(ContextMenu)) == 0

        await pilot.click(board, button=3, offset=(50, 30))
        await pilot.pause(0.1)
        assert len(app.query(BoardMenu)) == 1
        await pilot.click(board, button=1, offset=(100, 30))
        await pilot.pause(0.1)
        assert len(app.query(BoardMenu)) == 0

        await pilot.click(board, button=3, offset=(50, 30))
        await pilot.pause(0.1)
        assert len(app.query(BoardMenu)) == 1
        await pilot.click(widget, button=1, offset=(15, 5))
        await pilot.pause(0.1)
        assert len(app.query(BoardMenu)) == 0


@pytest.mark.asyncio
async def test_new_sticker_uses_theme_default_colors(tmp_storage):
    """새 스티커 색은 로드된 config.board_theme 스티커 기본값과 일치."""
    from sticker0.widgets.sticker_widget import StickerWidget

    app = Sticker0App(storage=tmp_storage)
    bt = app.config.board_theme
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("n")
        await pilot.pause(0.1)
        widget = app.query_one(StickerWidget)
        assert widget.sticker.colors.border == bt.sticker_border
        assert widget.sticker.colors.text == bt.sticker_text
        assert widget.sticker.colors.area == bt.sticker_area
