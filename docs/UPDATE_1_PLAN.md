# sticker0 Update 1 Implementation Plan

> **Documentation note:** 키보드 `q` 종료·`d`/Delete 삭제는 제거되었습니다. 종료/삭제는 우클릭 메뉴를 사용합니다. 아래 스니펫의 `bind(kb.quit, …)`, `on_key`의 `d`/`delete`, `q` 키 체크리스트는 과거 초안일 수 있습니다.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** v0.1.0의 UX를 개선하여 v0.2.0으로 업그레이드 한다 — 헤더/푸터 제거, 전체화면 보드, 단일 클릭 즉시 편집, 투명 배경, 테두리 역할 분리, z-index, 빈 영역 우클릭 메뉴, ContextMenu 버그 수정.

**Architecture:** 기존 Textual App 구조 유지. StickerWidget을 대폭 수정하여 항상 TextArea로 렌더링, 보드 빈 영역 우클릭에 새 BoardMenu 위젯 추가, app.py에서 Header/Footer 제거.

**Tech Stack:** Python ≥ 3.11, Textual ≥ 0.80, pytest + pytest-asyncio

---

## File Map

| 파일 | 변경 유형 | 내용 |
|------|-----------|------|
| `src/sticker0/sticker.py` | 수정 | `StickerColor.NONE = "none"` 추가, `from_dict` 기본값 "none"으로 변경 |
| `src/sticker0/widgets/color_picker.py` | 수정 | 투명(NONE) 옵션 추가 |
| `src/sticker0/widgets/context_menu.py` | 수정 | 버튼 CSS에 `color: $text` 추가 (텍스트 미표시 버그 수정) |
| `src/sticker0/app.py` | 수정 | Header/Footer 제거, imports 정리 |
| `src/sticker0/widgets/sticker_widget.py` | 대폭 수정 | 항상 TextArea, 단일 클릭 편집, 테두리 역할 분리, z-index, 투명 배경 |
| `src/sticker0/widgets/board_menu.py` | 신규 | BoardMenu 위젯 (Create / 색상 테마 / Quit) |
| `src/sticker0/widgets/board.py` | 수정 | 빈 영역 우클릭 → BoardMenu 표시, `add_new_sticker` 위치 파라미터 추가 |
| `tests/test_app.py` | 수정 | 새 동작에 맞게 테스트 업데이트 |

---

## Task 1: StickerColor.NONE 투명 색상 추가

**Files:**
- Modify: `src/sticker0/sticker.py`
- Modify: `src/sticker0/widgets/color_picker.py`
- Test: `tests/test_sticker.py`

- [ ] **Step 1: 실패 테스트 작성**

`tests/test_sticker.py` 에 추가:

```python
def test_sticker_color_none_roundtrip():
    from sticker0.sticker import StickerColor
    s = Sticker(color=StickerColor.NONE)
    d = s.to_dict()
    assert d["color"] == "none"
    s2 = Sticker.from_dict(d)
    assert s2.color == StickerColor.NONE

def test_new_sticker_default_color_is_none():
    from sticker0.sticker import StickerColor
    s = Sticker()
    assert s.color == StickerColor.NONE
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_sticker.py::test_sticker_color_none_roundtrip tests/test_sticker.py::test_new_sticker_default_color_is_none -v
```

Expected: FAIL (StickerColor.NONE 미존재)

- [ ] **Step 3: sticker.py 수정**

`StickerColor` 열거형에 `NONE` 추가, `Sticker.color` 기본값 변경:

```python
class StickerColor(str, Enum):
    YELLOW = "yellow"
    BLUE = "blue"
    GREEN = "green"
    PINK = "pink"
    WHITE = "white"
    DARK = "dark"
    NONE = "none"
```

`Sticker` dataclass의 color 필드 기본값:

```python
color: StickerColor = StickerColor.NONE
```

`from_dict` 메서드의 기본값:

