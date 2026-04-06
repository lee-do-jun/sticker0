# Sticker Copy/Paste (Context Menu) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 스티커 우클릭 `ContextMenu`에 Copy·Paste를 추가하고, 본문을 OS 클립보드와 동기화한다(명세: `requirements/sticker-copy-paste.md`).

**Architecture:** `ContextMenu`가 `MenuAction("copy"|"paste", ...)`를 보내고, `StickerBoard.on_context_menu_menu_action`이 처리한다. OS 클립보드 **쓰기/읽기**는 Textual 단독으로는 불완전하다(`App.copy_to_clipboard`는 OSC 52 + 앱 내부 버퍼이며, `App.clipboard`는 **앱 안에서 복사한 값만** 보관한다). 따라서 **읽기(Paste)** 와 터미널 호환 **쓰기**를 위해 `pyperclip`로 OS 클립보드를 다루고, Copy 시에는 Textual `copy_to_clipboard`도 호출해 앱 내부 상태·OSC 52를 유지한다. `StickerWidget`에 본문 일괄 치환 메서드를 두어 `TextArea`·`sticker.content`·저장을 일관되게 맞춘다.

**Tech Stack:** Python 3.11+, Textual ≥ 0.80, `pyperclip`(신규 의존성), pytest, pytest-asyncio.

**Spec note (엣지):** Paste는 클립보드가 비어 있거나 읽기 실패 시 **아무 것도 하지 않음**. Copy는 본문이 비어도 **빈 문자열을 클립보드에 설정**.

---

## File map

| File | Role |
|------|------|
| `pyproject.toml` | `pyperclip` 의존성 추가 |
| `src/sticker0/system_clipboard.py` | OS 클립보드 read/write 헬퍼 (`read_os_clipboard_text`, `write_clipboard_from_app`) |
| `src/sticker0/widgets/context_menu.py` | Copy/Paste 버튼·`action_map` 확장 |
| `src/sticker0/widgets/board.py` | `on_context_menu_menu_action`에 `copy` / `paste` 분기 |
| `src/sticker0/widgets/sticker_widget.py` | `replace_body_text(self, text: str) -> None` (TextArea + `sticker.content`) |
| `tests/test_system_clipboard.py` | pyperclip 모킹 단위 테스트 |
| `tests/test_app.py` | 컨텍스트 메뉴 Copy/Paste 통합 테스트(모킹) |

---

### Task 1: `pyperclip` 의존성

**Files:**

- Modify: `pyproject.toml` (`dependencies` 리스트)
- Test: (없음 — 다음 태스크에서 import 검증)

- [ ] **Step 1: `dependencies`에 한 줄 추가**

```toml
dependencies = [
    "textual>=0.80",
    "pyperclip>=1.8",
]
```

- [ ] **Step 2: lock 동기화**

Run: `uv lock`  
Expected: 종료 코드 0, `uv.lock` 갱신

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "deps: add pyperclip for OS clipboard read/write"
```

---

### Task 2: `system_clipboard` 헬퍼

**Files:**

- Create: `src/sticker0/system_clipboard.py`
- Test: `tests/test_system_clipboard.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_system_clipboard.py`:

```python
from unittest.mock import MagicMock, patch

import pytest

from sticker0 import system_clipboard as sc


def test_read_os_clipboard_text_returns_none_when_empty_string() -> None:
    with patch("pyperclip.paste", return_value=""):
        assert sc.read_os_clipboard_text() is None


def test_read_os_clipboard_text_returns_none_on_pyperclip_error() -> None:
    with patch("pyperclip.paste", side_effect=RuntimeError("no clipboard")):
        assert sc.read_os_clipboard_text() is None


def test_read_os_clipboard_text_returns_str_when_non_str_paste() -> None:
    with patch("pyperclip.paste", return_value=123):
        assert sc.read_os_clipboard_text() == "123"


def test_write_clipboard_from_app_calls_pyperclip_and_app() -> None:
    app = MagicMock()
    with patch("pyperclip.copy") as mock_copy:
        sc.write_clipboard_from_app(app, "hello")
    mock_copy.assert_called_once_with("hello")
    app.copy_to_clipboard.assert_called_once_with("hello")


def test_write_clipboard_from_app_still_calls_app_when_pyperclip_fails() -> None:
    app = MagicMock()
    with patch("pyperclip.copy", side_effect=OSError("denied")):
        sc.write_clipboard_from_app(app, "x")
    app.copy_to_clipboard.assert_called_once_with("x")
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `uv run pytest tests/test_system_clipboard.py -v`  
Expected: `ModuleNotFoundError` or import error for `system_clipboard`

