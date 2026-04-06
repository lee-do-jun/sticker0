# sticker0 Implementation Plan

> **Documentation note:** 키보드 `q` 종료·`d`/Delete 삭제는 제거되었습니다. 종료는 보드 메뉴 **Quit**, 삭제는 스티커 메뉴 **Delete**를 사용합니다. 본 문서의 `keybindings.quit`/`delete`, `action_quit`, 관련 키 시나리오는 과거 초안일 수 있습니다.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 터미널에서 동작하는 데스크톱 스티커 메모 앱 `sticker0`를 Python + Textual TUI로 구현한다.

**Architecture:** Textual App 기반 단일 TUI 프로세스. `StickerBoard` 전체화면 위젯 위에 `StickerWidget`들이 `position: absolute`로 자유롭게 배치된다. 스티커 데이터는 `~/.local/share/sticker0/{uuid}.json`에 각각 저장된다.

**Tech Stack:** Python ≥ 3.11, Textual ≥ 0.80, tomllib (표준), pytest + pytest-asyncio

---

## File Map

| 파일 | 역할 |
|------|------|
| `pyproject.toml` | 패키지 설정, uv 의존성, `stk` CLI 진입점 |
| `src/sticker0/sticker.py` | `Sticker` dataclass, `StickerColor`, `BorderType` enum |
| `src/sticker0/storage.py` | `StickerStorage`: JSON 파일 로드/저장/삭제 |
| `src/sticker0/config.py` | `AppConfig`: `~/.stkrc` TOML 파싱, 기본값 제공 |
| `src/sticker0/widgets/sticker_widget.py` | `StickerWidget`: floating 스티커 TUI 위젯 (드래그, 리사이즈, 편집) |
| `src/sticker0/widgets/context_menu.py` | `ContextMenu`: 우클릭 팝업 메뉴 |
| `src/sticker0/widgets/board.py` | `StickerBoard`: 스티커 캔버스, 스티커 CRUD 조율 |
| `src/sticker0/app.py` | `Sticker0App`: Textual App 클래스, 키바인딩, 툴바 |
| `src/sticker0/main.py` | CLI 진입점 `main()` |
| `tests/test_sticker.py` | Sticker 모델 단위 테스트 |
| `tests/test_storage.py` | StickerStorage 단위 테스트 (tmp_path 사용) |
| `tests/test_config.py` | AppConfig 단위 테스트 |
| `tests/test_app.py` | Textual Pilot 통합 테스트 |

---

## Task 1: Project Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `src/sticker0/__init__.py`
- Create: `src/sticker0/main.py`
- Create: `src/sticker0/widgets/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: pyproject.toml 작성**

```toml
[project]
name = "sticker0"
version = "0.1.0"
description = "Terminal sticky notes"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "textual>=0.80",
]

[project.scripts]
stk = "sticker0.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/sticker0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
]
```

- [ ] **Step 2: 디렉터리 및 빈 파일 생성**

```bash
mkdir -p src/sticker0/widgets tests
touch src/sticker0/__init__.py
touch src/sticker0/widgets/__init__.py
touch tests/__init__.py
```

- [ ] **Step 3: 임시 main.py 작성**

```python
# src/sticker0/main.py
def main() -> None:
    print("sticker0 v0.1.0")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: uv로 개발환경 초기화 및 설치 확인**

```bash
uv sync --dev
uv run stk
```

Expected output: `sticker0 v0.1.0`

- [ ] **Step 5: Commit**

```bash
git init
git add pyproject.toml src/ tests/
git commit -m "chore: project scaffold"
```

---

## Task 2: Sticker 데이터 모델

**Files:**
- Create: `src/sticker0/sticker.py`
- Create: `tests/test_sticker.py`

- [ ] **Step 1: 실패 테스트 작성**

```python
# tests/test_sticker.py
from sticker0.sticker import Sticker, StickerColor, BorderType, StickerPosition, StickerSize

def test_sticker_defaults():
    s = Sticker()
    assert s.title == ""
    assert s.content == ""
    assert s.color == StickerColor.YELLOW
    assert s.border == BorderType.ROUNDED
    assert s.position.x == 0
    assert s.position.y == 0
    assert s.size.width == 30
    assert s.size.height == 10
    assert s.id != ""

def test_sticker_roundtrip():
    s = Sticker(title="Test", content="Hello", color=StickerColor.BLUE)
    d = s.to_dict()
    s2 = Sticker.from_dict(d)
    assert s2.id == s.id
    assert s2.title == "Test"
    assert s2.content == "Hello"
    assert s2.color == StickerColor.BLUE

def test_sticker_touch_updates_timestamp():
    import time
    s = Sticker()
    before = s.updated_at
    time.sleep(0.01)
    s.touch()
    assert s.updated_at > before
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_sticker.py -v
```

Expected: `ImportError` or `ModuleNotFoundError`

- [ ] **Step 3: sticker.py 구현**

