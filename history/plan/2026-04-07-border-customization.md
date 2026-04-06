# Border Customization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 스티커별 border 스타일을 context menu → BorderPicker 팝업으로 변경할 수 있게 하고, 기존 `~/.stkrc [border]` + top/sides 분리 구조를 완전 제거한다.

**Architecture:** `Sticker` dataclass에 `line` 필드를 추가하여 스티커별 Textual border 타입을 저장한다. `settings.toml [theme]`에 `sticker_line`을 추가하여 새 스티커 기본값으로 사용한다. `~/.stkrc`의 `[border]` 섹션 파싱과 `BorderConfig`는 완전 제거한다. 8종의 border 스타일(solid, heavy, round, double, ascii, inner, outer, dashed)을 BorderPicker 팝업으로 선택한다.

**Tech Stack:** Python 3.11+, Textual >= 0.80, TOML (tomllib), pytest

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `src/sticker0/sticker.py` | Modify | `line` 필드 + `BORDER_STYLES` 상수 + `DEFAULT_BORDER_LINE` |
| `src/sticker0/config.py` | Modify | `BorderConfig` 제거, `BoardTheme.sticker_line` 추가, load/save 변경 |
| `src/sticker0/widgets/sticker_widget.py` | Modify | `BORDER_STYLE_MAP`·`_get_border_config()` 제거, 통일 border 적용 |
| `src/sticker0/widgets/context_menu.py` | Modify | "Change Border" 버튼 추가 |
| `src/sticker0/widgets/border_picker.py` | Create | Border 스타일 선택 팝업 |
| `src/sticker0/widgets/board.py` | Modify | border 액션 핸들링, BorderPicker 메시지, close_all_menus 확장 |
| `README.md` | Modify | `[border]` 섹션 제거 |
| `src/sticker0/CLAUDE.md` | Modify | 데이터 모델·Config 문서 갱신 |
| `src/sticker0/widgets/CLAUDE.md` | Modify | 위젯 문서 갱신 (BorderPicker 추가, ContextMenu 액션) |
| `CLAUDE.md` | Modify | 파일 맵·핵심 패턴 갱신 |
| `tests/test_sticker.py` | Modify | `line` 필드 테스트 추가 |
| `tests/test_config.py` | Modify | `BorderConfig` 테스트 제거, `sticker_line` 테스트 추가 |
| `tests/test_app.py` | Modify | border 변경 통합 테스트 추가 |

---

### Task 1: Sticker dataclass — `line` 필드 추가

**Files:**
- Modify: `src/sticker0/sticker.py`
- Test: `tests/test_sticker.py`

- [ ] **Step 1: Write failing tests for `line` field**

`tests/test_sticker.py` 끝에 추가:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_sticker.py::test_sticker_line_default tests/test_sticker.py::test_sticker_line_roundtrip tests/test_sticker.py::test_sticker_line_migration_from_old_json tests/test_sticker.py::test_border_styles_constant -v`

Expected: FAIL — `Sticker` has no `line` attribute, `BORDER_STYLES` not defined

- [ ] **Step 3: Implement `line` field in Sticker**

`src/sticker0/sticker.py` 상단, import 아래에 상수 추가:

```python
BORDER_STYLES: list[str] = [
    "solid", "heavy", "round", "double", "ascii", "inner", "outer", "dashed",
]
DEFAULT_BORDER_LINE = "solid"
```

`Sticker` dataclass에 `line` 필드 추가 (`colors` 바로 뒤):

```python
@dataclass
class Sticker:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    colors: StickerColors = field(default_factory=StickerColors)
    line: str = DEFAULT_BORDER_LINE
    minimized: bool = False
    position: StickerPosition = field(default_factory=StickerPosition)
    size: StickerSize = field(default_factory=StickerSize)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
```

`to_dict()` 에 `line` 추가 (`"colors"` 뒤):

```python
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
            "line": self.line,
            "minimized": self.minimized,
            "position": {"x": self.position.x, "y": self.position.y},
            "size": {"width": self.size.width, "height": self.size.height},
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
```

`from_dict()` 에 `line` 파싱 추가 (`colors` 할당 뒤):

```python
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
            colors = StickerColors()
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            content=data.get("content", ""),
            colors=colors,
            line=data.get("line", DEFAULT_BORDER_LINE),
            minimized=data.get("minimized", False),
            position=StickerPosition(**data.get("position", {})),
            size=StickerSize(**data.get("size", {})),
            created_at=datetime.fromisoformat(data.get("created_at", now)),
            updated_at=datetime.fromisoformat(data.get("updated_at", now)),
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_sticker.py -v`

Expected: ALL PASS (새 테스트 4개 + 기존 테스트 6개)

- [ ] **Step 5: Commit**

```bash
git add src/sticker0/sticker.py tests/test_sticker.py
git commit -m "feat: add line field to Sticker for per-sticker border style"
```

---

### Task 2: Config — BorderConfig 제거, sticker_line 추가

**Files:**
- Modify: `src/sticker0/config.py`
- Modify: `tests/test_config.py`

- [ ] **Step 1: Update test_config.py — 기존 BorderConfig 테스트 제거, sticker_line 테스트 추가**

`tests/test_config.py` 전체를 다음으로 교체:

```python
# tests/test_config.py
import os
import pytest
from pathlib import Path
from sticker0.config import AppConfig, BoardTheme