```python
color=StickerColor(data.get("color", "none")),
```

- [ ] **Step 4: color_picker.py 수정**

`COLOR_LABELS` 딕셔너리에 `NONE` 추가:

```python
from sticker0.sticker import StickerColor

COLOR_LABELS: dict[StickerColor, str] = {
    StickerColor.NONE:   "⬜ 투명 (기본)",
    StickerColor.YELLOW: "🟡 노랑",
    StickerColor.BLUE:   "🔵 파랑",
    StickerColor.GREEN:  "🟢 초록",
    StickerColor.PINK:   "🩷 분홍",
    StickerColor.WHITE:  "⬜ 흰색",
    StickerColor.DARK:   "⬛ 어두움",
}
```

- [ ] **Step 5: 테스트 통과 확인**

```bash
uv run pytest tests/test_sticker.py -v
```

Expected: All tests PASSED

- [ ] **Step 6: 기존 테스트 영향 확인**

`tests/test_sticker.py`의 `test_sticker_defaults` 가 `color == StickerColor.YELLOW`를 확인하므로, 이를 `StickerColor.NONE`으로 업데이트:

```python
def test_sticker_defaults():
    s = Sticker()
    assert s.title == ""
    assert s.content == ""
    assert s.color == StickerColor.NONE   # YELLOW → NONE
    assert s.border == BorderType.ROUNDED
    assert s.position.x == 0
    assert s.position.y == 0
    assert s.size.width == 30
    assert s.size.height == 10
    assert s.id != ""
```

- [ ] **Step 7: config.py 기본값 수정**

`src/sticker0/config.py`의 `ThemeConfig` 기본값:

```python
@dataclass
class ThemeConfig:
    default_color: StickerColor = StickerColor.NONE
```

`tests/test_config.py`의 `test_defaults_when_no_file` 업데이트:

```python
def test_defaults_when_no_file(tmp_path):
    config = AppConfig.load(path=tmp_path / ".stkrc")
    assert config.theme.default_color == StickerColor.NONE  # YELLOW → NONE
    ...
```

- [ ] **Step 8: 전체 테스트 통과 확인**

```bash
uv run pytest -v
```

Expected: All tests PASSED

- [ ] **Step 9: Commit**

```bash
git add src/sticker0/sticker.py src/sticker0/widgets/color_picker.py \
        src/sticker0/config.py tests/test_sticker.py tests/test_config.py
git commit -m "feat: add StickerColor.NONE transparent option, change default color"
```

---

## Task 2: ContextMenu 텍스트 미표시 버그 수정

**Files:**
- Modify: `src/sticker0/widgets/context_menu.py`

- [ ] **Step 1: 버그 재현 테스트 작성**

`tests/test_app.py`에 추가:

```python
@pytest.mark.asyncio
async def test_context_menu_buttons_have_text_color(tmp_storage):
    from sticker0.widgets.context_menu import ContextMenu
    from textual.widgets import Button
    s = Sticker(title="Menu test")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        from sticker0.widgets.sticker_widget import StickerWidget
        widget = app.query_one(StickerWidget)
        await pilot.click(widget, button=3, offset=(5, 2))
        await pilot.pause(0.1)
        menu = app.query_one(ContextMenu)
        # ContextMenu CSS에 color: $text 가 있어야 버튼 텍스트가 보임
        css = menu.DEFAULT_CSS
        assert "color: $text" in css
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_app.py::test_context_menu_buttons_have_text_color -v
```

Expected: FAIL (CSS에 `color: $text` 없음)

- [ ] **Step 3: context_menu.py CSS 수정**

`ContextMenu.DEFAULT_CSS`의 버튼 규칙에 `color: $text` 및 `background: $surface` 명시:

```python
DEFAULT_CSS = """
ContextMenu {
    position: absolute;
    width: 20;
    height: auto;
    border: round $accent;
    background: $surface;
    color: $text;
    layer: menu;
}
ContextMenu Button {
    width: 1fr;
    height: 1;
    border: none;
    background: transparent;
    color: $text;
}
ContextMenu Button:hover {
    background: $accent 20%;
}
"""
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
uv run pytest tests/test_app.py::test_context_menu_buttons_have_text_color -v
```

Expected: PASSED

- [ ] **Step 5: Commit**

```bash
git add src/sticker0/widgets/context_menu.py tests/test_app.py
git commit -m "fix: add explicit color: \$text to ContextMenu to fix invisible button text"
```

---

## Task 3: Header/Footer 제거

**Files:**
- Modify: `src/sticker0/app.py`

현재 `app.py`:
```python
from textual.widgets import Header, Footer
...
def compose(self) -> ComposeResult:
    yield Header(show_clock=True)
    yield StickerBoard(storage=self.storage, config=self.config)
    yield Footer()
```

- [ ] **Step 1: Header/Footer 미존재 테스트 작성**

`tests/test_app.py`에 추가:

```python
@pytest.mark.asyncio
async def test_app_has_no_header_or_footer(tmp_storage):
    from textual.widgets import Header, Footer
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        assert len(app.query(Header)) == 0
        assert len(app.query(Footer)) == 0
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_app.py::test_app_has_no_header_or_footer -v
```

Expected: FAIL (Header/Footer 존재함)

- [ ] **Step 3: app.py 수정**

```python
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
        self.bind(kb.quit, "quit", description="종료")

    def action_new_sticker(self) -> None:
        self.query_one(StickerBoard).add_new_sticker()

    def action_quit(self) -> None:
        self.exit()
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
uv run pytest tests/test_app.py -v
```

Expected: All tests PASSED (기존 테스트도 통과해야 함)

- [ ] **Step 5: Commit**

```bash
git add src/sticker0/app.py tests/test_app.py
git commit -m "feat: remove Header and Footer for fullscreen board"
```

---

## Task 4: StickerWidget 대폭 수정

**Files:**
- Modify: `src/sticker0/widgets/sticker_widget.py`

변경 사항:
1. `_editing` 플래그, `DOUBLE_CLICK_INTERVAL`, `_enter_edit_mode` / `_exit_edit_mode` 제거
2. `compose()`: `Static` 타이틀 제거 → `TextArea` 하나만 렌더링
3. 단일 클릭 즉시 편집 (TextArea 항상 렌더링, 포커스로 편집)
4. `TextArea.Changed` → 내용 저장
5. 테두리 역할 분리: `y==0` = 이동 드래그, `x==0`/`x==width-1` = 가로 리사이즈, `y==height-1` = 세로 리사이즈
6. z-index: `on_mouse_down` 시 `self.move_to_front()`
7. 투명 배경: `StickerColor.NONE` → `background: transparent`
8. `_enter_edit_mode`: TextArea 포커스 부여로 단순화

**Border 검출 로직 주의사항:**
- Textual에서 `event.x`, `event.y`는 위젯 내부 좌표 (border 포함 전체 크기 기준)
- `self.size.width` / `self.size.height` = 위젯 전체 크기 (border 포함)
- `y == 0` = 최상단 줄 (border 위치)

- [ ] **Step 1: 단일 클릭 편집 테스트 작성**

`tests/test_app.py`에서 기존 `test_double_click_enters_edit_mode` 를 교체:

```python
@pytest.mark.asyncio
async def test_single_click_focuses_textarea(tmp_storage):
    """단일 클릭으로 TextArea에 포커스 (내용 편집 가능)."""
    from sticker0.widgets.sticker_widget import StickerWidget
    from textual.widgets import TextArea
    s = Sticker(title="Edit me", content="original")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        # 스티커 내부(테두리 아닌 영역) 클릭 - y=2는 내부 영역
        await pilot.click(widget, offset=(5, 2))
        await pilot.pause(0.1)
        # TextArea가 항상 존재해야 함
        assert len(app.query(TextArea)) >= 1

@pytest.mark.asyncio
async def test_textarea_always_present(tmp_storage):
    """TextArea는 항상 렌더링되어 있어야 함 (비편집 상태에서도)."""
    from sticker0.widgets.sticker_widget import StickerWidget
    from textual.widgets import TextArea
    s = Sticker(content="hello")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        assert len(app.query(TextArea)) == 1
```

- [ ] **Step 2: 저장 동작 테스트 작성**

`tests/test_app.py`에 추가:

```python
@pytest.mark.asyncio
async def test_textarea_content_saves_on_change(tmp_storage):
    """TextArea 내용 변경 시 스티커 데이터에 반영."""
    from sticker0.widgets.sticker_widget import StickerWidget
    from textual.widgets import TextArea
    s = Sticker(content="original")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        # TextArea에 포커스
        await pilot.click(widget, offset=(5, 2))
        await pilot.pause(0.1)
        # 텍스트 입력
        await pilot.press("a", "b", "c")
        await pilot.pause(0.1)
        # 스티커 내용이 변경되어야 함
        assert "abc" in widget.sticker.content
```

- [ ] **Step 3: z-index 테스트 작성**

`tests/test_app.py`에 추가:

```python
@pytest.mark.asyncio
async def test_click_brings_sticker_to_front(tmp_storage):
    """스티커 클릭 시 DOM 마지막 순서로 이동 (z-index)."""
    from sticker0.widgets.sticker_widget import StickerWidget
    s1 = Sticker(content="first")
    s2 = Sticker(content="second")
    tmp_storage.save(s1)
    tmp_storage.save(s2)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widgets = list(app.query(StickerWidget))
        assert len(widgets) == 2
        first_widget = widgets[0]
        # 첫 번째 스티커의 상단 테두리(y=0) 클릭 → 앞으로 이동
        await pilot.mouse_down(first_widget, offset=(2, 0))
        await pilot.mouse_up(first_widget, offset=(2, 0))
        await pilot.pause(0.1)
        # 클릭된 위젯이 마지막 자식이어야 함 (최상단 렌더링)
        board = app.query_one("StickerBoard")
        last_widget = list(board.query(StickerWidget))[-1]
        assert last_widget.sticker.id == first_widget.sticker.id
```

- [ ] **Step 4: 리사이즈 테스트 업데이트**

기존 `test_sticker_resize_from_corner`를 새 border 역할로 교체 (우측 border 드래그 → 가로 크기 변경):

```python
@pytest.mark.asyncio
async def test_sticker_resize_right_border(tmp_storage):
    """우측 border 드래그 → 가로 크기 변경."""
    from sticker0.widgets.sticker_widget import StickerWidget
    s = Sticker(content="Resize me")
    s.size.width = 30
    s.size.height = 10
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        # 우측 border: x == width - 1
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
    """하단 border 드래그 → 세로 크기 변경."""
    from sticker0.widgets.sticker_widget import StickerWidget
    s = Sticker(content="Resize me")
    s.size.width = 30
    s.size.height = 10
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        # 하단 border: y == height - 1
        bottom_border_y = s.size.height - 1
        mid_x = s.size.width // 2
        await pilot.mouse_down(widget, offset=(mid_x, bottom_border_y))
        mid_screen_x = widget.region.x + mid_x
        bottom_screen_y = widget.region.y + bottom_border_y
        await pilot.mouse_up(offset=(mid_screen_x, bottom_screen_y + 5))
        await pilot.pause(0.1)
        assert widget.sticker.size.height == 15
```

- [ ] **Step 5: 실패 확인**

```bash
uv run pytest tests/test_app.py::test_textarea_always_present \
             tests/test_app.py::test_click_brings_sticker_to_front \
             tests/test_app.py::test_sticker_resize_right_border -v
```