```python
# src/sticker0/sticker.py
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class StickerColor(str, Enum):
    YELLOW = "yellow"
    BLUE = "blue"
    GREEN = "green"
    PINK = "pink"
    WHITE = "white"
    DARK = "dark"


class BorderType(str, Enum):
    ROUNDED = "rounded"
    SHARP = "sharp"
    DOUBLE = "double"
    THICK = "thick"
    ASCII = "ascii"


@dataclass
class StickerPosition:
    x: int = 0
    y: int = 0


@dataclass
class StickerSize:
    width: int = 30
    height: int = 10


@dataclass
class Sticker:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    color: StickerColor = StickerColor.YELLOW
    border: BorderType = BorderType.ROUNDED
    position: StickerPosition = field(default_factory=StickerPosition)
    size: StickerSize = field(default_factory=StickerSize)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "color": self.color.value,
            "border": self.border.value,
            "position": {"x": self.position.x, "y": self.position.y},
            "size": {"width": self.size.width, "height": self.size.height},
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Sticker:
        return cls(
            id=data["id"],
            title=data.get("title", ""),
            content=data.get("content", ""),
            color=StickerColor(data.get("color", "yellow")),
            border=BorderType(data.get("border", "rounded")),
            position=StickerPosition(**data.get("position", {})),
            size=StickerSize(**data.get("size", {})),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
uv run pytest tests/test_sticker.py -v
```

Expected: 3 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add src/sticker0/sticker.py tests/test_sticker.py
git commit -m "feat: add Sticker data model with serialization"
```

---

## Task 3: Storage Layer

**Files:**
- Create: `src/sticker0/storage.py`
- Create: `tests/test_storage.py`

- [ ] **Step 1: 실패 테스트 작성**

```python
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
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_storage.py -v
```

Expected: `ImportError`

- [ ] **Step 3: storage.py 구현**

```python
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
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
uv run pytest tests/test_storage.py -v
```

Expected: 5 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add src/sticker0/storage.py tests/test_storage.py
git commit -m "feat: add StickerStorage for JSON persistence"
```

---

## Task 4: Config Parser

**Files:**
- Create: `src/sticker0/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: 실패 테스트 작성**

```python
# tests/test_config.py
import pytest
from pathlib import Path
from sticker0.config import AppConfig
from sticker0.sticker import StickerColor, BorderType

def test_defaults_when_no_file(tmp_path):
    config = AppConfig.load(path=tmp_path / ".stkrc")
    assert config.theme.default_color == StickerColor.YELLOW
    assert config.border.type == BorderType.ROUNDED
    assert config.defaults.width == 30
    assert config.defaults.height == 10
    assert config.keybindings.new == "n"
    assert config.keybindings.delete == "d"
    assert config.keybindings.quit == "q"