def test_defaults_when_no_file(tmp_path):
    from sticker0.presets import (
        BOARD_PRESETS,
        DEFAULT_BOARD_PRESET,
        DEFAULT_STICKER_PRESET,
        STICKER_PRESETS,
    )
    from sticker0.sticker import DEFAULT_BORDER_LINE

    g = STICKER_PRESETS[DEFAULT_STICKER_PRESET]
    bg = BOARD_PRESETS[DEFAULT_BOARD_PRESET]
    config = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=tmp_path / "settings.toml",
    )
    assert config.board_theme.background == bg.background
    assert config.board_theme.indicator == bg.indicator
    assert config.board_theme.sticker_border == g.border
    assert config.board_theme.sticker_text == g.text
    assert config.board_theme.sticker_area == g.area
    assert config.board_theme.sticker_line == DEFAULT_BORDER_LINE
    assert config.defaults.width == 30
    assert config.defaults.height == 10
    assert config.defaults.preset == "Graphite"


def test_load_board_theme_from_settings_toml(tmp_path):
    """[theme]은 settings.toml에서 읽는다."""
    settings = tmp_path / "settings.toml"
    settings.write_text("""
[theme]
background = "black"
indicator = "white"
""", encoding="utf-8")
    config = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=settings,
    )
    assert config.board_theme.background == "black"
    assert config.board_theme.indicator == "white"


def test_load_theme_sticker_colors_from_settings_toml(tmp_path):
    """settings.toml [theme]의 border/text/area가 스티커 기본색으로 적용된다."""
    settings = tmp_path / "settings.toml"
    settings.write_text(
        """
[theme]
background = "black"
indicator = "white"
border = "#111111"
text = "#222222"
area = "#333333"
""",
        encoding="utf-8",
    )
    config = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=settings,
    )
    assert config.board_theme.sticker_border == "#111111"
    assert config.board_theme.sticker_text == "#222222"
    assert config.board_theme.sticker_area == "#333333"


def test_load_theme_sticker_line_from_settings_toml(tmp_path):
    """settings.toml [theme]의 line이 스티커 기본 border 스타일로 적용된다."""
    settings = tmp_path / "settings.toml"
    settings.write_text(
        """
[theme]
background = "black"
indicator = "white"
line = "heavy"
""",
        encoding="utf-8",
    )
    config = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=settings,
    )
    assert config.board_theme.sticker_line == "heavy"


def test_stkrc_theme_section_is_ignored(tmp_path):
    """~/.stkrc에 [theme]이 있어도 완전히 무시된다."""
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[theme]
background = "red"
indicator = "blue"
border = "#aabbcc"
""", encoding="utf-8")
    config = AppConfig.load(
        path=rc,
        settings_path=tmp_path / "settings.toml",
    )
    from sticker0.presets import BOARD_PRESETS, DEFAULT_BOARD_PRESET

    bg = BOARD_PRESETS[DEFAULT_BOARD_PRESET]
    assert config.board_theme.background == bg.background
    assert config.board_theme.indicator == bg.indicator


def test_stkrc_border_section_is_ignored(tmp_path):
    """~/.stkrc에 [border]가 있어도 완전히 무시된다 (deprecated)."""
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[border]
top = "heavy"
sides = "double"
""", encoding="utf-8")
    config = AppConfig.load(
        path=rc,
        settings_path=tmp_path / "settings.toml",
    )
    assert not hasattr(config, "border")


def test_settings_toml_takes_priority_over_defaults(tmp_path):
    """settings.toml의 [theme]이 있으면 기본값 대신 그 값을 사용한다."""
    settings = tmp_path / "settings.toml"
    settings.write_text("""
[theme]
background = "#2a2a2e"
indicator = "#d4d4d8"
""", encoding="utf-8")
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[theme]
background = "red"
""", encoding="utf-8")
    config = AppConfig.load(path=rc, settings_path=settings)
    assert config.board_theme.background == "#2a2a2e"
    assert config.board_theme.indicator == "#d4d4d8"


def test_load_custom_sticker_presets(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[presets.sticker.Fire]
border = "#ff0000"
text = "#ffffff"
area = "#330000"
""", encoding="utf-8")
    config = AppConfig.load(path=rc, settings_path=tmp_path / "settings.toml")
    assert "Fire" in config.sticker_presets
    assert config.sticker_presets["Fire"].border == "#ff0000"


def test_load_custom_board_presets(tmp_path):
    rc = tmp_path / ".stkrc"
    rc.write_text("""
[presets.board.Solarized]
background = "#002b36"
indicator = "#839496"
""", encoding="utf-8")
    config = AppConfig.load(path=rc, settings_path=tmp_path / "settings.toml")
    assert "Solarized" in config.board_presets
    assert config.board_presets["Solarized"].background == "#002b36"


def test_save_board_theme_creates_settings_toml(tmp_path):
    """save_board_theme()은 settings.toml을 생성한다."""
    from sticker0.presets import STICKER_PRESETS, DEFAULT_STICKER_PRESET
    from sticker0.sticker import DEFAULT_BORDER_LINE

    g = STICKER_PRESETS[DEFAULT_STICKER_PRESET]
    settings = tmp_path / "settings.toml"
    config = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=settings,
    )
    config.board_theme = BoardTheme(background="black", indicator="white")
    config.save_board_theme()
    assert settings.exists()
    reloaded = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=settings,
    )
    assert reloaded.board_theme.background == "black"
    assert reloaded.board_theme.indicator == "white"
    assert reloaded.board_theme.sticker_border == g.border
    assert reloaded.board_theme.sticker_text == g.text
    assert reloaded.board_theme.sticker_area == g.area
    assert reloaded.board_theme.sticker_line == DEFAULT_BORDER_LINE


