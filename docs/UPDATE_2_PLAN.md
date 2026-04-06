# sticker0 Update 2 Implementation Plan

> **Documentation note:** 키보드 `q` 종료·`d`/Delete 삭제는 제거되었습니다. 종료/삭제는 우클릭 메뉴를 사용합니다. 아래 스니펫의 `keybindings.quit`/`delete`, `action_quit`, `on_key`의 `d`/`delete` 등은 과거 초안일 수 있습니다.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** v0.2.0의 색상 시스템을 3색 프리셋 기반으로 전면 교체하고, 보드 테마, 최소화, 중앙점 제약, 테두리 커스터마이징을 추가하여 v0.3.0으로 업그레이드한다.

**Architecture:** `StickerColor`/`BorderType` enum을 제거하고 `StickerColors` dataclass (border/text/area 3색)로 교체. 보드 테마는 `BoardTheme` (background/indicator)로 관리하며 .stkrc에 atomic write. `presets.py`에 내장 프리셋 정의, 커스텀 프리셋은 .stkrc에서 로드. 스티커 최소화는 `minimized` 플래그로 관리하며 높이 3줄 + Static 한 줄 표시.

**Tech Stack:** Python >= 3.11, Textual >= 0.80, pytest + pytest-asyncio, tomllib (stdlib)

---

## File Map

| 파일 | 변경 유형 | 책임 |
|------|-----------|------|
| `src/sticker0/sticker.py` | 대폭 수정 | `StickerColor`/`BorderType` enum 제거, `StickerColors` dataclass 추가, `minimized` 필드, JSON 마이그레이션 |
| `src/sticker0/presets.py` | 신규 | 내장 스티커/보드 프리셋 정의, 프리셋 조회 헬퍼 |
| `src/sticker0/config.py` | 대폭 수정 | `BoardTheme`, `BorderConfig` top/sides, atomic write, 커스텀 프리셋 로드 |
| `src/sticker0/widgets/sticker_widget.py` | 대폭 수정 | 3색 스타일링, 최소화/복원, 더블클릭 감지, 중앙점 제약, 스크롤바 여백 |
| `src/sticker0/widgets/context_menu.py` | 수정 | 텍스트 색상 동적 적용, 최소화/복원 항목 추가 |
| `src/sticker0/widgets/preset_picker.py` | 신규 (color_picker.py 대체) | 스티커 프리셋 선택 팝업 |
| `src/sticker0/widgets/theme_picker.py` | 신규 | 보드 테마 선택 팝업 |
| `src/sticker0/widgets/board_menu.py` | 수정 | 텍스트 색상 동적 적용, 테마 변경 액션 연결 |
| `src/sticker0/widgets/board.py` | 수정 | 보드 테마 배경 적용, on_resize 클램프, 메뉴 상호 배제, 프리셋/테마 피커 연결 |
| `src/sticker0/widgets/color_picker.py` | 삭제 | preset_picker.py로 대체 |
| `tests/test_sticker.py` | 수정 | 새 데이터 모델 테스트 |
| `tests/test_presets.py` | 신규 | 프리셋 조회 테스트 |
| `tests/test_config.py` | 수정 | 새 설정 형식 + atomic write 테스트 |
| `tests/test_app.py` | 수정 | 새 동작 테스트 (프리셋, 최소화, 테마 등) |

---

## Task 1: 데이터 모델 교체 + 프리셋 정의

**Files:**
- Create: `src/sticker0/presets.py`
- Modify: `src/sticker0/sticker.py`
- Modify: `tests/test_sticker.py`
- Create: `tests/test_presets.py`

- [ ] **Step 1: 프리셋 테스트 작성**

`tests/test_presets.py`:

```python
# tests/test_presets.py
from sticker0.presets import (
    StickerPreset,
    BoardThemePreset,
    STICKER_PRESETS,
    BOARD_PRESETS,
    DEFAULT_STICKER_PRESET,
    DEFAULT_BOARD_PRESET,
    get_sticker_preset,
    get_board_preset,
)


def test_builtin_sticker_presets_exist():
    assert "Snow" in STICKER_PRESETS
    assert "Ink" in STICKER_PRESETS
    assert "Sky" in STICKER_PRESETS
    assert "Banana" in STICKER_PRESETS


def test_snow_preset_values():
    snow = STICKER_PRESETS["Snow"]
    assert snow.border == "white"
    assert snow.text == "white"
    assert snow.area == "transparent"


def test_ink_preset_values():
    ink = STICKER_PRESETS["Ink"]
    assert ink.border == "black"
    assert ink.text == "black"
    assert ink.area == "transparent"


def test_sky_preset_values():
    sky = STICKER_PRESETS["Sky"]
    assert sky.border == "white"
    assert sky.text == "white"
    assert sky.area == "#1565c0"


def test_banana_preset_values():
    banana = STICKER_PRESETS["Banana"]
    assert banana.border == "black"
    assert banana.text == "black"
    assert banana.area == "#ffeb3b"


def test_builtin_board_presets_exist():
    assert "Dark Base" in BOARD_PRESETS
    assert "Light Base" in BOARD_PRESETS
    assert "Dark Mode" in BOARD_PRESETS
    assert "White Mode" in BOARD_PRESETS


def test_dark_mode_preset_values():
    dm = BOARD_PRESETS["Dark Mode"]
    assert dm.background == "transparent"
    assert dm.indicator == "white"


def test_default_sticker_preset():
    assert DEFAULT_STICKER_PRESET == "Snow"


def test_default_board_preset():
    assert DEFAULT_BOARD_PRESET == "Dark Mode"


def test_get_sticker_preset_found():
    preset = get_sticker_preset("Snow")
    assert preset is not None
    assert preset.name == "Snow"


def test_get_sticker_preset_not_found():
    assert get_sticker_preset("Nonexistent") is None


def test_get_board_preset_found():
    preset = get_board_preset("Dark Base")
    assert preset is not None
    assert preset.name == "Dark Base"
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_presets.py -v
```