Expected: FAIL

- [ ] **Step 6: StickerWidget 완전 재작성**

```python
# src/sticker0/widgets/sticker_widget.py
from __future__ import annotations
from textual.widget import Widget
from textual.widgets import TextArea
from textual.app import ComposeResult
from textual.events import MouseDown, MouseMove, MouseUp
from sticker0.sticker import Sticker, StickerColor, BorderType

COLOR_MAP: dict[StickerColor, tuple[str, str]] = {
    StickerColor.YELLOW: ("#000000", "#ffeb3b"),
    StickerColor.BLUE:   ("#ffffff", "#1565c0"),
    StickerColor.GREEN:  ("#000000", "#4caf50"),
    StickerColor.PINK:   ("#000000", "#f48fb1"),
    StickerColor.WHITE:  ("#000000", "#ffffff"),
    StickerColor.DARK:   ("#ffffff", "#212121"),
    StickerColor.NONE:   ("", ""),  # 투명
}

BORDER_MAP: dict[BorderType, str] = {
    BorderType.ROUNDED: "round",
    BorderType.SHARP:   "solid",
    BorderType.DOUBLE:  "double",
    BorderType.THICK:   "heavy",
    BorderType.ASCII:   "ascii",
}

_DRAG_MOVE = "move"
_DRAG_RESIZE_W = "resize_w"
_DRAG_RESIZE_H = "resize_h"


class StickerWidget(Widget):
    DEFAULT_CSS = """
    StickerWidget {
        position: absolute;
        min-width: 20;
        min-height: 5;
        background: transparent;
    }
    StickerWidget TextArea {
        height: 1fr;
        background: transparent;
        border: none;
        padding: 0 1;
    }
    StickerWidget TextArea:focus {
        border: none;
    }
    """

    MIN_WIDTH = 20
    MIN_HEIGHT = 5
    can_focus = True

    def __init__(self, sticker: Sticker, **kwargs) -> None:
        super().__init__(**kwargs)
        self.sticker = sticker
        self._drag_start: tuple[int, int] | None = None
        self._drag_origin: tuple[int, int] = (0, 0)
        self._drag_mode: str = _DRAG_MOVE

    def on_mount(self) -> None:
        self._apply_sticker_styles()

    def _apply_sticker_styles(self) -> None:
        border_style = BORDER_MAP.get(self.sticker.border, "round")
        if self.sticker.color == StickerColor.NONE:
            self.styles.background = "transparent"
            self.styles.border = (border_style, "")
        else:
            text_color, bg_color = COLOR_MAP.get(
                self.sticker.color, ("#000000", "#ffeb3b")
            )
            self.styles.background = bg_color
            self.styles.color = text_color
            self.styles.border = (border_style, text_color)
        # 상단 테두리: 드래그 핸들 시각 표시 (double)
        self.styles.border_top = ("double", "")
        self.styles.offset = (self.sticker.position.x, self.sticker.position.y)
        self.styles.width = self.sticker.size.width
        self.styles.height = self.sticker.size.height

    def compose(self) -> ComposeResult:
        editor_id = f"sticker-editor-{self.sticker.id}"
        yield TextArea(self.sticker.content, id=editor_id)

    def _get_editor(self) -> TextArea:
        return self.query_one(f"#sticker-editor-{self.sticker.id}", TextArea)

    def _classify_border(self, x: int, y: int) -> str | None:
        """클릭 좌표가 어느 border 영역인지 반환. 내부면 None."""
        w = self.size.width
        h = self.size.height
        if y == 0:
            return _DRAG_MOVE
        if x == 0 or x == w - 1:
            return _DRAG_RESIZE_W
        if y == h - 1:
            return _DRAG_RESIZE_H
        return None

    def on_mouse_down(self, event: MouseDown) -> None:
        # z-index: 클릭 시 최상단 이동
        self.move_to_front()

        mode = self._classify_border(event.x, event.y)
        if mode is None:
            # 내부 영역: TextArea가 처리하도록 위임
            return

        event.stop()
        self._drag_start = (event.screen_x, event.screen_y)
        self._drag_mode = mode
        if mode == _DRAG_MOVE:
            self._drag_origin = (self.sticker.position.x, self.sticker.position.y)
        else:
            self._drag_origin = (self.sticker.size.width, self.sticker.size.height)
        self.capture_mouse()

    def on_mouse_move(self, event: MouseMove) -> None:
        if self._drag_start is None:
            return
        event.stop()
        dx = event.screen_x - self._drag_start[0]
        dy = event.screen_y - self._drag_start[1]
        self._apply_drag(dx, dy)

    def _apply_drag(self, dx: int, dy: int) -> None:
        if self._drag_mode == _DRAG_MOVE:
            new_x = max(0, self._drag_origin[0] + dx)
            new_y = max(0, self._drag_origin[1] + dy)
            self.sticker.position.x = new_x
            self.sticker.position.y = new_y
            self.styles.offset = (new_x, new_y)
        elif self._drag_mode == _DRAG_RESIZE_W:
            new_w = max(self.MIN_WIDTH, self._drag_origin[0] + dx)
            self.sticker.size.width = new_w
            self.styles.width = new_w
        elif self._drag_mode == _DRAG_RESIZE_H:
            new_h = max(self.MIN_HEIGHT, self._drag_origin[1] + dy)
            self.sticker.size.height = new_h
            self.styles.height = new_h

    def on_mouse_up(self, event: MouseUp) -> None:
        if event.button == 3:
            event.stop()
            self._drag_start = None
            self.release_mouse()
            self._show_context_menu(event.screen_x, event.screen_y)
            return
        if self._drag_start is not None:
            dx = event.screen_x - self._drag_start[0]
            dy = event.screen_y - self._drag_start[1]
            self._apply_drag(dx, dy)
            self._drag_start = None
            self.release_mouse()
            board = self.app.query_one("StickerBoard")
            board.save_sticker(self.sticker)

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """TextArea 내용 변경 시 즉시 저장."""
        self.sticker.content = event.text_area.text
        try:
            board = self.app.query_one("StickerBoard")
            board.save_sticker(self.sticker)
        except Exception:
            pass

    def _show_context_menu(self, screen_x: int, screen_y: int) -> None:
        from sticker0.widgets.context_menu import ContextMenu
        for menu in self.app.query(ContextMenu):
            menu.remove()
        board = self.app.query_one("StickerBoard")
        local_x = screen_x - board.region.x
        local_y = screen_y - board.region.y
        menu = ContextMenu(
            sticker_id=self.sticker.id,
            x=local_x,
            y=local_y,
        )
        board.mount(menu)

    def _enter_edit_mode(self) -> None:
        """편집 모드 진입: TextArea에 포커스 부여."""
        self._get_editor().focus()

    def on_key(self, event) -> None:
        """StickerWidget 자체에 포커스가 있을 때만 키 처리 (TextArea 포커스 시 제외)."""
        if event.key in ("d", "delete"):
            try:
                board = self.app.query_one("StickerBoard")
                board.delete_sticker(self.sticker.id)
            except Exception:
                pass
            event.stop()
        elif event.key == "enter":
            self._enter_edit_mode()
            event.stop()
```