def test_save_board_theme_includes_line(tmp_path):
    """save_board_theme()에서 line 값이 settings.toml에 저장된다."""
    settings = tmp_path / "settings.toml"
    config = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=settings,
    )
    config.board_theme.sticker_line = "round"
    config.save_board_theme()
    reloaded = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=settings,
    )
    assert reloaded.board_theme.sticker_line == "round"


def test_save_board_theme_does_not_touch_stkrc(tmp_path):
    """save_board_theme()은 ~/.stkrc를 수정하지 않는다."""
    rc = tmp_path / ".stkrc"
    original_content = '[defaults]\nwidth = 30\n'
    rc.write_text(original_content, encoding="utf-8")
    settings = tmp_path / "settings.toml"
    config = AppConfig.load(path=rc, settings_path=settings)
    config.board_theme = BoardTheme(background="black", indicator="white")
    config.save_board_theme()
    assert rc.read_text(encoding="utf-8") == original_content


def test_save_board_theme_preserves_other_settings_sections(tmp_path):
    """settings.toml에 [theme] 외 다른 섹션이 있으면 보존한다."""
    settings = tmp_path / "settings.toml"
    settings.write_text("""
[other]
foo = "bar"

[theme]
background = "old"
indicator = "old"
""", encoding="utf-8")
    config = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=settings,
    )
    config.board_theme = BoardTheme(background="new", indicator="new")
    config.save_board_theme()
    text = settings.read_text(encoding="utf-8")
    assert '[other]' in text
    assert 'foo = "bar"' in text
    reloaded = AppConfig.load(path=tmp_path / ".stkrc", settings_path=settings)
    assert reloaded.board_theme.background == "new"


def test_save_board_theme_atomic_write(tmp_path):
    """Atomic write: tmp 파일이 남아있지 않아야 함."""
    settings = tmp_path / "settings.toml"
    settings.write_text('[theme]\nbackground = "old"\n', encoding="utf-8")
    config = AppConfig.load(path=tmp_path / ".stkrc", settings_path=settings)
    config.board_theme = BoardTheme(background="white", indicator="black")
    config.save_board_theme()
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert len(tmp_files) == 0
    reloaded = AppConfig.load(path=tmp_path / ".stkrc", settings_path=settings)
    assert reloaded.board_theme.background == "white"


def test_save_board_theme_creates_parent_dir(tmp_path):
    """settings.toml의 부모 디렉터리가 없어도 자동 생성한다."""
    settings = tmp_path / "nested" / "deep" / "settings.toml"
    config = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=settings,
    )
    config.board_theme = BoardTheme(background="blue", indicator="white")
    config.save_board_theme()
    assert settings.exists()
    reloaded = AppConfig.load(path=tmp_path / ".stkrc", settings_path=settings)
    assert reloaded.board_theme.background == "blue"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_config.py -v`

Expected: FAIL — `BorderConfig` import error (removed from test), `sticker_line` attribute not found

- [ ] **Step 3: Implement Config changes**

`src/sticker0/config.py` 전체를 다음으로 교체:

```python
# src/sticker0/config.py
from __future__ import annotations
import os
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from sticker0.presets import (
    BOARD_PRESETS,
    STICKER_PRESETS,
    BoardThemePreset,
    DEFAULT_BOARD_PRESET,
    DEFAULT_STICKER_PRESET,
    StickerPreset,
)
from sticker0.sticker import DEFAULT_BORDER_LINE

CONFIG_PATH = Path.home() / ".stkrc"
SETTINGS_PATH = Path.home() / ".local" / "share" / "sticker0" / "settings.toml"

_G_THEME_STICKER = STICKER_PRESETS[DEFAULT_STICKER_PRESET]
_G_THEME_BOARD = BOARD_PRESETS[DEFAULT_BOARD_PRESET]


def _replace_toml_section(content: str, section: str, new_block: str) -> str:
    """content에서 [section] 블록을 new_block으로 교체. 없으면 끝에 추가."""
    lines = content.split("\n")
    result: list[str] = []
    in_target = False
    found = False
    for line in lines:
        stripped = line.strip()
        if stripped == f"[{section}]":
            in_target = True
            found = True
            result.extend(new_block.rstrip("\n").split("\n"))
            continue
        if in_target and stripped.startswith("[") and not stripped.startswith(f"[{section}]"):
            in_target = False
        if not in_target:
            result.append(line)
    if not found:
        if result and result[-1] != "":
            result.append("")
        result.extend(new_block.rstrip("\n").split("\n"))
    return "\n".join(result)


@dataclass
class BoardTheme:
    """보드 배경/강조색 + 새 스티커 기본 색·라인. settings.toml [theme]에 저장."""

    background: str = _G_THEME_BOARD.background
    indicator: str = _G_THEME_BOARD.indicator
    sticker_border: str = _G_THEME_STICKER.border
    sticker_text: str = _G_THEME_STICKER.text
    sticker_area: str = _G_THEME_STICKER.area
    sticker_line: str = DEFAULT_BORDER_LINE