Expected: FAIL (모듈 미존재)

- [ ] **Step 3: presets.py 작성**

```python
# src/sticker0/presets.py
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class StickerPreset:
    name: str
    border: str
    text: str
    area: str


@dataclass(frozen=True)
class BoardThemePreset:
    name: str
    background: str
    indicator: str


STICKER_PRESETS: dict[str, StickerPreset] = {
    "Snow": StickerPreset("Snow", "white", "white", "transparent"),
    "Ink": StickerPreset("Ink", "black", "black", "transparent"),
    "Sky": StickerPreset("Sky", "white", "white", "#1565c0"),
    "Banana": StickerPreset("Banana", "black", "black", "#ffeb3b"),
}

BOARD_PRESETS: dict[str, BoardThemePreset] = {
    "Dark Base": BoardThemePreset("Dark Base", "black", "white"),
    "Light Base": BoardThemePreset("Light Base", "white", "black"),
    "Dark Mode": BoardThemePreset("Dark Mode", "transparent", "white"),
    "White Mode": BoardThemePreset("White Mode", "transparent", "black"),
}

DEFAULT_STICKER_PRESET = "Snow"
DEFAULT_BOARD_PRESET = "Dark Mode"


def get_sticker_preset(
    name: str,
    custom: dict[str, StickerPreset] | None = None,
) -> StickerPreset | None:
    if custom and name in custom:
        return custom[name]
    return STICKER_PRESETS.get(name)


def get_board_preset(
    name: str,
    custom: dict[str, BoardThemePreset] | None = None,
) -> BoardThemePreset | None:
    if custom and name in custom:
        return custom[name]
    return BOARD_PRESETS.get(name)
```

- [ ] **Step 4: 프리셋 테스트 통과 확인**

```bash
uv run pytest tests/test_presets.py -v
```

Expected: All PASSED

- [ ] **Step 5: 새 데이터 모델 테스트 작성**

`tests/test_sticker.py` 전체 교체:

```python
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
```

- [ ] **Step 6: 실패 확인**

```bash
uv run pytest tests/test_sticker.py -v
```

Expected: FAIL (StickerColors 미존재, color/border 필드 변경)

- [ ] **Step 7: sticker.py 재작성**

```python
# src/sticker0/sticker.py
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class StickerColors:
    border: str = "white"
    text: str = "white"
    area: str = "transparent"


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
    colors: StickerColors = field(default_factory=StickerColors)
    minimized: bool = False
    position: StickerPosition = field(default_factory=StickerPosition)
    size: StickerSize = field(default_factory=StickerSize)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "colors": {
                "border": self.colors.border,
                "text": self.colors.text,
                "area": self.colors.area,
            },
            "minimized": self.minimized,
            "position": {"x": self.position.x, "y": self.position.y},
            "size": {"width": self.size.width, "height": self.size.height},
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Sticker:
        now = datetime.now(timezone.utc).isoformat()
        colors_data = data.get("colors")
        if colors_data is not None:
            colors = StickerColors(
                border=colors_data.get("border", "white"),
                text=colors_data.get("text", "white"),
                area=colors_data.get("area", "transparent"),
            )
        else:
            # Legacy v0.2.0 migration: 기존 color 필드 무시, 기본 Snow 적용
            colors = StickerColors()
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            content=data.get("content", ""),
            colors=colors,
            minimized=data.get("minimized", False),
            position=StickerPosition(**data.get("position", {})),
            size=StickerSize(**data.get("size", {})),
            created_at=datetime.fromisoformat(data.get("created_at", now)),
            updated_at=datetime.fromisoformat(data.get("updated_at", now)),
        )

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
```

- [ ] **Step 8: sticker + presets 테스트 통과 확인**

```bash
uv run pytest tests/test_sticker.py tests/test_presets.py -v
```

Expected: All PASSED

- [ ] **Step 9: Commit**

```bash
git add src/sticker0/sticker.py src/sticker0/presets.py \
        tests/test_sticker.py tests/test_presets.py
git commit -m "feat: replace StickerColor/BorderType with StickerColors + presets system"
```

---

## Task 2: Config 재작성 + Atomic Write

**Files:**
- Modify: `src/sticker0/config.py`
- Modify: `tests/test_config.py`

- [ ] **Step 1: 새 config 테스트 작성**

`tests/test_config.py` 전체 교체:

```python
# tests/test_config.py
import os
import pytest
from pathlib import Path
from sticker0.config import AppConfig, BoardTheme, BorderConfig


def test_defaults_when_no_file(tmp_path):
    config = AppConfig.load(path=tmp_path / ".stkrc")
    assert config.board_theme.background == "transparent"
    assert config.board_theme.indicator == "white"
    assert config.border.top == "double"
    assert config.border.sides == "single"
    assert config.defaults.width == 30
    assert config.defaults.height == 10
    assert config.defaults.preset == "Snow"
    assert config.keybindings.new == "n"
    assert config.keybindings.quit == "q"


def test_load_board_theme_from_toml(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[theme]
background = "black"
indicator = "white"
""", encoding="utf-8")
    config = AppConfig.load(path=rc)
    assert config.board_theme.background == "black"
    assert config.board_theme.indicator == "white"


def test_load_border_config_from_toml(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[border]
top = "heavy"
sides = "double"
""", encoding="utf-8")
    config = AppConfig.load(path=rc)
    assert config.border.top == "heavy"
    assert config.border.sides == "double"


def test_load_custom_sticker_presets(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[presets.sticker.Fire]
border = "#ff0000"
text = "#ffffff"
area = "#330000"
""", encoding="utf-8")
    config = AppConfig.load(path=rc)
    assert "Fire" in config.sticker_presets
    assert config.sticker_presets["Fire"].border == "#ff0000"


def test_load_custom_board_presets(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[presets.board.Solarized]
background = "#002b36"
indicator = "#839496"
""", encoding="utf-8")
    config = AppConfig.load(path=rc)
    assert "Solarized" in config.board_presets
    assert config.board_presets["Solarized"].background == "#002b36"


def test_partial_config_uses_defaults(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text('[border]\ntop = "heavy"\n', encoding="utf-8")
    config = AppConfig.load(path=rc)
    assert config.border.top == "heavy"
    assert config.border.sides == "single"  # default
    assert config.board_theme.indicator == "white"  # default


def test_save_board_theme_creates_file(tmp_path):
    rc = tmp_path / ".stkrc"
    config = AppConfig.load(path=rc)
    config.board_theme = BoardTheme(background="black", indicator="white")
    config.save_board_theme(path=rc)
    assert rc.exists()
    reloaded = AppConfig.load(path=rc)
    assert reloaded.board_theme.background == "black"
    assert reloaded.board_theme.indicator == "white"


def test_save_board_theme_preserves_other_sections(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[border]
top = "heavy"
sides = "double"

[keybindings]
new = "a"
""", encoding="utf-8")
    config = AppConfig.load(path=rc)
    config.board_theme = BoardTheme(background="black", indicator="white")
    config.save_board_theme(path=rc)
    reloaded = AppConfig.load(path=rc)
    assert reloaded.board_theme.background == "black"
    assert reloaded.border.top == "heavy"
    assert reloaded.keybindings.new == "a"


def test_save_board_theme_atomic_write(tmp_path):
    """Atomic write: 중간에 실패해도 원본 파일이 손상되지 않아야 함."""
    rc = tmp_path / ".stkrc"
    rc.write_text('[border]\ntop = "heavy"\n', encoding="utf-8")
    config = AppConfig.load(path=rc)
    config.board_theme = BoardTheme(background="white", indicator="black")
    config.save_board_theme(path=rc)
    # tmp 파일이 남아있지 않아야 함
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert len(tmp_files) == 0
    # 원본이 정상
    reloaded = AppConfig.load(path=rc)
    assert reloaded.board_theme.background == "white"


def test_invalid_border_style_uses_default(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text('[border]\ntop = "invalid_style"\n', encoding="utf-8")
    config = AppConfig.load(path=rc)
    # 잘못된 값은 그대로 저장 (유효성 검증은 widget에서)
    assert config.border.top == "invalid_style"
```

- [ ] **Step 2: 실패 확인**

```bash
uv run pytest tests/test_config.py -v
```

Expected: FAIL (BoardTheme 미존재)

- [ ] **Step 3: config.py 재작성**

```python
# src/sticker0/config.py
from __future__ import annotations
import os
import re
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from sticker0.presets import StickerPreset, BoardThemePreset

CONFIG_PATH = Path.home() / ".stkrc"


@dataclass
class BoardTheme:
    background: str = "transparent"
    indicator: str = "white"


@dataclass
class BorderConfig:
    top: str = "double"
    sides: str = "single"


@dataclass
class DefaultsConfig:
    width: int = 30
    height: int = 10
    preset: str = "Snow"


@dataclass
class KeybindingsConfig:
    new: str = "n"
    delete: str = "d"
    quit: str = "q"


@dataclass
class AppConfig:
    board_theme: BoardTheme = field(default_factory=BoardTheme)
    border: BorderConfig = field(default_factory=BorderConfig)
    defaults: DefaultsConfig = field(default_factory=DefaultsConfig)
    keybindings: KeybindingsConfig = field(default_factory=KeybindingsConfig)
    sticker_presets: dict[str, StickerPreset] = field(default_factory=dict)
    board_presets: dict[str, BoardThemePreset] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path = CONFIG_PATH) -> AppConfig:
        if not path.exists():
            return cls()
        with open(path, "rb") as f:
            data = tomllib.load(f)
        config = cls()
        # Board theme
        if (t := data.get("theme")) is not None:
            config.board_theme.background = t.get("background", "transparent")
            config.board_theme.indicator = t.get("indicator", "white")
        # Border
        if (b := data.get("border")) is not None:
            config.border.top = b.get("top", "double")
            config.border.sides = b.get("sides", "single")
        # Defaults
        if (d := data.get("defaults")) is not None:
            config.defaults.width = d.get("width", 30)
            config.defaults.height = d.get("height", 10)
            config.defaults.preset = d.get("preset", "Snow")
        # Keybindings
        if (kb := data.get("keybindings")) is not None:
            config.keybindings.new = kb.get("new", "n")
            config.keybindings.delete = kb.get("delete", "d")
            config.keybindings.quit = kb.get("quit", "q")
        # Custom presets
        presets_data = data.get("presets", {})
        if (sp := presets_data.get("sticker")) is not None:
            for name, vals in sp.items():
                config.sticker_presets[name] = StickerPreset(
                    name=name,
                    border=vals.get("border", "white"),
                    text=vals.get("text", "white"),
                    area=vals.get("area", "transparent"),
                )
        if (bp := presets_data.get("board")) is not None:
            for name, vals in bp.items():
                config.board_presets[name] = BoardThemePreset(
                    name=name,
                    background=vals.get("background", "transparent"),
                    indicator=vals.get("indicator", "white"),
                )
        return config

    def save_board_theme(self, path: Path = CONFIG_PATH) -> None:
        """보드 테마를 .stkrc [theme] 섹션에 atomic write."""
        theme_lines = (
            "[theme]\n"
            f'background = "{self.board_theme.background}"\n'
            f'indicator = "{self.board_theme.indicator}"\n'
        )
        if path.exists():
            content = path.read_text(encoding="utf-8")
            # [theme] 섹션 찾기 및 교체
            pattern = r"\[theme\]\n(?:[^\[]*?)(?=\n\[|\Z)"
            if re.search(pattern, content):
                content = re.sub(pattern, theme_lines.rstrip(), content)
            else:
                content = content.rstrip() + "\n\n" + theme_lines
        else:
            content = theme_lines
        # Atomic write
        fd, tmp_path_str = tempfile.mkstemp(
            dir=path.parent, suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path_str, str(path))
        except BaseException:
            try:
                os.unlink(tmp_path_str)
            except OSError:
                pass
            raise
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
uv run pytest tests/test_config.py -v
```