**중요:** `board.py`에서 `_enter_edit_mode()` 호출부를 확인:

`src/sticker0/widgets/board.py`의 `on_context_menu_menu_action` 에서 `widget._enter_edit_mode()` 호출은 그대로 유지 (단순히 TextArea에 포커스 부여하므로 동작함).

- [ ] **Step 7: 테스트 통과 확인**

```bash
uv run pytest tests/test_app.py -v
```

Expected: All tests PASSED. 실패하는 이전 테스트:
- `test_double_click_enters_edit_mode` → `test_single_click_focuses_textarea`로 교체됨
- `test_escape_exits_edit_mode` → 제거됨 (더 이상 _editing 상태 없음)
- `test_sticker_resize_from_corner` → `test_sticker_resize_right_border`, `test_sticker_resize_bottom_border`로 교체됨

이전 테스트 제거:
```python
# tests/test_app.py 에서 아래 함수들 삭제:
# - test_double_click_enters_edit_mode
# - test_escape_exits_edit_mode
# - test_sticker_resize_from_corner
# - test_focused_sticker_enter_opens_edit (있다면)
```

- [ ] **Step 8: Commit**

```bash
git add src/sticker0/widgets/sticker_widget.py tests/test_app.py
git commit -m "feat: rewrite StickerWidget — always-on TextArea, single-click edit, border role separation, z-index, transparent bg"
```