@dataclass
class DefaultsConfig:
    width: int = 30
    height: int = 10
    preset: str = "Graphite"


@dataclass
class AppConfig:
    board_theme: BoardTheme = field(default_factory=BoardTheme)
    defaults: DefaultsConfig = field(default_factory=DefaultsConfig)
    sticker_presets: dict[str, StickerPreset] = field(default_factory=dict)
    board_presets: dict[str, BoardThemePreset] = field(default_factory=dict)

    @classmethod
    def load(
        cls,
        path: Path = CONFIG_PATH,
        settings_path: Path = SETTINGS_PATH,
    ) -> AppConfig:
        """설정을 로드한다.

        Args:
            path: ~/.stkrc — 인간만 편집하는 읽기 전용 설정
                  ([defaults], [presets.*] 포함. [theme], [border] 무시)
            settings_path: settings.toml — 프로그램이 읽고 쓰는 상태 파일
                  ([theme] 포함)
        """
        config = cls()
        config._settings_path = settings_path

        # ~/.stkrc 로드 ([theme], [border] 무시)
        if path.exists():
            with open(path, "rb") as f:
                data = tomllib.load(f)
            # Defaults
            if (d := data.get("defaults")) is not None:
                config.defaults.width = d.get("width", 30)
                config.defaults.height = d.get("height", 10)
                config.defaults.preset = d.get("preset", "Graphite")
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

        # settings.toml 로드 ([theme])
        if settings_path.exists():
            with open(settings_path, "rb") as f:
                sdata = tomllib.load(f)
            if (t := sdata.get("theme")) is not None:
                config.board_theme.background = t.get(
                    "background", _G_THEME_BOARD.background
                )
                config.board_theme.indicator = t.get(
                    "indicator", _G_THEME_BOARD.indicator
                )
                config.board_theme.sticker_border = t.get(
                    "border", _G_THEME_STICKER.border
                )
                config.board_theme.sticker_text = t.get("text", _G_THEME_STICKER.text)
                config.board_theme.sticker_area = t.get("area", _G_THEME_STICKER.area)
                config.board_theme.sticker_line = t.get("line", DEFAULT_BORDER_LINE)

        return config

    def save_board_theme(self, path: Path | None = None) -> None:
        """settings.toml의 [theme] 섹션에 보드 배경/indicator와 새 스티커 기본 색·라인을 atomic write."""
        actual_path = path if path is not None else getattr(self, "_settings_path", SETTINGS_PATH)
        actual_path.parent.mkdir(parents=True, exist_ok=True)
        bt = self.board_theme
        theme_block = (
            "[theme]\n"
            f'background = "{bt.background}"\n'
            f'indicator = "{bt.indicator}"\n'
            f'border = "{bt.sticker_border}"\n'
            f'text = "{bt.sticker_text}"\n'
            f'area = "{bt.sticker_area}"\n'
            f'line = "{bt.sticker_line}"\n'
        )
        if actual_path.exists():
            content = _replace_toml_section(
                actual_path.read_text(encoding="utf-8"), "theme", theme_block
            )
        else:
            content = theme_block
        # Atomic write
        fd, tmp_path_str = tempfile.mkstemp(dir=actual_path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path_str, str(actual_path))
        except BaseException:
            try:
                os.unlink(tmp_path_str)
            except OSError:
                pass
            raise
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_config.py -v`

Expected: ALL PASS

- [ ] **Step 5: Run full test suite for regressions**

Run: `uv run pytest -v`

Expected: ALL PASS — `config.border` 참조는 아직 `sticker_widget.py`에만 있고, 해당 코드 경로는 기존 config 테스트에서만 검증되므로 test_app.py는 통과해야 함

> **주의**: `sticker_widget.py`의 `_get_border_config()`가 `self.app.config.border`를 참조하므로 `AttributeError`가 발생할 수 있다. 이 경우 해당 메서드의 `except AttributeError`가 fallback을 제공하므로 앱 테스트는 통과한다.

- [ ] **Step 6: Commit**

```bash
git add src/sticker0/config.py tests/test_config.py
git commit -m "refactor: remove BorderConfig, add sticker_line to BoardTheme"
```

---

### Task 3: StickerWidget — 통일 border 적용

**Files:**
- Modify: `src/sticker0/widgets/sticker_widget.py`

- [ ] **Step 1: Remove `BORDER_STYLE_MAP` and `_get_border_config()`**

`src/sticker0/widgets/sticker_widget.py`에서 다음을 삭제:

```python
# 삭제: 라인 16-21
BORDER_STYLE_MAP: dict[str, str] = {
    "single": "solid",
    "double": "double",
    "heavy": "heavy",
    "simple": "ascii",
}
```

```python
# 삭제: 라인 108-116
    def _get_border_config(self) -> tuple[str, str]:
        """config에서 border top/sides 스타일 조회. (top_textual, sides_textual) 반환."""
        try:
            config = self.app.config
            top = BORDER_STYLE_MAP.get(config.border.top, "double")
            sides = BORDER_STYLE_MAP.get(config.border.sides, "solid")
            return (top, sides)
        except AttributeError:
            return ("double", "solid")
```

- [ ] **Step 2: Update `_apply_sticker_styles()` for unified border**

`_apply_sticker_styles()` 메서드의 border 적용 부분을 교체. 기존:

```python
        # Border style from config
        top_style, sides_style = self._get_border_config()
        self.styles.border = (sides_style, border_color)
        self.styles.border_top = (top_style, border_color)