Expected: All PASSED

- [ ] **Step 5: Commit**

```bash
git add src/sticker0/config.py tests/test_config.py
git commit -m "feat: rewrite config with BoardTheme, top/sides border, atomic write, custom presets"
```

---

## Task 3: StickerWidget 3색 스타일링 + 테두리 스타일

**Files:**
- Modify: `src/sticker0/widgets/sticker_widget.py`

이 태스크는 sticker_widget.py에서 기존 `StickerColor`/`BorderType` 참조를 모두 새 시스템으로 교체한다. 최소화/클램프는 Task 4, 5에서 처리.

- [ ] **Step 1: sticker_widget.py 3색 시스템 적용**

기존 `COLOR_MAP`, `BORDER_MAP`, `StickerColor`, `BorderType` import 제거. 새 스타일링 로직 적용.

```python
# src/sticker0/widgets/sticker_widget.py
from __future__ import annotations
import time
from textual.widget import Widget
from textual.widgets import TextArea
from textual.app import ComposeResult
from textual.events import MouseDown, MouseMove, MouseUp
from textual.css.query import NoMatches
from sticker0.sticker import Sticker

# 테두리 스타일 이름 → Textual border 스타일
BORDER_STYLE_MAP: dict[str, str] = {
    "single": "solid",
    "double": "double",
    "heavy": "heavy",
    "simple": "ascii",
}

_DRAG_MOVE = "move"
_DRAG_RESIZE_RIGHT = "resize_right"
_DRAG_RESIZE_LEFT = "resize_left"
_DRAG_RESIZE_H = "resize_h"

DOUBLE_CLICK_INTERVAL = 0.4


class StickerWidget(Widget):
    DEFAULT_CSS = """
    StickerWidget {
        position: absolute;
        min-width: 20;
        min-height: 3;
        background: transparent;
    }
    StickerWidget TextArea {
        height: 1fr;
        border: none;
        padding: 0 2 0 1;
    }
    StickerWidget TextArea:focus {
        border: none;
    }
    """

    MIN_WIDTH = 20
    MIN_HEIGHT = 5
    MINIMIZED_HEIGHT = 3
    can_focus = True

    def __init__(self, sticker: Sticker, **kwargs) -> None:
        super().__init__(**kwargs)
        self.sticker = sticker
        self._drag_start: tuple[int, int] | None = None
        self._drag_origin: tuple[int, int] = (0, 0)
        self._drag_mode: str = _DRAG_MOVE
        self._last_top_click: float = 0.0

    def on_mount(self) -> None:
        self._apply_sticker_styles()

    def _get_board_background(self) -> str:
        """보드 테마의 background 색상 조회."""
        try:
            board = self.app.query_one("StickerBoard")
            return getattr(board, "board_bg", "transparent")
        except NoMatches:
            return "transparent"

    def _get_border_config(self) -> tuple[str, str]:
        """config에서 border top/sides 스타일 조회. (top_textual, sides_textual) 반환."""
        try:
            config = self.app.config
            top = BORDER_STYLE_MAP.get(config.border.top, "double")
            sides = BORDER_STYLE_MAP.get(config.border.sides, "solid")
            return (top, sides)
        except AttributeError:
            return ("double", "solid")

    def _apply_sticker_styles(self) -> None:
        colors = self.sticker.colors
        # Area color: transparent → 보드 배경 상속
        area_color = colors.area
        if area_color == "transparent":
            area_color = self._get_board_background()
        self.styles.background = area_color
        self.styles.color = colors.text

        # Border style from config
        top_style, sides_style = self._get_border_config()
        self.styles.border = (sides_style, colors.border)
        self.styles.border_top = (top_style, colors.border)

        # Position and size
        self.styles.offset = (self.sticker.position.x, self.sticker.position.y)
        self.styles.width = self.sticker.size.width
        if self.sticker.minimized:
            self.styles.height = self.MINIMIZED_HEIGHT
        else:
            self.styles.height = self.sticker.size.height

        # TextArea 스크롤바 색상
        try:
            editor = self._get_editor()
            editor.styles.scrollbar_color = colors.text
            editor.styles.scrollbar_background = colors.area if colors.area != "transparent" else area_color
        except NoMatches:
            pass

    def compose(self) -> ComposeResult:
        editor_id = f"sticker-editor-{self.sticker.id}"
        yield TextArea(self.sticker.content, id=editor_id)

    def _get_editor(self) -> TextArea:
        return self.query_one(f"#sticker-editor-{self.sticker.id}", TextArea)

    def _classify_border(self, x: int, y: int) -> str | None:
        w = self.outer_size.width
        h = self.outer_size.height
        if y == 0:
            return _DRAG_MOVE
        if self.sticker.minimized:
            return None  # 최소화 상태에서 리사이즈 불가
        if x == 0:
            return _DRAG_RESIZE_LEFT
        if x == w - 1:
            return _DRAG_RESIZE_RIGHT
        if y == h - 1:
            return _DRAG_RESIZE_H
        return None

    def _move_to_front(self) -> None:
        parent = self.parent
        if parent is not None:
            children = list(parent.children)
            if children and children[-1] is not self:
                parent.move_child(self, after=children[-1])

    def on_mouse_down(self, event: MouseDown) -> None:
        self._move_to_front()
        mode = self._classify_border(event.x, event.y)

        # 상단 테두리 더블클릭 → 최소화/복원 토글
        if mode == _DRAG_MOVE:
            now = time.monotonic()
            if now - self._last_top_click < DOUBLE_CLICK_INTERVAL:
                self._toggle_minimize()
                self._last_top_click = 0.0
                event.stop()
                return
            self._last_top_click = now

        if mode is None:
            if self.sticker.minimized:
                event.stop()  # 최소화 시 내부 클릭 차단
            return

        event.stop()
        self._drag_start = (event.screen_x, event.screen_y)
        self._drag_mode = mode
        if mode == _DRAG_MOVE:
            self._drag_origin = (self.sticker.position.x, self.sticker.position.y)
        elif mode == _DRAG_RESIZE_LEFT:
            self._drag_origin = (self.sticker.position.x, self.sticker.size.width)
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

    def _clamp_position(self) -> None:
        """스티커 중앙점이 화면 우변/하변을 넘지 않도록 보정."""
        try:
            screen_w = self.screen.size.width
            screen_h = self.screen.size.height
        except Exception:
            return
        cx = self.sticker.position.x + self.sticker.size.width // 2
        cy = self.sticker.position.y + self.sticker.size.height // 2
        if cx > screen_w:
            self.sticker.position.x = screen_w - self.sticker.size.width // 2
        if cy > screen_h:
            self.sticker.position.y = screen_h - self.sticker.size.height // 2
        self.sticker.position.x = max(0, self.sticker.position.x)
        self.sticker.position.y = max(0, self.sticker.position.y)
        self.styles.offset = (self.sticker.position.x, self.sticker.position.y)

    def _apply_drag(self, dx: int, dy: int) -> None:
        if self._drag_mode == _DRAG_MOVE:
            new_x = max(0, self._drag_origin[0] + dx)
            new_y = max(0, self._drag_origin[1] + dy)
            self.sticker.position.x = new_x
            self.sticker.position.y = new_y
            self.styles.offset = (new_x, new_y)
            self._clamp_position()
        elif self._drag_mode == _DRAG_RESIZE_RIGHT:
            new_w = max(self.MIN_WIDTH, self._drag_origin[0] + dx)
            self.sticker.size.width = new_w
            self.styles.width = new_w
        elif self._drag_mode == _DRAG_RESIZE_LEFT:
            new_x = max(0, self._drag_origin[0] + dx)
            new_w = max(self.MIN_WIDTH, self._drag_origin[1] - dx)
            self.sticker.position.x = new_x
            self.sticker.size.width = new_w
            self.styles.offset = (new_x, self.sticker.position.y)
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
            try:
                board = self.app.query_one("StickerBoard")
                board.save_sticker(self.sticker)
            except NoMatches:
                pass

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self.sticker.content = event.text_area.text
        try:
            board = self.app.query_one("StickerBoard")
            board.save_sticker(self.sticker)
        except NoMatches:
            pass

    def _toggle_minimize(self) -> None:
        """최소화/복원 토글."""
        self._set_minimized(not self.sticker.minimized)

    def _set_minimized(self, minimized: bool) -> None:
        from textual.widgets import Static
        self.sticker.minimized = minimized
        if minimized:
            self.styles.height = self.MINIMIZED_HEIGHT
            try:
                editor = self._get_editor()
                editor.display = False
            except NoMatches:
                pass
            # 첫 줄 텍스트 + ellipsis 표시
            first_line = self.sticker.content.split("\n")[0] if self.sticker.content else ""
            max_w = max(1, self.sticker.size.width - 4)
            if len(first_line) > max_w:
                first_line = first_line[: max_w - 3] + "..."
            self.mount(Static(first_line, id="minimized-label"))
        else:
            self.styles.height = self.sticker.size.height
            try:
                editor = self._get_editor()
                editor.display = True
            except NoMatches:
                pass
            try:
                self.query_one("#minimized-label").remove()
            except NoMatches:
                pass
        try:
            board = self.app.query_one("StickerBoard")
            board.save_sticker(self.sticker)
        except NoMatches:
            pass

    def _show_context_menu(self, screen_x: int, screen_y: int) -> None:
        from sticker0.widgets.context_menu import ContextMenu
        board = self.app.query_one("StickerBoard")
        # 메뉴 상호 배제: 모든 기존 메뉴 닫기
        board.close_all_menus()
        local_x = screen_x - board.region.x
        local_y = screen_y - board.region.y
        indicator = getattr(board, "indicator", "white")
        menu = ContextMenu(
            sticker_id=self.sticker.id,
            x=local_x,
            y=local_y,
            indicator=indicator,
            minimized=self.sticker.minimized,
        )
        board.mount(menu)

    def _enter_edit_mode(self) -> None:
        if not self.sticker.minimized:
            self._get_editor().focus()

    def on_key(self, event) -> None:
        if event.key in ("d", "delete"):
            try:
                board = self.app.query_one("StickerBoard")
                board.delete_sticker(self.sticker.id)
            except NoMatches:
                pass
            event.stop()
        elif event.key == "enter":
            self._enter_edit_mode()
            event.stop()
```