- [ ] **Step 3: Minimal implementation**

`src/sticker0/system_clipboard.py`:

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import App


def read_os_clipboard_text() -> str | None:
    """OS 클립보드 텍스트. 비어 있거나 읽기 불가면 None."""

    try:
        import pyperclip

        raw = pyperclip.paste()
    except Exception:
        return None
    if not isinstance(raw, str):
        raw = str(raw)
    if raw == "":
        return None
    return raw


def write_clipboard_from_app(app: App, text: str) -> None:
    """OS 클립보드(pyperclip) + Textual OSC52/내부 버퍼."""

    try:
        import pyperclip

        pyperclip.copy(text)
    except Exception:
        pass
    app.copy_to_clipboard(text)
```

- [ ] **Step 4: Run tests — expect PASS**

Run: `uv run pytest tests/test_system_clipboard.py -v`  
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/sticker0/system_clipboard.py tests/test_system_clipboard.py
git commit -m "feat: OS clipboard helpers via pyperclip"
```

---

### Task 3: `StickerWidget.replace_body_text`

**Files:**

- Modify: `src/sticker0/widgets/sticker_widget.py` (`StickerWidget` 클래스 내 `_get_editor` 근처에 메서드 추가)
- Test: `tests/test_app.py` (Paste 통합 테스트에서 사용 — Task 5에서 추가 가능; 또는 여기서 소단위 테스트)

- [ ] **Step 1: 메서드 추가**

`sticker_widget.py`의 `def _get_editor(self) -> TextArea:` 바로 아래에 삽입:

```python
    def replace_body_text(self, text: str) -> None:
        """스티커 본문과 TextArea를 동일한 문자열로 맞춘다(저장은 호출부)."""

        self.sticker.content = text
        try:
            self._get_editor().text = text
        except NoMatches:
            pass
```

- [ ] **Step 2: Commit**

```bash
git add src/sticker0/widgets/sticker_widget.py
git commit -m "feat: StickerWidget.replace_body_text for paste"
```

---

### Task 4: `ContextMenu` 버튼·액션

**Files:**

- Modify: `src/sticker0/widgets/context_menu.py`

- [ ] **Step 1: `compose()`에 Copy/Paste 버튼 추가**

최소화/복원 버튼 **직후**, `Color` 앞에 두 줄을 넣는다(순서: Minimize|Expand, **Copy**, **Paste**, Color, Delete).

`if self._minimized:` 분기 안·밖 **양쪽**에 동일하게:

```python
            yield PrimaryOnlyButton(
                "Copy", id="menu-copy", menu_indicator=mi, menu_panel_bg=mb
            )
            yield PrimaryOnlyButton(
                "Paste", id="menu-paste", menu_indicator=mi, menu_panel_bg=mb
            )
```

- [ ] **Step 2: `action_map`에 매핑**

```python
        action_map = {
            "menu-delete": "delete",
            "menu-preset": "preset",
            "menu-minimize": "minimize",
            "menu-restore": "restore",
            "menu-copy": "copy",
            "menu-paste": "paste",
        }
```

- [ ] **Step 3: Commit**

```bash
git add src/sticker0/widgets/context_menu.py
git commit -m "feat: context menu Copy and Paste buttons"
```

---

### Task 5: `StickerBoard` 핸들러 + 통합 테스트

**Files:**

- Modify: `src/sticker0/widgets/board.py` (`on_context_menu_menu_action`에 분기 추가)
- Modify: `tests/test_app.py`

- [ ] **Step 1: Write failing integration tests**

`tests/test_app.py` 끝부분에 추가(기존 fixture `tmp_storage` 재사용). 파일 상단에 다음이 없으면 추가: `from textual.widgets import TextArea`.