```

새 코드:

```python
        from sticker0.sticker import BORDER_STYLES, DEFAULT_BORDER_LINE
        line = self.sticker.line if self.sticker.line in BORDER_STYLES else DEFAULT_BORDER_LINE
        self.styles.border = (line, border_color)
```

- [ ] **Step 3: Run tests to verify nothing broke**

Run: `uv run pytest -v`

Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add src/sticker0/widgets/sticker_widget.py
git commit -m "refactor: unified border from sticker.line, remove top/sides split"
```

---

### Task 4: ContextMenu — "Change Border" 버튼 추가

**Files:**
- Modify: `src/sticker0/widgets/context_menu.py`

- [ ] **Step 1: Add "Change Border" button to `compose()`**

`src/sticker0/widgets/context_menu.py`의 `compose()` 메서드에서 `"Change Color"` 버튼 바로 뒤에 추가:

기존:

```python
        yield PrimaryOnlyButton("Change Color", id="menu-preset", menu_indicator=mi, menu_panel_bg=mb)
        yield PrimaryOnlyButton("Delete", id="menu-delete", menu_indicator=mi, menu_panel_bg=mb)
```

새 코드:

```python
        yield PrimaryOnlyButton("Change Color", id="menu-preset", menu_indicator=mi, menu_panel_bg=mb)
        yield PrimaryOnlyButton("Change Border", id="menu-border", menu_indicator=mi, menu_panel_bg=mb)
        yield PrimaryOnlyButton("Delete", id="menu-delete", menu_indicator=mi, menu_panel_bg=mb)
```

- [ ] **Step 2: Add action mapping for "border"**

`on_button_pressed()` 의 `action_map`에 추가:

기존:

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

새 코드:

```python
        action_map = {
            "menu-delete": "delete",
            "menu-preset": "preset",
            "menu-border": "border",
            "menu-minimize": "minimize",
            "menu-restore": "restore",
            "menu-copy": "copy",
            "menu-paste": "paste",
        }
```

- [ ] **Step 3: Run tests to verify nothing broke**

Run: `uv run pytest -v`

Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add src/sticker0/widgets/context_menu.py
git commit -m "feat: add Change Border button to context menu"
```

---

### Task 5: BorderPicker 팝업 위젯 생성

**Files:**
- Create: `src/sticker0/widgets/border_picker.py`
- Modify: `tests/test_app.py`

- [ ] **Step 1: Write failing integration test for BorderPicker**

`tests/test_app.py` 끝에 추가:

```python
@pytest.mark.asyncio
async def test_border_change_via_context_menu(tmp_storage, tmp_config):
    """우클릭 → Change Border → round 선택 → border 변경 확인."""
    from sticker0.widgets.sticker_widget import StickerWidget
    from sticker0.widgets.border_picker import BorderPicker
    s = Sticker(title="Border test", line="solid")
    tmp_storage.save(s)
    app = Sticker0App(storage=tmp_storage, config=tmp_config)
    async with app.run_test(size=(120, 40)) as pilot:
        widget = app.query_one(StickerWidget)
        await pilot.click(widget, button=3, offset=(5, 2))
        await pilot.pause(0.1)
        from sticker0.widgets.context_menu import ContextMenu
        menu = app.query_one(ContextMenu)
        await pilot.click(menu.query_one("#menu-border"))
        await pilot.pause(0.1)
        assert len(app.query(BorderPicker)) == 1
        picker = app.query_one(BorderPicker)
        await pilot.click(picker.query_one("#border-round"))
        await pilot.pause(0.1)
        loaded = tmp_storage.load(s.id)
        assert loaded.line == "round"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_app.py::test_border_change_via_context_menu -v`

Expected: FAIL — `border_picker` module not found

- [ ] **Step 3: Create BorderPicker widget**

`src/sticker0/widgets/border_picker.py` 생성:

```python
# src/sticker0/widgets/border_picker.py
from __future__ import annotations
from rich.style import Style
from rich.text import Text
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Button
from textual.message import Message
from sticker0.sticker import BORDER_STYLES
from sticker0.widgets.menu_button import PrimaryOnlyButton
from sticker0.widgets.popup_geometry import (
    apply_clamp_popup_to_parent,
    apply_popup_board_theme,
)