def test_load_from_toml(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[theme]
default_color = "blue"

[border]
type = "double"

[defaults]
width = 40
height = 15

[keybindings]
new = "a"
delete = "x"
quit = "ctrl+q"
""", encoding="utf-8")
    config = AppConfig.load(path=rc)
    assert config.theme.default_color == StickerColor.BLUE
    assert config.border.type == BorderType.DOUBLE
    assert config.defaults.width == 40
    assert config.defaults.height == 15
    assert config.keybindings.new == "a"
    assert config.keybindings.delete == "x"
    assert config.keybindings.quit == "ctrl+q"

def test_partial_config_uses_defaults(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text('[theme]\ndefault_color = "green"\n', encoding="utf-8")
    config = AppConfig.load(path=rc)
    assert config.theme.default_color == StickerColor.GREEN
    assert config.border.type == BorderType.ROUNDED  # default
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_config.py -v
```

Expected: `ImportError`

- [ ] **Step 3: config.py 구현**

```python
# src/sticker0/config.py
from __future__ import annotations
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from sticker0.sticker import StickerColor, BorderType

CONFIG_PATH = Path.home() / ".stkrc"


@dataclass
class ThemeConfig:
    default_color: StickerColor = StickerColor.YELLOW


@dataclass
class BorderConfig:
    type: BorderType = BorderType.ROUNDED


@dataclass
class DefaultsConfig:
    width: int = 30
    height: int = 10


@dataclass
class KeybindingsConfig:
    new: str = "n"
    delete: str = "d"
    quit: str = "q"


@dataclass
class AppConfig:
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    border: BorderConfig = field(default_factory=BorderConfig)
    defaults: DefaultsConfig = field(default_factory=DefaultsConfig)
    keybindings: KeybindingsConfig = field(default_factory=KeybindingsConfig)

    @classmethod
    def load(cls, path: Path = CONFIG_PATH) -> AppConfig:
        if not path.exists():
            return cls()
        with open(path, "rb") as f:
            data = tomllib.load(f)
        config = cls()
        if t := data.get("theme"):
            if v := t.get("default_color"):
                config.theme.default_color = StickerColor(v)
        if b := data.get("border"):
            if v := b.get("type"):
                config.border.type = BorderType(v)
        if d := data.get("defaults"):
            config.defaults.width = d.get("width", 30)
            config.defaults.height = d.get("height", 10)
        if kb := data.get("keybindings"):
            config.keybindings.new = kb.get("new", "n")
            config.keybindings.delete = kb.get("delete", "d")
            config.keybindings.quit = kb.get("quit", "q")
        return config
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
uv run pytest tests/test_config.py -v
```

Expected: 3 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add src/sticker0/config.py tests/test_config.py
git commit -m "feat: add AppConfig with ~/.stkrc TOML parsing"
```

---

## Task 5: StickerWidget — 기본 렌더링

**Files:**
- Create: `src/sticker0/widgets/sticker_widget.py`
- Create: `tests/test_app.py` (Pilot 테스트 시작)

색상 맵:

| StickerColor | 텍스트 색 | 배경 색 |
|-------------|-----------|---------|
| YELLOW | #000000 | #ffeb3b |
| BLUE | #ffffff | #1565c0 |
| GREEN | #000000 | #4caf50 |
| PINK | #000000 | #f48fb1 |
| WHITE | #000000 | #ffffff |
| DARK | #ffffff | #212121 |

BorderType → Textual border 스타일 맵:
- ROUNDED → `"round"`
- SHARP → `"solid"`
- DOUBLE → `"double"`
- THICK → `"heavy"`
- ASCII → `"ascii"`

- [ ] **Step 1: 기본 렌더링 테스트 작성**

```python
# tests/test_app.py
import pytest
from textual.pilot import Pilot
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
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_app.py -v
```

Expected: `ImportError` (app.py, sticker_widget.py 미존재)

- [ ] **Step 3: StickerWidget 구현**

```python
# src/sticker0/widgets/sticker_widget.py
from __future__ import annotations
import time
from textual.widget import Widget
from textual.widgets import Static, TextArea
from textual.app import ComposeResult
from textual.events import MouseDown, MouseMove, MouseUp, Click
from sticker0.sticker import Sticker, StickerColor, BorderType

COLOR_MAP: dict[StickerColor, tuple[str, str]] = {
    StickerColor.YELLOW: ("#000000", "#ffeb3b"),
    StickerColor.BLUE:   ("#ffffff", "#1565c0"),
    StickerColor.GREEN:  ("#000000", "#4caf50"),
    StickerColor.PINK:   ("#000000", "#f48fb1"),
    StickerColor.WHITE:  ("#000000", "#ffffff"),
    StickerColor.DARK:   ("#ffffff", "#212121"),
}

BORDER_MAP: dict[BorderType, str] = {
    BorderType.ROUNDED: "round",
    BorderType.SHARP:   "solid",
    BorderType.DOUBLE:  "double",
    BorderType.THICK:   "heavy",
    BorderType.ASCII:   "ascii",
}

class StickerWidget(Widget):
    DEFAULT_CSS = """
    StickerWidget {
        position: absolute;
        padding: 0 1;
        min-width: 20;
        min-height: 5;
    }
    StickerWidget .sticker-title {
        text-style: bold;
        height: 1;
    }
    StickerWidget .sticker-content {
        height: 1fr;
    }
    """

    def __init__(self, sticker: Sticker, **kwargs) -> None:
        super().__init__(**kwargs)
        self.sticker = sticker
        self._drag_start: tuple[int, int] | None = None
        self._drag_origin: tuple[int, int] = (0, 0)
        self._last_click: float = 0.0
        self._editing = False
        self._apply_sticker_styles()

    def _apply_sticker_styles(self) -> None:
        text_color, bg_color = COLOR_MAP.get(
            self.sticker.color, COLOR_MAP[StickerColor.YELLOW]
        )
        border_style = BORDER_MAP.get(self.sticker.border, "round")
        self.styles.background = bg_color
        self.styles.color = text_color
        self.styles.border = (border_style, text_color)
        self.styles.offset = (self.sticker.position.x, self.sticker.position.y)
        self.styles.width = self.sticker.size.width
        self.styles.height = self.sticker.size.height

    def compose(self) -> ComposeResult:
        title = self.sticker.title or "📌 메모"
        yield Static(title, classes="sticker-title")
        yield Static(self.sticker.content, classes="sticker-content")

    def refresh_display(self) -> None:
        """스티커 데이터 변경 후 화면 갱신."""
        self._apply_sticker_styles()
        self.query_one(".sticker-title", Static).update(
            self.sticker.title or "📌 메모"
        )
        self.query_one(".sticker-content", Static).update(self.sticker.content)
```

- [ ] **Step 4: 임시 app.py 작성 (테스트 통과용)**

```python
# src/sticker0/app.py
from __future__ import annotations
from textual.app import App, ComposeResult
from sticker0.config import AppConfig
from sticker0.storage import StickerStorage
from sticker0.widgets.board import StickerBoard


class Sticker0App(App):
    def __init__(self, storage: StickerStorage | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = AppConfig.load()
        self.storage = storage or StickerStorage()

    def compose(self) -> ComposeResult:
        yield StickerBoard(storage=self.storage, config=self.config)
```

- [ ] **Step 5: 임시 board.py 작성**

```python
# src/sticker0/widgets/board.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from sticker0.config import AppConfig
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
```

- [ ] **Step 6: 테스트 통과 확인**

```bash
uv run pytest tests/test_app.py -v
```

Expected: 2 tests PASSED

- [ ] **Step 7: Commit**

```bash
git add src/sticker0/widgets/sticker_widget.py src/sticker0/widgets/board.py \
        src/sticker0/app.py tests/test_app.py
git commit -m "feat: add StickerWidget with basic rendering and StickerBoard"
```

---

## Task 6: StickerWidget — 드래그 이동

**Files:**
- Modify: `src/sticker0/widgets/sticker_widget.py`
- Modify: `tests/test_app.py`

- [ ] **Step 1: 드래그 테스트 추가**

```python
# tests/test_app.py 에 추가
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
        # 타이틀바에서 드래그 시작 (screen 좌표)
        await pilot.mouse_down(widget, offset=(5, 0))
        await pilot.mouse_move(widget, offset=(15, 5))  # +10 x, +5 y
        await pilot.mouse_up(widget)
        assert widget.sticker.position.x == 15
        assert widget.sticker.position.y == 10
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_app.py::test_sticker_drag_moves_position -v
```

Expected: FAIL (드래그 미구현)

- [ ] **Step 3: 드래그 이벤트 핸들러 구현**

`src/sticker0/widgets/sticker_widget.py` 의 `StickerWidget` 클래스에 추가:

```python
    def on_mouse_down(self, event: MouseDown) -> None:
        event.stop()
        self._drag_start = (event.screen_x, event.screen_y)
        self._drag_origin = (self.sticker.position.x, self.sticker.position.y)
        self.capture_mouse()

    def on_mouse_move(self, event: MouseMove) -> None:
        if self._drag_start is None:
            return
        event.stop()
        dx = event.screen_x - self._drag_start[0]
        dy = event.screen_y - self._drag_start[1]
        new_x = max(0, self._drag_origin[0] + dx)
        new_y = max(0, self._drag_origin[1] + dy)
        self.sticker.position.x = new_x
        self.sticker.position.y = new_y
        self.styles.offset = (new_x, new_y)

    def on_mouse_up(self, event: MouseUp) -> None:
        if self._drag_start is not None:
            self._drag_start = None
            self.release_mouse()
            # 위치 영속화
            board = self.app.query_one("StickerBoard")
            board.save_sticker(self.sticker)
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
uv run pytest tests/test_app.py -v
```

Expected: All tests PASSED

- [ ] **Step 5: Commit**

```bash
git add src/sticker0/widgets/sticker_widget.py tests/test_app.py
git commit -m "feat: implement drag-to-move on StickerWidget"
```

---

## Task 7: StickerWidget — 리사이즈

**Files:**
- Modify: `src/sticker0/widgets/sticker_widget.py`
- Modify: `tests/test_app.py`

리사이즈는 우하단 모서리(last row, last col)에서 드래그할 때 동작한다.

- [ ] **Step 1: 리사이즈 테스트 추가**

```python
# tests/test_app.py 에 추가
@pytest.mark.asyncio
async def test_sticker_resize_from_corner(tmp_storage):
    s = Sticker(title="Resize me")
    s.size.width = 30
    s.size.height = 10
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        from sticker0.widgets.sticker_widget import StickerWidget
        widget = app.query_one(StickerWidget)
        # 우하단 모서리에서 드래그
        corner_x = s.size.width - 1
        corner_y = s.size.height - 1
        await pilot.mouse_down(widget, offset=(corner_x, corner_y))
        await pilot.mouse_move(widget, offset=(corner_x + 5, corner_y + 3))
        await pilot.mouse_up(widget)
        assert widget.sticker.size.width == 35
        assert widget.sticker.size.height == 13
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_app.py::test_sticker_resize_from_corner -v
```

Expected: FAIL

- [ ] **Step 3: 리사이즈 로직 추가**

`on_mouse_down`을 아래로 교체 (드래그 vs 리사이즈 구분):

```python
    MIN_WIDTH = 20
    MIN_HEIGHT = 5

    def _is_resize_handle(self, event: MouseDown) -> bool:
        """우하단 모서리(2x2 영역) 클릭 여부."""
        w = self.sticker.size.width
        h = self.sticker.size.height
        return event.x >= w - 2 and event.y >= h - 2

    def on_mouse_down(self, event: MouseDown) -> None:
        event.stop()
        self._drag_start = (event.screen_x, event.screen_y)
        if self._is_resize_handle(event):
            self._resizing = True
            self._drag_origin = (self.sticker.size.width, self.sticker.size.height)
        else:
            self._resizing = False
            self._drag_origin = (self.sticker.position.x, self.sticker.position.y)
        self.capture_mouse()

    def on_mouse_move(self, event: MouseMove) -> None:
        if self._drag_start is None:
            return
        event.stop()
        dx = event.screen_x - self._drag_start[0]
        dy = event.screen_y - self._drag_start[1]
        if self._resizing:
            new_w = max(self.MIN_WIDTH, self._drag_origin[0] + dx)
            new_h = max(self.MIN_HEIGHT, self._drag_origin[1] + dy)
            self.sticker.size.width = new_w
            self.sticker.size.height = new_h
            self.styles.width = new_w
            self.styles.height = new_h
        else:
            new_x = max(0, self._drag_origin[0] + dx)
            new_y = max(0, self._drag_origin[1] + dy)
            self.sticker.position.x = new_x
            self.sticker.position.y = new_y
            self.styles.offset = (new_x, new_y)
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
uv run pytest tests/test_app.py -v
```

Expected: All tests PASSED

- [ ] **Step 5: Commit**

```bash
git add src/sticker0/widgets/sticker_widget.py tests/test_app.py
git commit -m "feat: add resize handle on StickerWidget bottom-right corner"
```

---

## Task 8: StickerWidget — 더블클릭 편집 모드

**Files:**
- Modify: `src/sticker0/widgets/sticker_widget.py`
- Modify: `tests/test_app.py`

더블클릭 → content Static을 TextArea로 교체 → Esc/blur로 저장 후 복원.

- [ ] **Step 1: 편집 모드 테스트 추가**

```python
# tests/test_app.py 에 추가
@pytest.mark.asyncio
async def test_double_click_enters_edit_mode(tmp_storage):
    s = Sticker(title="Edit me", content="original")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        from sticker0.widgets.sticker_widget import StickerWidget
        from textual.widgets import TextArea
        widget = app.query_one(StickerWidget)
        await pilot.click(widget, offset=(5, 2))
        await pilot.click(widget, offset=(5, 2))  # double click
        await pilot.pause()
        assert len(app.query(TextArea)) == 1

@pytest.mark.asyncio
async def test_escape_exits_edit_mode(tmp_storage):
    s = Sticker(title="Edit me", content="original")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        from sticker0.widgets.sticker_widget import StickerWidget
        from textual.widgets import TextArea, Static
        widget = app.query_one(StickerWidget)
        await pilot.click(widget, offset=(5, 2))
        await pilot.click(widget, offset=(5, 2))
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        assert len(app.query(TextArea)) == 0
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_app.py::test_double_click_enters_edit_mode -v
```

Expected: FAIL

- [ ] **Step 3: 편집 모드 구현**

`StickerWidget`에 추가 (import에 `TextArea` 추가):

```python
from textual.widgets import Static, TextArea

    DOUBLE_CLICK_INTERVAL = 0.4  # seconds

    def on_click(self, event: Click) -> None:
        now = time.monotonic()
        if now - self._last_click < self.DOUBLE_CLICK_INTERVAL:
            self._enter_edit_mode()
            event.stop()
        self._last_click = now

    def _enter_edit_mode(self) -> None:
        if self._editing:
            return
        self._editing = True
        content_widget = self.query_one(".sticker-content", Static)
        content_widget.remove()
        editor = TextArea(
            self.sticker.content,
            classes="sticker-content",
            id="sticker-editor",
        )
        self.mount(editor)
        editor.focus()

    def _exit_edit_mode(self) -> None:
        if not self._editing:
            return
        self._editing = False
        try:
            editor = self.query_one("#sticker-editor", TextArea)
            self.sticker.content = editor.text
            editor.remove()
        except Exception:
            pass
        self.mount(Static(self.sticker.content, classes="sticker-content"))
        board = self.app.query_one("StickerBoard")
        board.save_sticker(self.sticker)

    def on_key(self, event) -> None:
        if self._editing and event.key == "escape":
            self._exit_edit_mode()
            event.stop()
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
uv run pytest tests/test_app.py -v
```

Expected: All tests PASSED

- [ ] **Step 5: Commit**

```bash
git add src/sticker0/widgets/sticker_widget.py tests/test_app.py
git commit -m "feat: double-click edit mode with Escape to save"
```

---

## Task 9: 우클릭 Context Menu

**Files:**
- Create: `src/sticker0/widgets/context_menu.py`
- Modify: `src/sticker0/widgets/sticker_widget.py`
- Modify: `tests/test_app.py`

- [ ] **Step 1: Context Menu 테스트 추가**

```python
# tests/test_app.py 에 추가
@pytest.mark.asyncio
async def test_right_click_shows_context_menu(tmp_storage):
    s = Sticker(title="Menu test")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        from sticker0.widgets.sticker_widget import StickerWidget
        from sticker0.widgets.context_menu import ContextMenu
        widget = app.query_one(StickerWidget)
        await pilot.mouse_right_click(widget, offset=(5, 2))
        await pilot.pause()
        assert len(app.query(ContextMenu)) == 1

@pytest.mark.asyncio
async def test_context_menu_delete_removes_sticker(tmp_storage):
    s = Sticker(title="Delete via menu")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        from sticker0.widgets.sticker_widget import StickerWidget
        from sticker0.widgets.context_menu import ContextMenu
        widget = app.query_one(StickerWidget)
        await pilot.mouse_right_click(widget, offset=(5, 2))
        await pilot.pause()
        menu = app.query_one(ContextMenu)
        await pilot.click(menu.query_one("#menu-delete"))
        await pilot.pause()
        assert len(app.query(StickerWidget)) == 0
        assert tmp_storage.load_all() == []
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_app.py::test_right_click_shows_context_menu -v
```

Expected: FAIL

- [ ] **Step 3: ContextMenu 위젯 구현**

```python
# src/sticker0/widgets/context_menu.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Button
from textual.message import Message


class ContextMenu(Widget):
    """우클릭 팝업 메뉴."""

    DEFAULT_CSS = """
    ContextMenu {
        position: absolute;
        width: 20;
        height: auto;
        border: round $accent;
        background: $surface;
        layer: menu;
        z-index: 100;
    }
    ContextMenu Button {
        width: 1fr;
        height: 1;
        border: none;
        background: transparent;
    }
    ContextMenu Button:hover {
        background: $accent 20%;
    }
    """

    class MenuAction(Message):
        def __init__(self, action: str, sticker_id: str) -> None:
            super().__init__()
            self.action = action
            self.sticker_id = sticker_id

    def __init__(self, sticker_id: str, x: int, y: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.sticker_id = sticker_id
        self.styles.offset = (x, y)

    def compose(self) -> ComposeResult:
        yield Button("✏️  편집", id="menu-edit", variant="default")
        yield Button("🗑️  삭제", id="menu-delete", variant="error")
        yield Button("🎨  색상 변경", id="menu-color", variant="default")
        yield Button("✖  닫기", id="menu-close", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "menu-close":
            self.remove()
            return
        action_map = {
            "menu-edit": "edit",
            "menu-delete": "delete",
            "menu-color": "color",
        }
        action = action_map.get(event.button.id or "", "")
        if action:
            self.post_message(self.MenuAction(action, self.sticker_id))
            self.remove()
```

- [ ] **Step 4: StickerWidget에 우클릭 핸들러 추가**

`src/sticker0/widgets/sticker_widget.py`에 추가:

```python
from textual.events import MouseEvent

    def on_mouse_right_click(self, event: MouseEvent) -> None:
        event.stop()
        from sticker0.widgets.context_menu import ContextMenu
        # 기존 메뉴 닫기
        for menu in self.app.query(ContextMenu):
            menu.remove()
        menu = ContextMenu(
            sticker_id=self.sticker.id,
            x=event.screen_x,
            y=event.screen_y,
        )
        self.app.query_one("StickerBoard").mount(menu)
```

- [ ] **Step 5: StickerBoard에서 ContextMenu.MenuAction 처리**

`src/sticker0/widgets/board.py`에 추가:

```python
from sticker0.widgets.context_menu import ContextMenu

    def on_context_menu_menu_action(self, message: ContextMenu.MenuAction) -> None:
        if message.action == "delete":
            self.storage.delete(message.sticker_id)
            for widget in self.query("StickerWidget"):
                from sticker0.widgets.sticker_widget import StickerWidget
                if isinstance(widget, StickerWidget) and widget.sticker.id == message.sticker_id:
                    widget.remove()
        elif message.action == "edit":
            for widget in self.query("StickerWidget"):
                from sticker0.widgets.sticker_widget import StickerWidget
                if isinstance(widget, StickerWidget) and widget.sticker.id == message.sticker_id:
                    widget._enter_edit_mode()
```

- [ ] **Step 6: 테스트 통과 확인**

```bash
uv run pytest tests/test_app.py -v
```

Expected: All tests PASSED

- [ ] **Step 7: Commit**

```bash
git add src/sticker0/widgets/context_menu.py \
        src/sticker0/widgets/sticker_widget.py \
        src/sticker0/widgets/board.py \
        tests/test_app.py
git commit -m "feat: right-click context menu with edit/delete actions"
```

---

## Task 10: 새 스티커 생성 + 키보드 단축키

**Files:**
- Modify: `src/sticker0/widgets/board.py`
- Modify: `src/sticker0/app.py`
- Modify: `tests/test_app.py`

- [ ] **Step 1: 새 스티커 생성 테스트 추가**

```python
# tests/test_app.py 에 추가
@pytest.mark.asyncio
async def test_press_n_creates_sticker(tmp_storage):
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        from sticker0.widgets.sticker_widget import StickerWidget
        await pilot.press("n")
        await pilot.pause()
        assert len(app.query(StickerWidget)) == 1
        assert len(tmp_storage.load_all()) == 1

@pytest.mark.asyncio
async def test_press_q_quits_app(tmp_storage):
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("q")
    assert not app.is_running
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_app.py::test_press_n_creates_sticker -v
```

Expected: FAIL

- [ ] **Step 3: StickerBoard에 스티커 생성 메서드 추가**

`src/sticker0/widgets/board.py` 수정:

```python
from sticker0.sticker import Sticker, StickerPosition, StickerSize

    def add_new_sticker(self) -> None:
        """기본값으로 새 스티커를 생성하고 화면 중앙에 배치."""
        size = self.size  # Textual Size(width, height)
        w = self.config.defaults.width
        h = self.config.defaults.height
        sticker = Sticker(
            color=self.config.theme.default_color,
            border=self.config.border.type,
            position=StickerPosition(
                x=max(0, (size.width - w) // 2),
                y=max(0, (size.height - h) // 2),
            ),
            size=StickerSize(width=w, height=h),
        )
        self.storage.save(sticker)
        from sticker0.widgets.sticker_widget import StickerWidget
        self.mount(StickerWidget(sticker))
```

- [ ] **Step 4: Sticker0App에 키바인딩 추가**

`src/sticker0/app.py` 수정:

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
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
        yield Header(show_clock=True)
        yield StickerBoard(storage=self.storage, config=self.config)
        yield Footer()

    def on_mount(self) -> None:
        kb = self.config.keybindings
        self.bind(kb.new, "new_sticker", description="새 스티커")
        self.bind(kb.quit, "quit", description="종료")

    def action_new_sticker(self) -> None:
        self.query_one(StickerBoard).add_new_sticker()

    def action_quit(self) -> None:
        self.exit()
```

- [ ] **Step 4b: StickerWidget에 포커스 + d/Enter 키 지원 추가**

`src/sticker0/widgets/sticker_widget.py` 클래스 최상단(DEFAULT_CSS 위)에 추가:

```python
    can_focus = True
```

`on_key` 메서드를 아래로 교체:

```python
    def on_key(self, event) -> None:
        if self._editing:
            if event.key == "escape":
                self._exit_edit_mode()
                event.stop()
        else:
            if event.key in ("d", "delete"):
                board = self.app.query_one("StickerBoard")
                board.delete_sticker(self.sticker.id)
                event.stop()
            elif event.key == "enter":
                self._enter_edit_mode()
                event.stop()
```

`src/sticker0/widgets/board.py` 에 `delete_sticker` 메서드 추가:

```python
    def delete_sticker(self, sticker_id: str) -> None:
        self.storage.delete(sticker_id)
        from sticker0.widgets.sticker_widget import StickerWidget
        for widget in self.query(StickerWidget):
            if widget.sticker.id == sticker_id:
                widget.remove()
                break
```

- [ ] **Step 4c: d/Enter 키 테스트 추가**

```python
# tests/test_app.py 에 추가
@pytest.mark.asyncio
async def test_focused_sticker_delete_with_d_key(tmp_storage):
    s = Sticker(title="Press d")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        from sticker0.widgets.sticker_widget import StickerWidget
        widget = app.query_one(StickerWidget)
        widget.focus()
        await pilot.pause()
        await pilot.press("d")
        await pilot.pause()
        assert len(app.query(StickerWidget)) == 0
        assert tmp_storage.load_all() == []

@pytest.mark.asyncio
async def test_focused_sticker_enter_opens_edit(tmp_storage):
    s = Sticker(title="Press enter", content="hello")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        from sticker0.widgets.sticker_widget import StickerWidget
        from textual.widgets import TextArea
        widget = app.query_one(StickerWidget)
        widget.focus()
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        assert len(app.query(TextArea)) == 1
```

- [ ] **Step 5: 테스트 통과 확인**

```bash
uv run pytest tests/test_app.py -v
```

Expected: All tests PASSED

- [ ] **Step 6: Commit**

```bash
git add src/sticker0/widgets/board.py src/sticker0/app.py tests/test_app.py
git commit -m "feat: new sticker creation with keyboard binding"
```

---

## Task 11: main.py 완성 + 패키징

**Files:**
- Modify: `src/sticker0/main.py`
- Modify: `src/sticker0/__init__.py`

- [ ] **Step 1: main.py 완성**

```python
# src/sticker0/main.py
from __future__ import annotations


def main() -> None:
    from sticker0.app import Sticker0App
    app = Sticker0App()
    app.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: __init__.py 버전 노출**

```python
# src/sticker0/__init__.py
__version__ = "0.1.0"
```

- [ ] **Step 3: stk 명령어 실행 확인**

```bash
uv run stk
```

Expected: TUI 앱이 실행되고 `n`키로 스티커 생성, `q`키로 종료 가능

- [ ] **Step 4: uv tool install 테스트**

```bash
uv build
uv tool install dist/sticker0-0.1.0-py3-none-any.whl
stk
```

Expected: `stk` 명령어로 앱 실행

- [ ] **Step 5: 전체 테스트 통과 확인**

```bash
uv run pytest -v
```

Expected: All tests PASSED

- [ ] **Step 6: Commit**

```bash
git add src/sticker0/main.py src/sticker0/__init__.py
git commit -m "feat: finalize CLI entrypoint and packaging"
```

---

## Task 12: 색상 변경 메뉴 구현

**Files:**
- Create: `src/sticker0/widgets/color_picker.py`
- Modify: `src/sticker0/widgets/board.py`
- Modify: `tests/test_app.py`

- [ ] **Step 1: 색상 변경 테스트 추가**

```python
# tests/test_app.py 에 추가
@pytest.mark.asyncio
async def test_color_change_via_context_menu(tmp_storage):
    from sticker0.sticker import StickerColor
    s = Sticker(title="Color test", color=StickerColor.YELLOW)
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        from sticker0.widgets.sticker_widget import StickerWidget
        from sticker0.widgets.color_picker import ColorPicker
        widget = app.query_one(StickerWidget)
        await pilot.mouse_right_click(widget, offset=(5, 2))
        await pilot.pause()
        menu = app.query_one("ContextMenu")
        await pilot.click(menu.query_one("#menu-color"))
        await pilot.pause()
        assert len(app.query(ColorPicker)) == 1
        picker = app.query_one(ColorPicker)
        await pilot.click(picker.query_one("#color-blue"))
        await pilot.pause()
        loaded = tmp_storage.load(s.id)
        assert loaded.color == StickerColor.BLUE
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_app.py::test_color_change_via_context_menu -v
```

Expected: FAIL

- [ ] **Step 3: ColorPicker 구현**

```python
# src/sticker0/widgets/color_picker.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Button
from textual.message import Message
from sticker0.sticker import StickerColor

COLOR_LABELS: dict[StickerColor, str] = {
    StickerColor.YELLOW: "🟡 노랑",
    StickerColor.BLUE:   "🔵 파랑",
    StickerColor.GREEN:  "🟢 초록",
    StickerColor.PINK:   "🩷 분홍",
    StickerColor.WHITE:  "⬜ 흰색",
    StickerColor.DARK:   "⬛ 어두움",
}


class ColorPicker(Widget):
    DEFAULT_CSS = """
    ColorPicker {
        position: absolute;
        width: 20;
        height: auto;
        border: round $accent;
        background: $surface;
        layer: menu;
        z-index: 100;
    }
    ColorPicker Button {
        width: 1fr;
        height: 1;
        border: none;
        background: transparent;
    }
    """

    class ColorSelected(Message):
        def __init__(self, sticker_id: str, color: StickerColor) -> None:
            super().__init__()
            self.sticker_id = sticker_id
            self.color = color

    def __init__(self, sticker_id: str, x: int, y: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.sticker_id = sticker_id
        self.styles.offset = (x, y)

    def compose(self) -> ComposeResult:
        for color, label in COLOR_LABELS.items():
            yield Button(label, id=f"color-{color.value}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        color_value = (event.button.id or "").replace("color-", "")
        try:
            color = StickerColor(color_value)
            self.post_message(self.ColorSelected(self.sticker_id, color))
        except ValueError:
            pass
        self.remove()
```

- [ ] **Step 4: board.py 완전한 메서드 교체**

`src/sticker0/widgets/board.py` 상단 import에 추가:

```python
from sticker0.widgets.color_picker import ColorPicker
```

`on_context_menu_menu_action`을 아래 완전한 버전으로 교체:

```python
    def on_context_menu_menu_action(self, message) -> None:
        from sticker0.widgets.sticker_widget import StickerWidget
        from sticker0.widgets.context_menu import ContextMenu
        if message.action == "delete":
            self.delete_sticker(message.sticker_id)
        elif message.action == "edit":
            for widget in self.query(StickerWidget):
                if widget.sticker.id == message.sticker_id:
                    widget._enter_edit_mode()
        elif message.action == "color":
            picker = ColorPicker(
                sticker_id=message.sticker_id,
                x=20,
                y=5,
            )
            self.mount(picker)

    def on_color_picker_color_selected(self, message: ColorPicker.ColorSelected) -> None:
        from sticker0.widgets.sticker_widget import StickerWidget
        for widget in self.query(StickerWidget):
            if widget.sticker.id == message.sticker_id:
                widget.sticker.color = message.color
                widget._apply_sticker_styles()
                widget.refresh()
                self.storage.save(widget.sticker)
```

- [ ] **Step 5: 테스트 통과 확인**

```bash
uv run pytest tests/test_app.py -v
```

Expected: All tests PASSED

- [ ] **Step 6: 전체 테스트 및 최종 Commit**

```bash
uv run pytest -v
git add src/sticker0/widgets/color_picker.py \
        src/sticker0/widgets/board.py \
        tests/test_app.py
git commit -m "feat: color picker via context menu"
```

---

## Verification

### 수동 동작 확인 체크리스트

```bash
# 1. 앱 실행
uv run stk

# 2. n 키로 스티커 3개 생성
# 3. 각 스티커를 드래그해서 이동
# 4. 스티커 우하단 모서리를 드래그해서 리사이즈
# 5. 스티커 더블클릭 → 텍스트 편집 → Esc로 저장
# 6. 우클릭 → 삭제
# 7. 우클릭 → 색상 변경
# 8. q 키로 종료 후 재실행 → 스티커가 복원되는지 확인

# 9. ~/.stkrc 테스트
cat > ~/.stkrc << 'EOF'
[theme]
default_color = "blue"

[border]
type = "double"
EOF
uv run stk  # 새 스티커가 파란색 + double 테두리로 생성되는지 확인

# 10. 전체 테스트
uv run pytest -v --tb=short
```

### tmux 통합 테스트

```bash
# tmux에서 실행
tmux new-window -n stickers 'uv run stk'
# 또는
tmux split-window -h 'uv run stk'
```