- [ ] **Step 2: 실패 확인 (기존 테스트)**

```bash
uv run pytest tests/test_app.py -v 2>&1 | head -40
```

Expected: 다수 FAIL (import 에러 — StickerColor 참조, color 필드 참조 등). 이 단계에서는 test_app.py 실패가 예상됨. Task 7에서 테스트 전체 업데이트.

- [ ] **Step 3: Commit (WIP)**

```bash
git add src/sticker0/widgets/sticker_widget.py
git commit -m "wip: rewrite sticker_widget for 3-color system, minimize, clamp"
```

---

## Task 4: ContextMenu 수정

**Files:**
- Modify: `src/sticker0/widgets/context_menu.py`

- [ ] **Step 1: context_menu.py 재작성**

```python
# src/sticker0/widgets/context_menu.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Button
from textual.message import Message


class ContextMenu(Widget):
    """스티커 우클릭 팝업 메뉴."""

    DEFAULT_CSS = """
    ContextMenu {
        position: absolute;
        width: 20;
        height: auto;
        background: $surface;
        layer: menu;
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

    def __init__(
        self,
        sticker_id: str,
        x: int,
        y: int,
        indicator: str = "white",
        minimized: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.sticker_id = sticker_id
        self._menu_x = x
        self._menu_y = y
        self._indicator = indicator
        self._minimized = minimized

    def on_mount(self) -> None:
        self.styles.offset = (self._menu_x, self._menu_y)
        self.styles.border = ("round", self._indicator)
        self.styles.color = self._indicator

    def compose(self) -> ComposeResult:
        if self._minimized:
            yield Button("복원", id="menu-restore", variant="default")
        else:
            yield Button("편집", id="menu-edit", variant="default")
            yield Button("최소화", id="menu-minimize", variant="default")
        yield Button("프리셋 변경", id="menu-preset", variant="default")
        yield Button("삭제", id="menu-delete", variant="error")
        yield Button("닫기", id="menu-close", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "menu-close":
            self.remove()
            return
        action_map = {
            "menu-edit": "edit",
            "menu-delete": "delete",
            "menu-preset": "preset",
            "menu-minimize": "minimize",
            "menu-restore": "restore",
        }
        action = action_map.get(event.button.id or "", "")
        if action:
            self.post_message(self.MenuAction(action, self.sticker_id))
            self.remove()
```