class BorderPicker(Widget):
    """스티커 border 스타일 선택 팝업."""

    DEFAULT_CSS = """
    BorderPicker {
        position: absolute;
        width: 22;
        height: auto;
        background: transparent;
        layer: menu;
    }
    BorderPicker Button {
        width: 1fr;
        height: auto;
        min-height: 1;
        border: none;
        background: transparent;
    }
    """

    class BorderSelected(Message):
        def __init__(self, sticker_id: str, line: str) -> None:
            super().__init__()
            self.sticker_id = sticker_id
            self.line = line

    def __init__(
        self,
        sticker_id: str,
        x: int,
        y: int,
        indicator: str = "white",
        board_background: str = "transparent",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.sticker_id = sticker_id
        self._x = x
        self._y = y
        self._indicator = indicator
        self._board_background = board_background

    def on_mount(self) -> None:
        self.styles.offset = (self._x, self._y)
        self.styles.border = ("round", self._indicator)
        apply_popup_board_theme(self, self._board_background, self._indicator)
        self.call_after_refresh(self._clamp_to_parent)

    def _clamp_to_parent(self) -> None:
        apply_clamp_popup_to_parent(self)

    def compose(self) -> ComposeResult:
        mi, mb = self._indicator, self._board_background
        for style_name in BORDER_STYLES:
            label = Text(style_name.capitalize(), style=Style(bold=True))
            yield PrimaryOnlyButton(
                label,
                id=f"border-{style_name}",
                menu_indicator=mi,
                menu_panel_bg=mb,
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        style_name = (event.button.id or "").removeprefix("border-")
        if style_name in BORDER_STYLES:
            self.post_message(self.BorderSelected(self.sticker_id, style_name))
        self.remove()
```

- [ ] **Step 4: Run test — 아직 board handler 없으므로 실패 예상**

Run: `uv run pytest tests/test_app.py::test_border_change_via_context_menu -v`

Expected: FAIL — board가 "border" action을 처리하지 않으므로 `BorderPicker`가 mount되지 않음

- [ ] **Step 5: Commit (BorderPicker widget만)**

```bash
git add src/sticker0/widgets/border_picker.py
git commit -m "feat: add BorderPicker popup widget"
```

---

### Task 6: Board — BorderPicker 통합

**Files:**
- Modify: `src/sticker0/widgets/board.py`
- Modify: `tests/test_app.py`

- [ ] **Step 1: Update `close_all_menus()` to include BorderPicker**

`src/sticker0/widgets/board.py`의 `close_all_menus()`:

기존:

```python
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
```

새 코드:

```python
    def close_all_menus(self) -> None:
        """모든 팝업 메뉴/피커 닫기 (상호 배제)."""
        from sticker0.widgets.context_menu import ContextMenu
        from sticker0.widgets.board_menu import BoardMenu
        from sticker0.widgets.preset_picker import PresetPicker
        from sticker0.widgets.theme_picker import ThemePicker
        from sticker0.widgets.border_picker import BorderPicker
        for w in self.query(ContextMenu):
            w.remove()
        for w in self.query(BoardMenu):
            w.remove()
        for w in self.query(PresetPicker):
            w.remove()
        for w in self.query(ThemePicker):
            w.remove()
        for w in self.query(BorderPicker):
            w.remove()
```

- [ ] **Step 2: Update `_pointer_is_on_popup_layer()` to include BorderPicker**

기존:

```python
        from sticker0.widgets.context_menu import ContextMenu
        from sticker0.widgets.board_menu import BoardMenu
        from sticker0.widgets.preset_picker import PresetPicker
        from sticker0.widgets.theme_picker import ThemePicker
        from textual.errors import NoWidget

        popup_types = (ContextMenu, BoardMenu, PresetPicker, ThemePicker)
```

새 코드:

```python
        from sticker0.widgets.context_menu import ContextMenu
        from sticker0.widgets.board_menu import BoardMenu
        from sticker0.widgets.preset_picker import PresetPicker
        from sticker0.widgets.theme_picker import ThemePicker
        from sticker0.widgets.border_picker import BorderPicker
        from textual.errors import NoWidget

        popup_types = (ContextMenu, BoardMenu, PresetPicker, ThemePicker, BorderPicker)
```

- [ ] **Step 3: Update `on_resize()` to include BorderPicker**

기존:

```python
        for popup_cls in (
            ContextMenu,
            BoardMenu,
            PresetPicker,
            ThemePicker,
        ):
```

새 코드:

```python
        from sticker0.widgets.border_picker import BorderPicker

        for popup_cls in (
            ContextMenu,
            BoardMenu,
            PresetPicker,
            ThemePicker,
            BorderPicker,
        ):
```

- [ ] **Step 4: Handle "border" action in `on_context_menu_menu_action()`**

기존 handler의 `elif message.action == "minimize":` 바로 앞에 추가:

```python
        elif message.action == "border":
            from sticker0.widgets.border_picker import BorderPicker
            self.close_all_menus()
            picker = BorderPicker(
                sticker_id=message.sticker_id,
                x=message.x,
                y=message.y,
                indicator=self.indicator,
                board_background=self.board_bg,
            )
            self.mount(picker)
```

- [ ] **Step 5: Add `on_border_picker_border_selected()` handler**

`on_preset_picker_preset_selected()` 바로 뒤에 추가:

```python
    def on_border_picker_border_selected(self, message) -> None:
        for widget in self.query(StickerWidget):
            if widget.sticker.id == message.sticker_id:
                widget.sticker.line = message.line
                widget._apply_sticker_styles()
                widget.refresh()
                self.storage.save(widget.sticker)
                break
        self.config.board_theme.sticker_line = message.line
        self.config.save_board_theme()
```

- [ ] **Step 6: Update `add_new_sticker()` to use `sticker_line`**

기존:

```python
        sticker = Sticker(
            content=content if content is not None else "",
            colors=colors,
            size=StickerSize(
                width=cfg.defaults.width,
                height=cfg.defaults.height,
            ),
        )
```

새 코드:

```python
        sticker = Sticker(
            content=content if content is not None else "",
            colors=colors,
            line=bt.sticker_line,
            size=StickerSize(
                width=cfg.defaults.width,
                height=cfg.defaults.height,
            ),
        )
```

- [ ] **Step 7: Run integration test**

Run: `uv run pytest tests/test_app.py::test_border_change_via_context_menu -v`

Expected: PASS

- [ ] **Step 8: Add new sticker default line test**

`tests/test_app.py` 끝에 추가:

```python
@pytest.mark.asyncio
async def test_new_sticker_uses_theme_default_line(tmp_storage, tmp_config):
    """새 스티커의 line은 config.board_theme.sticker_line과 일치."""
    from sticker0.widgets.board_menu import BoardMenu
    from sticker0.widgets.sticker_widget import StickerWidget

    tmp_config.board_theme.sticker_line = "heavy"
    app = Sticker0App(storage=tmp_storage, config=tmp_config)
    async with app.run_test(size=(120, 40)) as pilot:
        board = app.query_one("StickerBoard")
        await pilot.click(board, button=3, offset=(60, 20))
        await pilot.pause(0.1)
        menu = app.query_one(BoardMenu)
        await pilot.click(menu.query_one("#board-create"))
        await pilot.pause(0.1)
        widget = app.query_one(StickerWidget)
        assert widget.sticker.line == "heavy"
```

- [ ] **Step 9: Run test**

Run: `uv run pytest tests/test_app.py::test_new_sticker_uses_theme_default_line -v`

Expected: PASS

- [ ] **Step 10: Run full test suite**

Run: `uv run pytest -v`

Expected: ALL PASS

- [ ] **Step 11: Commit**

```bash
git add src/sticker0/widgets/board.py tests/test_app.py
git commit -m "feat: integrate BorderPicker into board with full save flow"
```

---

### Task 7: README — `[border]` 섹션 제거

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Remove `[border]` from README config section**

`README.md`에서 Configuration 섹션의 변경:

1. 라인 128의 설명에서 `**border** line styles, and` 제거:

기존:

```
**`~/.stkrc`** is for human-edited options only: custom **sticker** and **board** presets, **border** line styles, and **defaults** (new-sticker size and default preset name). The app does not write this file.
```

새 텍스트:

```
**`~/.stkrc`** is for human-edited options only: custom **sticker** and **board** presets, and **defaults** (new-sticker size and default preset name). The app does not write this file.
```

2. 라인 132의 예시 설명에서 `**`[border]`**` 제거:

기존:

```
Example `~/.stkrc` with several custom presets (add your own `[presets.sticker.Name]` / `[presets.board.Name]` tables); put **`[border]`** and **`[defaults]`** at the bottom:
```

새 텍스트:

```
Example `~/.stkrc` with several custom presets (add your own `[presets.sticker.Name]` / `[presets.board.Name]` tables); put **`[defaults]`** at the bottom:
```

3. TOML 예시에서 `[border]` 블록 삭제 (라인 171-173):

```toml
[border]
top = "heavy"         # single | double | heavy | simple
sides = "heavy"
```

이 3줄 + 앞의 빈 줄을 삭제.

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: remove [border] section from README config"
```

---

### Task 8: CLAUDE.md 문서 갱신

**Files:**
- Modify: `CLAUDE.md`
- Modify: `src/sticker0/CLAUDE.md`
- Modify: `src/sticker0/widgets/CLAUDE.md`

- [ ] **Step 1: Update root `CLAUDE.md`**

파일 맵에 `border_picker.py` 추가:

기존:

```
 preset_picker.py # 스티커 프리셋 선택 팝업
 theme_picker.py # 보드 테마 선택 팝업
```

새 코드:

```
 preset_picker.py # 스티커 프리셋 선택 팝업
 border_picker.py # 스티커 border 스타일 선택 팝업
 theme_picker.py # 보드 테마 선택 팝업
```

주의사항에서 `_classify_border()` 관련 외에 border config 관련 사항 제거:

기존:

```
- `StickerColor`/`BorderType` enum 제거됨 (v0.3.0)
```

새 코드:

```
- `StickerColor`/`BorderType` enum 제거됨 (v0.3.0)
- `BorderConfig`/`BORDER_STYLE_MAP` 제거됨 — border는 스티커별 `line` 필드로 관리
```

- [ ] **Step 2: Update `src/sticker0/CLAUDE.md`**

데이터 모델 섹션의 Sticker dataclass 설명 업데이트:

기존:

```
**Sticker dataclass**: `id`(uuid4), `title`(""), `content`(""), `colors`(StickerColors), `minimized`(False), `position`(StickerPosition x/y), `size`(StickerSize w=30 h=10), `created_at/updated_at`(UTC datetime)
```

새 코드:

```
**Sticker dataclass**: `id`(uuid4), `title`(""), `content`(""), `colors`(StickerColors), `line`(DEFAULT_BORDER_LINE="solid"), `minimized`(False), `position`(StickerPosition x/y), `size`(StickerSize w=30 h=10), `created_at/updated_at`(UTC datetime)

**BORDER_STYLES**: `["solid", "heavy", "round", "double", "ascii", "inner", "outer", "dashed"]` — 사용 가능한 Textual border 타입
```

Config 섹션에서 `BorderConfig` 관련 제거:

기존:

```
**BorderConfig**: top / sides (`BORDER_STYLE_MAP`: single→solid, double→double, heavy→heavy, simple→ascii)
```

이 줄을 삭제.

`BoardTheme` 설명 업데이트:

기존:

```
**BoardTheme** (`settings.toml [theme]`): `background`, `indicator` — 보드 배경·UI 강조색. **추가로** `border` / `text` / `area`는 **새로 만드는 스티커**의 기본 `StickerColors` (스티커 프리셋을 고르면 다음 생성에도 반영되도록 `save_board_theme()`에 동일하게 저장)
```

새 코드:

```
**BoardTheme** (`settings.toml [theme]`): `background`, `indicator` — 보드 배경·UI 강조색. **추가로** `border` / `text` / `area`는 **새로 만드는 스티커**의 기본 `StickerColors`, `sticker_line`은 기본 border 스타일 (스티커 프리셋/border를 고르면 다음 생성에도 반영되도록 `save_board_theme()`에 동일하게 저장)
```

`AppConfig` 필드 목록 업데이트:

기존:

```
**AppConfig**: `board_theme`, `border`, `defaults`, `sticker_presets`, `board_presets`
```

새 코드:

```
**AppConfig**: `board_theme`, `defaults`, `sticker_presets`, `board_presets`
```

settings.toml 예시에 `line` 추가:

기존:

```toml
[theme]
background = "#1e1e22"
indicator = "#d4d4d8"
border = "#d4d4d8"
text = "#d4d4d8"
area = "#2a2a2e"
```

새 코드:

```toml
[theme]
background = "#1e1e22"
indicator = "#d4d4d8"
border = "#d4d4d8"
text = "#d4d4d8"
area = "#2a2a2e"
line = "solid"
```

stkrc 예시에서 `[border]` 블록 삭제:

기존:

```toml
[border]
top = "heavy"
sides = "heavy"

[defaults]
preset = "Graphite"
```

새 코드:

```toml
[defaults]
preset = "Graphite"
```

- [ ] **Step 3: Update `src/sticker0/widgets/CLAUDE.md`**

StickerWidget 섹션:

기존:

```
**`_apply_sticker_styles()`**:
- `colors.area == "transparent"` → `_get_board_background()` 상속
- border: 4면 sides 스타일 후 top 덮어씀
- `BORDER_STYLE_MAP`: `single→solid, double→double, heavy→heavy, simple→ascii`
```

새 코드:

```
**`_apply_sticker_styles()`**:
- `colors.area == "transparent"` → `_get_board_background()` 상속
- border: `sticker.line`으로 4면 통일 적용 (`BORDER_STYLES` 외 값은 `DEFAULT_BORDER_LINE` fallback)
```

ContextMenu action 값 업데이트:

기존:

```
**ContextMenu action 값**: `"copy"`, `"paste"`, `"delete"`, `"preset"`, `"minimize"`, `"restore"`
```

새 코드:

```
**ContextMenu action 값**: `"copy"`, `"paste"`, `"delete"`, `"preset"`, `"border"`, `"minimize"`, `"restore"`
```

팝업 위젯 테이블에 BorderPicker 추가:

기존:

```
| PresetPicker | 스티커 프리셋 선택 | `PresetSelected(sticker_id, colors)` |
| ThemePicker | 보드 테마 선택 | `ThemeSelected(background, indicator)` |
```

새 코드:

```
| PresetPicker | 스티커 프리셋 선택 | `PresetSelected(sticker_id, colors)` |
| BorderPicker | 스티커 border 스타일 선택 | `BorderSelected(sticker_id, line)` |
| ThemePicker | 보드 테마 선택 | `ThemeSelected(background, indicator)` |
```

ContextMenu 설명에 Change Border 추가:

기존:

```
- 일반: Minimize, Copy, Paste, Color, Delete
- 최소화: Expand, Copy, Paste, Color, Delete
```

새 코드:

```
- 일반: Minimize, Copy, Paste, Color, Border, Delete
- 최소화: Expand, Copy, Paste, Color, Border, Delete
```

`BorderPicker 버튼 id` 추가:

기존:

```
**PresetPicker 버튼 id**: `f"preset-{name}"` (예: `#preset-Graphite`)
```

새 코드:

```
**PresetPicker 버튼 id**: `f"preset-{name}"` (예: `#preset-Graphite`)

**BorderPicker 버튼 id**: `f"border-{style}"` (예: `#border-solid`, `#border-heavy`)
```

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md src/sticker0/CLAUDE.md src/sticker0/widgets/CLAUDE.md
git commit -m "docs: update CLAUDE.md files for border customization"
```

---

### Task 9: 최종 검증

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest -v`

Expected: ALL PASS

- [ ] **Step 2: Run app manually for smoke test**

Run: `uv run stk`

스모크 테스트 체크리스트:
1. 스티커 생성
2. 스티커 우클릭 → "Change Border" 버튼 확인
3. Change Border 클릭 → BorderPicker 팝업 표시 (8종 스타일)
4. 스타일 선택 → border 즉시 반영 확인
5. 앱 재실행 → border 유지 확인

- [ ] **Step 3: Final commit (if any cleanup needed)**

```bash
git status
# 필요한 경우 추가 정리 후 커밋
```

---

## Self-Review Checklist

- [x] **Spec coverage**: README [border] 제거, BorderConfig 삭제, Sticker.line 추가, context menu "Change Border", BorderPicker 팝업, settings.toml line 저장, 스티커 JSON line 저장, top/sides 통일 — 모두 커버됨
- [x] **Placeholder scan**: 모든 step에 구체적 코드 또는 명령어 포함, TBD/TODO 없음
- [x] **Type consistency**: `sticker.line`, `message.line`, `bt.sticker_line`, `DEFAULT_BORDER_LINE`, `BORDER_STYLES` — 전체 plan에서 일관