---

## Task 5: BoardMenu + 빈 영역 우클릭

**Files:**
- Create: `src/sticker0/widgets/board_menu.py`
- Modify: `src/sticker0/widgets/board.py`

- [ ] **Step 1: BoardMenu 테스트 작성**

`tests/test_app.py`에 추가:

```python
@pytest.mark.asyncio
async def test_empty_board_right_click_shows_board_menu(tmp_storage):
    """빈 보드 영역 우클릭 → BoardMenu 표시."""
    from sticker0.widgets.board_menu import BoardMenu
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        board = app.query_one("StickerBoard")
        # 스티커가 없는 빈 영역에서 우클릭
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
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_app.py::test_empty_board_right_click_shows_board_menu -v
```

Expected: FAIL (BoardMenu 미존재)

- [ ] **Step 3: board_menu.py 작성**

```python
# src/sticker0/widgets/board_menu.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Button
from textual.message import Message


class BoardMenu(Widget):
    """빈 보드 영역 우클릭 팝업 메뉴."""

    DEFAULT_CSS = """
    BoardMenu {
        position: absolute;
        width: 24;
        height: auto;
        border: round $accent;
        background: $surface;
        color: $text;
        layer: menu;
    }
    BoardMenu Button {
        width: 1fr;
        height: 1;
        border: none;
        background: transparent;
        color: $text;
    }
    BoardMenu Button:hover {
        background: $accent 20%;
    }
    """

    class MenuAction(Message):
        def __init__(self, action: str, x: int = 0, y: int = 0) -> None:
            super().__init__()
            self.action = action
            self.x = x
            self.y = y

    def __init__(self, x: int, y: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self._menu_x = x
        self._menu_y = y

    def on_mount(self) -> None:
        self.styles.offset = (self._menu_x, self._menu_y)

    def compose(self) -> ComposeResult:
        yield Button("✨ Create", id="board-create")
        yield Button("🎨 색상 테마 변경", id="board-theme")
        yield Button("✖ Quit", id="board-quit")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        action_map = {
            "board-create": "create",
            "board-theme": "theme",
            "board-quit": "quit",
        }
        action = action_map.get(event.button.id or "", "")
        if action:
            self.post_message(
                self.MenuAction(action, x=self._menu_x, y=self._menu_y)
            )
        self.remove()
```

- [ ] **Step 4: board.py 수정**

`add_new_sticker` 메서드에 선택적 위치 파라미터 추가, `on_mouse_up`으로 빈 영역 우클릭 감지, BoardMenu 메시지 처리:

```python
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

    def on_mouse_up(self, event: MouseUp) -> None:
        """빈 영역 우클릭 감지 (StickerWidget이 stop하지 않은 경우)."""
        if event.button == 3:
            from sticker0.widgets.board_menu import BoardMenu
            from sticker0.widgets.context_menu import ContextMenu
            # 기존 메뉴 모두 닫기
            for menu in self.query(BoardMenu):
                menu.remove()
            for menu in self.query(ContextMenu):
                menu.remove()
            menu = BoardMenu(x=event.x, y=event.y)
            self.mount(menu)

    def on_board_menu_menu_action(self, message) -> None:
        from sticker0.widgets.board_menu import BoardMenu
        if message.action == "create":
            self.add_new_sticker(x=message.x, y=message.y)
        elif message.action == "quit":
            self.app.exit()
        # "theme" is reserved for future use

    def on_context_menu_menu_action(self, message) -> None:
        if message.action == "delete":
            self.delete_sticker(message.sticker_id)
        elif message.action == "edit":
            for widget in self.query(StickerWidget):
                if widget.sticker.id == message.sticker_id:
                    widget._enter_edit_mode()
        elif message.action == "color":
            from sticker0.widgets.color_picker import ColorPicker
            for picker in self.query(ColorPicker):
                picker.remove()
            picker = ColorPicker(
                sticker_id=message.sticker_id,
                x=22,
                y=3,
            )
            self.mount(picker)

    def on_color_picker_color_selected(self, message) -> None:
        from sticker0.widgets.color_picker import ColorPicker
        for widget in self.query(StickerWidget):
            if widget.sticker.id == message.sticker_id:
                widget.sticker.color = message.color
                widget._apply_sticker_styles()
                widget.refresh()
                self.storage.save(widget.sticker)
                break
```

- [ ] **Step 5: 테스트 통과 확인**

```bash
uv run pytest tests/test_app.py -v
```

Expected: All tests PASSED

- [ ] **Step 6: Commit**

```bash
git add src/sticker0/widgets/board_menu.py src/sticker0/widgets/board.py \
        tests/test_app.py
git commit -m "feat: add BoardMenu for empty area right-click with Create/Theme/Quit"
```

---

## Task 6: 버전 업데이트 및 최종 검증

**Files:**
- Modify: `pyproject.toml`
- Modify: `src/sticker0/__init__.py`

- [ ] **Step 1: 버전 업데이트**

`pyproject.toml`:
```toml
version = "0.2.0"
```

`src/sticker0/__init__.py`:
```python
__version__ = "0.2.0"
```

- [ ] **Step 2: 전체 테스트 통과 확인**

```bash
uv run pytest -v --tb=short
```

Expected: All tests PASSED

- [ ] **Step 3: 수동 동작 확인**

```bash
uv run stk
```

체크리스트:
- [ ] 헤더/푸터 없이 전체화면 보드
- [ ] `n` 키로 투명 스티커 생성
- [ ] 스티커 상단 테두리(═══) 드래그로 이동
- [ ] 우측/좌측 테두리 드래그로 가로 크기 조절
- [ ] 하단 테두리 드래그로 세로 크기 조절
- [ ] 스티커 내부 클릭 → 즉시 편집 가능
- [ ] 겹치는 스티커 클릭 → 최상단으로
- [ ] 빈 영역 우클릭 → BoardMenu (Create/색상 테마/Quit)
- [ ] 스티커 우클릭 → ContextMenu (텍스트 표시 확인)
- [ ] ContextMenu 색상 변경 → 투명 포함 7가지 색상
- [ ] `q` 키로 종료 후 재실행 → 스티커 복원

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml src/sticker0/__init__.py
git commit -m "chore: bump version to v0.2.0"
```

---

## Verification

### 전체 테스트

```bash
uv run pytest -v
```

Expected: All tests PASSED

### 주요 API 참고

- `config.border.border_type` (NOT `.type`)
- `StickerColor.NONE = "none"` (투명)
- `Widget.move_to_front()` — z-index 최상단 이동
- `TextArea.Changed` — 내용 변경 이벤트
- BoardMenu는 `StickerWidget.on_mouse_up(button==3)` 이 stop하지 않은 우클릭에만 응답
- `add_new_sticker(x, y)` — 위치 지정 생성 지원