- [ ] **Step 2: Commit**

```bash
git add src/sticker0/widgets/context_menu.py
git commit -m "feat: update ContextMenu with dynamic indicator color, minimize/restore items"
```

---

## Task 5: PresetPicker 신규 (ColorPicker 대체)

**Files:**
- Create: `src/sticker0/widgets/preset_picker.py`
- Delete: `src/sticker0/widgets/color_picker.py`

- [ ] **Step 1: preset_picker.py 작성**

```python
# src/sticker0/widgets/preset_picker.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Button
from textual.message import Message
from sticker0.sticker import StickerColors
from sticker0.presets import StickerPreset, STICKER_PRESETS


class PresetPicker(Widget):
    """스티커 프리셋 선택 팝업."""

    DEFAULT_CSS = """
    PresetPicker {
        position: absolute;
        width: 22;
        height: auto;
        background: $surface;
        layer: menu;
    }
    PresetPicker Button {
        width: 1fr;
        height: 1;
        border: none;
        background: transparent;
    }
    PresetPicker Button:hover {
        background: $accent 20%;
    }
    """

    class PresetSelected(Message):
        def __init__(self, sticker_id: str, colors: StickerColors) -> None:
            super().__init__()
            self.sticker_id = sticker_id
            self.colors = colors

    def __init__(
        self,
        sticker_id: str,
        x: int,
        y: int,
        indicator: str = "white",
        custom_presets: dict[str, StickerPreset] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.sticker_id = sticker_id
        self._x = x
        self._y = y
        self._indicator = indicator
        self._all_presets: dict[str, StickerPreset] = dict(STICKER_PRESETS)
        if custom_presets:
            self._all_presets.update(custom_presets)

    def on_mount(self) -> None:
        self.styles.offset = (self._x, self._y)
        self.styles.border = ("round", self._indicator)
        self.styles.color = self._indicator

    def compose(self) -> ComposeResult:
        for name in self._all_presets:
            yield Button(name, id=f"preset-{name}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        name = (event.button.id or "").removeprefix("preset-")
        preset = self._all_presets.get(name)
        if preset:
            colors = StickerColors(
                border=preset.border,
                text=preset.text,
                area=preset.area,
            )
            self.post_message(self.PresetSelected(self.sticker_id, colors))
        self.remove()
```

- [ ] **Step 2: color_picker.py 삭제**

```bash
rm src/sticker0/widgets/color_picker.py
```

- [ ] **Step 3: Commit**

```bash
git add src/sticker0/widgets/preset_picker.py
git rm src/sticker0/widgets/color_picker.py
git commit -m "feat: replace ColorPicker with PresetPicker for 3-color preset selection"
```

---

## Task 6: ThemePicker 신규 + BoardMenu 수정

**Files:**
- Create: `src/sticker0/widgets/theme_picker.py`
- Modify: `src/sticker0/widgets/board_menu.py`

- [ ] **Step 1: theme_picker.py 작성**

```python
# src/sticker0/widgets/theme_picker.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Button
from textual.message import Message
from sticker0.presets import BoardThemePreset, BOARD_PRESETS


class ThemePicker(Widget):
    """보드 테마 선택 팝업."""

    DEFAULT_CSS = """
    ThemePicker {
        position: absolute;
        width: 22;
        height: auto;
        background: $surface;
        layer: menu;
    }
    ThemePicker Button {
        width: 1fr;
        height: 1;
        border: none;
        background: transparent;
    }
    ThemePicker Button:hover {
        background: $accent 20%;
    }
    """

    class ThemeSelected(Message):
        def __init__(self, background: str, indicator: str) -> None:
            super().__init__()
            self.background = background
            self.indicator = indicator

    def __init__(
        self,
        x: int,
        y: int,
        indicator: str = "white",
        custom_presets: dict[str, BoardThemePreset] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._x = x
        self._y = y
        self._indicator = indicator
        self._all_presets: dict[str, BoardThemePreset] = dict(BOARD_PRESETS)
        if custom_presets:
            self._all_presets.update(custom_presets)

    def on_mount(self) -> None:
        self.styles.offset = (self._x, self._y)
        self.styles.border = ("round", self._indicator)
        self.styles.color = self._indicator

    def compose(self) -> ComposeResult:
        for name in self._all_presets:
            yield Button(name, id=f"theme-{name}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        name = (event.button.id or "").removeprefix("theme-")
        preset = self._all_presets.get(name)
        if preset:
            self.post_message(
                self.ThemeSelected(preset.background, preset.indicator)
            )
        self.remove()
```