```python
@pytest.mark.asyncio
async def test_context_menu_copy_writes_clipboard(tmp_storage):
    from unittest.mock import patch

    from sticker0.widgets.context_menu import ContextMenu
    from sticker0.widgets.sticker_widget import StickerWidget

    s = Sticker(content="note body")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        await pilot.click(widget, button=3, offset=(5, 2))
        await pilot.pause(0.1)
        menu = app.query_one(ContextMenu)
        with patch(
            "sticker0.widgets.board.write_clipboard_from_app"
        ) as mock_write:
            await pilot.click(menu.query_one("#menu-copy"))
            await pilot.pause(0.1)
        mock_write.assert_called_once()
        assert mock_write.call_args[0][1] == "note body"


@pytest.mark.asyncio
async def test_context_menu_paste_replaces_content(tmp_storage):
    from unittest.mock import patch

    from sticker0.widgets.context_menu import ContextMenu
    from sticker0.widgets.sticker_widget import StickerWidget

    s = Sticker(content="old")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        await pilot.click(widget, button=3, offset=(5, 2))
        await pilot.pause(0.1)
        menu = app.query_one(ContextMenu)
        with patch(
            "sticker0.widgets.board.read_os_clipboard_text",
            return_value="from-clip",
        ):
            await pilot.click(menu.query_one("#menu-paste"))
            await pilot.pause(0.1)
        assert widget.sticker.content == "from-clip"
        assert widget.query_one(TextArea).text == "from-clip"
        loaded = tmp_storage.load(s.id)
        assert loaded.content == "from-clip"


@pytest.mark.asyncio
async def test_context_menu_paste_noop_when_clipboard_empty(tmp_storage):
    from unittest.mock import patch

    from sticker0.widgets.context_menu import ContextMenu
    from sticker0.widgets.sticker_widget import StickerWidget

    s = Sticker(content="unchanged")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        await pilot.click(widget, button=3, offset=(5, 2))
        await pilot.pause(0.1)
        menu = app.query_one(ContextMenu)
        with patch("sticker0.widgets.board.read_os_clipboard_text", return_value=None):
            await pilot.click(menu.query_one("#menu-paste"))
            await pilot.pause(0.1)
        assert widget.sticker.content == "unchanged"
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `uv run pytest tests/test_app.py::test_context_menu_copy_writes_clipboard tests/test_app.py::test_context_menu_paste_replaces_content tests/test_app.py::test_context_menu_paste_noop_when_clipboard_empty -v`  
Expected: FAIL (mock 경로 미구현 또는 핸들러 없음)

- [ ] **Step 3: `board.py` 구현**

파일 상단 import 그룹에 추가:

```python
from sticker0.system_clipboard import read_os_clipboard_text, write_clipboard_from_app
```

`on_context_menu_menu_action`의 `if message.action == "delete":` **앞** 또는 `restore` 분기 **뒤**에 다음을 추가한다(`StickerWidget`는 이미 파일 상단에서 import됨):

```python
        if message.action == "copy":
            for widget in self.query(StickerWidget):
                if widget.sticker.id == message.sticker_id:
                    write_clipboard_from_app(self.app, widget.sticker.content)
                    break
        elif message.action == "paste":
            clip = read_os_clipboard_text()
            if clip is None:
                return
            for widget in self.query(StickerWidget):
                if widget.sticker.id == message.sticker_id:
                    widget.replace_body_text(clip)
                    self.save_sticker(widget.sticker)
                    break
```

- [ ] **Step 4: 전체 테스트**

Run: `uv run pytest -v`  
Expected: 전부 통과

- [ ] **Step 5: Commit**

```bash
git add src/sticker0/widgets/board.py tests/test_app.py
git commit -m "feat: context menu copy/paste via OS clipboard"
```

---

### Task 6: 위젯 문서 한 줄 (선택, YAGNI)

명세에 이미 액션 목록이 없다면 `src/sticker0/widgets/CLAUDE.md`의 ContextMenu 표에 `"copy"`, `"paste"` 한 줄 추가만 한다. **분량이 커지면 생략 가능.**

---

## Self-review

**1. Spec coverage**

| Requirement | Task |
|-------------|------|
| 메뉴 Copy/Paste | Task 4, 5 |
| Copy → OS 클립보드(빈 문자열 포함) | Task 2 `write_clipboard_from_app`, Task 5 |
| Paste → 현재 스티커 본문만, 신규 스티커 없음 | Task 3, 5 |
| 빈/실패 Paste 무시 | Task 2 `read_os_clipboard_text`, Task 5 |
| 단축키 없음 | 구현 안 함(명세 부합) |

**2. Placeholder scan:** 없음.

**3. Type consistency:** `MenuAction.action` 값 `"copy"` / `"paste"` — `context_menu.action_map`·`board` 분기·문서가 동일 문자열을 사용한다.

---

## Execution handoff

**Plan complete and saved to `docs/features/sticker-copy-paste/2026-04-07-implementation-plan.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — 태스크마다 새 서브에이전트 배치, 태스크 사이 리뷰, 빠른 반복

**2. Inline Execution** — 이 세션에서 `executing-plans` 스타일로 일괄 구현·체크포인트

**Which approach?**