- [ ] **Step 2: board_menu.py 수정**

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
        background: $surface;
        layer: menu;
    }
    BoardMenu Button {
        width: 1fr;
        height: 1;
        border: none;
        background: transparent;
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

    def __init__(
        self,
        x: int,
        y: int,
        indicator: str = "white",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._menu_x = x
        self._menu_y = y
        self._indicator = indicator

    def on_mount(self) -> None:
        self.styles.offset = (self._menu_x, self._menu_y)
        self.styles.border = ("round", self._indicator)
        self.styles.color = self._indicator

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

- [ ] **Step 3: Commit**

```bash
git add src/sticker0/widgets/theme_picker.py src/sticker0/widgets/board_menu.py
git commit -m "feat: add ThemePicker widget, update BoardMenu with dynamic indicator color"
```

---

## Task 7: Board 업데이트 + App 연결

**Files:**
- Modify: `src/sticker0/widgets/board.py`
- Modify: `src/sticker0/app.py`

- [ ] **Step 1: board.py 재작성**

```python
# src/sticker0/widgets/board.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.events import MouseUp, Resize
from sticker0.config import AppConfig, BoardTheme
from sticker0.sticker import Sticker, StickerColors, StickerSize
from sticker0.presets import STICKER_PRESETS, DEFAULT_STICKER_PRESET
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
        self.board_bg = config.board_theme.background
        self.indicator = config.board_theme.indicator

    def on_mount(self) -> None:
        self._apply_board_theme()

    def _apply_board_theme(self) -> None:
        self.styles.background = self.board_bg

    def compose(self) -> ComposeResult:
        for sticker in self.storage.load_all():
            yield StickerWidget(sticker)

    def save_sticker(self, sticker: Sticker) -> None:
        self.storage.save(sticker)

    def add_new_sticker(self, x: int | None = None, y: int | None = None) -> None:
        cfg = self.config
        # 기본 프리셋으로 색상 결정
        preset_name = cfg.defaults.preset
        preset = STICKER_PRESETS.get(preset_name)
        if preset:
            colors = StickerColors(
                border=preset.border, text=preset.text, area=preset.area,
            )
        else:
            colors = StickerColors()
        sticker = Sticker(
            colors=colors,
            size=StickerSize(
                width=cfg.defaults.width,
                height=cfg.defaults.height,
            ),
        )
        if x is not None and y is not None:
            sticker.position.x = x
            sticker.position.y = y
        else:
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

    def close_all_menus(self) -> None:
        """모든 팝업 메뉴/피커 닫기 (상호 배제)."""
        from sticker0.widgets.context_menu import ContextMenu
        from sticker0.widgets.board_menu import BoardMenu
        from sticker0.widgets.preset_picker import PresetPicker
        from sticker0.widgets.theme_picker import ThemePicker
        for w in self.query(ContextMenu):
            w.remove()
        for w in self.query(BoardMenu):
            w.remove()
        for w in self.query(PresetPicker):
            w.remove()
        for w in self.query(ThemePicker):
            w.remove()

    def on_mouse_up(self, event: MouseUp) -> None:
        if event.button == 3:
            self.close_all_menus()
            from sticker0.widgets.board_menu import BoardMenu
            menu = BoardMenu(
                x=event.x, y=event.y, indicator=self.indicator,
            )
            self.mount(menu)

    def on_resize(self, event: Resize) -> None:
        """터미널 크기 변경 시 모든 스티커 위치 보정."""
        for widget in self.query(StickerWidget):
            widget._clamp_position()

    def on_context_menu_menu_action(self, message) -> None:
        if message.action == "delete":
            self.delete_sticker(message.sticker_id)
        elif message.action == "edit":
            for widget in self.query(StickerWidget):
                if widget.sticker.id == message.sticker_id:
                    widget._enter_edit_mode()
        elif message.action == "preset":
            from sticker0.widgets.preset_picker import PresetPicker
            self.close_all_menus()
            picker = PresetPicker(
                sticker_id=message.sticker_id,
                x=22,
                y=3,
                indicator=self.indicator,
                custom_presets=self.config.sticker_presets,
            )
            self.mount(picker)
        elif message.action == "minimize":
            for widget in self.query(StickerWidget):
                if widget.sticker.id == message.sticker_id:
                    widget._set_minimized(True)
        elif message.action == "restore":
            for widget in self.query(StickerWidget):
                if widget.sticker.id == message.sticker_id:
                    widget._set_minimized(False)

    def on_board_menu_menu_action(self, message) -> None:
        if message.action == "create":
            self.add_new_sticker(x=message.x, y=message.y)
        elif message.action == "theme":
            from sticker0.widgets.theme_picker import ThemePicker
            self.close_all_menus()
            picker = ThemePicker(
                x=message.x,
                y=message.y,
                indicator=self.indicator,
                custom_presets=self.config.board_presets,
            )
            self.mount(picker)
        elif message.action == "quit":
            self.app.exit()

    def on_preset_picker_preset_selected(self, message) -> None:
        for widget in self.query(StickerWidget):
            if widget.sticker.id == message.sticker_id:
                widget.sticker.colors = message.colors
                widget._apply_sticker_styles()
                widget.refresh()
                self.storage.save(widget.sticker)
                break

    def on_theme_picker_theme_selected(self, message) -> None:
        self.board_bg = message.background
        self.indicator = message.indicator
        self._apply_board_theme()
        # 모든 스티커 스타일 재적용 (transparent 상속 반영)
        for widget in self.query(StickerWidget):
            widget._apply_sticker_styles()
            widget.refresh()
        # config 업데이트 + 저장
        self.config.board_theme = BoardTheme(
            background=message.background,
            indicator=message.indicator,
        )
        self.config.save_board_theme()
```

- [ ] **Step 2: app.py 수정**

`app.py`에 `config` 속성이 접근 가능하도록 확인. 현재 `self.config`가 App 인스턴스에 있으므로 `self.app.config`로 접근 가능.

```python
# src/sticker0/app.py — 변경 없음 (config가 이미 self.config로 접근 가능)
# 단, StickerColor import 제거 필요
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

- [ ] **Step 3: Commit**

```bash
git add src/sticker0/widgets/board.py src/sticker0/app.py
git commit -m "feat: update board with theme support, resize clamp, menu exclusion, preset/theme pickers"
```

---

## Task 8: 전체 테스트 업데이트 + 버전 범프

**Files:**
- Modify: `tests/test_app.py`
- Modify: `tests/test_storage.py` (필요 시)

- [ ] **Step 1: test_app.py 전체 교체**

기존 `StickerColor`, `BorderType` 참조를 모두 제거하고 새 데이터 모델에 맞게 교체. 새 기능 테스트 추가.

```python
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
    """우클릭 → 프리셋 변경 → Ink 선택 → 색상 변경 확인."""
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
        await pilot.click(picker.query_one("#preset-Ink"))
        await pilot.pause(0.1)
        loaded = tmp_storage.load(s.id)
        assert loaded.colors.border == "black"
        assert loaded.colors.text == "black"
        assert loaded.colors.area == "transparent"


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
        await pilot.click(picker.query_one("#theme-Dark Base"))
        await pilot.pause(0.1)
        assert board.board_bg == "black"
        assert board.indicator == "white"


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
async def test_new_sticker_has_snow_preset_colors(tmp_storage):
    """새 스티커는 Snow 프리셋 기본 색상."""
    from sticker0.widgets.sticker_widget import StickerWidget
    app = Sticker0App(storage=tmp_storage)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("n")
        await pilot.pause(0.1)
        widget = app.query_one(StickerWidget)
        assert widget.sticker.colors.border == "white"
        assert widget.sticker.colors.text == "white"
        assert widget.sticker.colors.area == "transparent"
```

- [ ] **Step 2: 테스트 실행**

```bash
uv run pytest -v
```

Expected: 테스트 실패 시 원인 분석 후 수정. 모든 테스트 통과될 때까지 반복.

**주의:** sticker_widget.py에서 `on_mount` 시 `self.app.config` 접근이 필요한데, 테스트에서 `Sticker0App`은 `self.config`로 설정됨. `_get_border_config()`에서 `self.app.config`로 접근.

**주의:** 기존 `test_storage.py`에서 `Sticker.from_dict`가 변경되었으므로 확인 필요. `from_dict`는 `colors` 필드가 없는 레거시 JSON도 처리하므로 기존 저장 파일 호환.

- [ ] **Step 3: 버전 업데이트**

`pyproject.toml`:
```toml
version = "0.3.0"
```

`src/sticker0/__init__.py`:
```python
__version__ = "0.3.0"
```

- [ ] **Step 4: 전체 테스트 최종 확인**

```bash
uv run pytest -v --tb=short
```

Expected: All tests PASSED

- [ ] **Step 5: Commit**

```bash
git add tests/test_app.py tests/test_storage.py \
        pyproject.toml src/sticker0/__init__.py
git commit -m "test: update all tests for v0.3.0, bump version to 0.3.0"
```

---

## Verification

### 전체 테스트

```bash
uv run pytest -v
```

### 수동 동작 확인

```bash
uv run stk
```

체크리스트:
- [ ] 기본 Snow 프리셋으로 스티커 생성 (white border/text, transparent area)
- [ ] 상단 테두리 드래그 이동
- [ ] 좌/우/하단 테두리 리사이즈
- [ ] 스티커 우클릭 → 메뉴 텍스트 보임 (indicator 색상)
- [ ] 프리셋 변경 → Ink/Sky/Banana 색상 적용
- [ ] 최소화 (우클릭 또는 상단 더블클릭) → 3줄로 축소, 첫 줄만 표시
- [ ] 복원 (우클릭 또는 상단 더블클릭) → 원래 크기
- [ ] 최소화 상태에서 리사이즈/편집 불가, 이동만 가능
- [ ] 빈 영역 우클릭 → BoardMenu 텍스트 보임
- [ ] 테마 변경 → Dark Base/Light Base/White Mode 배경 적용
- [ ] 스티커 Transparent area → 보드 배경색 상속
- [ ] 메뉴 상호 배제 (스티커/보드 메뉴 동시 불가)
- [ ] 중앙점이 화면 밖으로 나가지 않음 (드래그 + 화면 축소)
- [ ] `q` 종료 후 재실행 → 모든 스티커 + 테마 복원

### 주요 API 참고

- `StickerColors(border, text, area)` — 스티커 3색 (replaces StickerColor)
- `BoardTheme(background, indicator)` — 보드 테마 2색
- `BorderConfig(top, sides)` — 테두리 스타일 (replaces BorderType)
- `BORDER_STYLE_MAP` — `{"single": "solid", "double": "double", "heavy": "heavy", "simple": "ascii"}`
- `config.save_board_theme()` — atomic write로 .stkrc [theme] 섹션 저장
- `board.close_all_menus()` — 메뉴 상호 배제 헬퍼
- `widget._clamp_position()` — 중앙점 화면 제약
- `widget._set_minimized(bool)` — 최소화/복원
