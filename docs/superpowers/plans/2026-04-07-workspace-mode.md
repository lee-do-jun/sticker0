# Workspace Mode (`--workspace`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `stk --workspace` / `stk -w` 플래그로 프로젝트 로컬 `.sticker0/` 디렉토리를 저장소로 사용하는 워크스페이스 모드 추가

**Architecture:** `main.py`에서 `argparse`로 `--workspace` 플래그(선택적 경로 인자)를 파싱하고, workspace 경로가 주어지면 `<root>/.sticker0/`을 `data_dir`과 `settings_path`로 사용. `~/.stkrc`는 항상 적용. `Sticker0App`에 workspace 경로를 전달하여 `StickerStorage`와 `AppConfig`를 올바르게 연결.

**Tech Stack:** Python 3.11+, argparse (stdlib)

---

## File Structure

| 파일 | 변경 | 역할 |
|------|------|------|
| `src/sticker0/main.py` | **수정** | argparse CLI 추가, workspace 경로 결정, App에 전달 |
| `src/sticker0/app.py` | **수정** | `workspace` 파라미터 수신 → storage/config 경로 연결 |
| `tests/test_main.py` | **생성** | CLI 파싱 테스트 |
| `tests/test_app.py` | **수정** | workspace 모드 통합 테스트 추가 |

> `config.py`, `storage.py`는 이미 `settings_path`, `data_dir` 주입을 지원하므로 변경 불필요.

---

### Task 1: CLI 파싱 — `main.py`에 argparse 추가

**Files:**
- Create: `tests/test_main.py`
- Modify: `src/sticker0/main.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_main.py` 생성:

```python
# tests/test_main.py
from sticker0.main import parse_args


def test_no_args_returns_none_workspace():
    args = parse_args([])
    assert args.workspace is None


def test_workspace_flag_without_path_uses_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    args = parse_args(["--workspace"])
    assert args.workspace == tmp_path


def test_workspace_short_flag(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    args = parse_args(["-w"])
    assert args.workspace == tmp_path


def test_workspace_with_explicit_path(tmp_path):
    args = parse_args(["--workspace", str(tmp_path)])
    assert args.workspace == tmp_path


def test_workspace_short_with_explicit_path(tmp_path):
    args = parse_args(["-w", str(tmp_path)])
    assert args.workspace == tmp_path
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `uv run pytest tests/test_main.py -v`
Expected: FAIL — `cannot import name 'parse_args' from 'sticker0.main'`

- [ ] **Step 3: 최소 구현**

`src/sticker0/main.py` 수정:

```python
# src/sticker0/main.py
from __future__ import annotations

import argparse
from pathlib import Path

from sticker0.app import Sticker0App


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="stk",
        description="Terminal sticky notes",
    )
    parser.add_argument(
        "-w",
        "--workspace",
        nargs="?",
        const="__CWD__",
        default=None,
        metavar="PATH",
        help="Use <PATH>/.sticker0/ as local storage (default: current directory)",
    )
    args = parser.parse_args(argv)
    if args.workspace == "__CWD__":
        args.workspace = Path.cwd()
    elif args.workspace is not None:
        args.workspace = Path(args.workspace).resolve()
    return args


def main() -> None:
    args = parse_args()
    if args.workspace is not None:
        data_dir = args.workspace / ".sticker0"
        from sticker0.config import AppConfig, CONFIG_PATH
        from sticker0.storage import StickerStorage

        data_dir.mkdir(parents=True, exist_ok=True)
        config = AppConfig.load(
            path=CONFIG_PATH,
            settings_path=data_dir / "settings.toml",
        )
        storage = StickerStorage(data_dir=data_dir)
        app = Sticker0App(storage=storage, config=config)
    else:
        app = Sticker0App()
    app.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `uv run pytest tests/test_main.py -v`
Expected: 5 passed

- [ ] **Step 5: 커밋**

```bash
git add src/sticker0/main.py tests/test_main.py
git commit -m "feat: add --workspace/-w CLI flag for local .sticker0/ storage"
```

---

### Task 2: workspace 모드 통합 테스트

**Files:**
- Modify: `tests/test_app.py`

- [ ] **Step 1: 실패하는 통합 테스트 작성**

`tests/test_app.py` 하단에 추가:

```python
@pytest.mark.asyncio
async def test_workspace_mode_uses_local_sticker0_dir(tmp_path):
    """workspace 모드에서 .sticker0/ 폴더에 스티커와 설정이 저장된다."""
    from sticker0.config import AppConfig, CONFIG_PATH
    from sticker0.widgets.sticker_widget import StickerWidget
    from sticker0.widgets.board_menu import BoardMenu

    data_dir = tmp_path / ".sticker0"
    data_dir.mkdir()
    config = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=data_dir / "settings.toml",
    )
    storage = StickerStorage(data_dir=data_dir)
    app = Sticker0App(storage=storage, config=config)
    async with app.run_test(size=(120, 40)) as pilot:
        board = app.query_one("StickerBoard")
        await pilot.click(board, button=3, offset=(60, 20))
        await pilot.pause(0.1)
        menu = app.query_one(BoardMenu)
        await pilot.click(menu.query_one("#board-create"))
        await pilot.pause(0.1)
        assert len(app.query(StickerWidget)) == 1

    saved_files = list(data_dir.glob("*.json"))
    assert len(saved_files) == 1


@pytest.mark.asyncio
async def test_workspace_mode_settings_toml_independent(tmp_path):
    """workspace의 settings.toml은 글로벌과 독립적으로 관리된다."""
    from sticker0.config import AppConfig, BoardTheme
    from sticker0.widgets.board_menu import BoardMenu
    from sticker0.widgets.theme_picker import ThemePicker

    data_dir = tmp_path / ".sticker0"
    data_dir.mkdir()
    config = AppConfig.load(
        path=tmp_path / ".stkrc",
        settings_path=data_dir / "settings.toml",
    )
    storage = StickerStorage(data_dir=data_dir)
    app = Sticker0App(storage=storage, config=config)
    async with app.run_test(size=(120, 40)) as pilot:
        board = app.query_one("StickerBoard")
        await pilot.click(board, button=3, offset=(60, 20))
        await pilot.pause(0.1)
        menu = app.query_one(BoardMenu)
        await pilot.click(menu.query_one("#board-theme"))
        await pilot.pause(0.1)
        picker = app.query_one(ThemePicker)
        await pilot.click(picker.query_one("#theme-Ivory"))
        await pilot.pause(0.1)

    settings_file = data_dir / "settings.toml"
    assert settings_file.exists()
    content = settings_file.read_text(encoding="utf-8")
    assert "[theme]" in content
```

- [ ] **Step 2: 테스트 통과 확인**

Run: `uv run pytest tests/test_app.py::test_workspace_mode_uses_local_sticker0_dir tests/test_app.py::test_workspace_mode_settings_toml_independent -v`
Expected: 2 passed

> 이 테스트들은 기존 주입 메커니즘(`StickerStorage(data_dir=...)`, `AppConfig.load(settings_path=...)`)만 사용하므로 Task 1이 완료되었다면 바로 통과해야 합니다.

- [ ] **Step 3: 전체 테스트 회귀 확인**

Run: `uv run pytest -v`
Expected: ALL passed

- [ ] **Step 4: 커밋**

```bash
git add tests/test_app.py
git commit -m "test: add workspace mode integration tests"
```

---

### Task 3: `--help` 출력 확인 테스트

**Files:**
- Modify: `tests/test_main.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_main.py`에 추가:

```python
def test_help_shows_workspace_option(capsys):
    import sys
    try:
        parse_args(["--help"])
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert "--workspace" in captured.out
    assert "-w" in captured.out
```

- [ ] **Step 2: 테스트 통과 확인**

Run: `uv run pytest tests/test_main.py::test_help_shows_workspace_option -v`
Expected: PASS (Task 1의 argparse 구현에 이미 포함)

- [ ] **Step 3: 자동 폴더 생성 테스트 추가**

`tests/test_main.py`에 추가:

```python
def test_workspace_creates_sticker0_dir(tmp_path):
    """workspace 지정 시 .sticker0/ 폴더가 자동 생성되어야 한다."""
    from sticker0.main import main as stk_main
    from unittest.mock import patch

    project_dir = tmp_path / "my_project"
    project_dir.mkdir()
    sticker_dir = project_dir / ".sticker0"
    assert not sticker_dir.exists()

    with patch("sticker0.main.parse_args") as mock_parse:
        mock_parse.return_value = type("Args", (), {"workspace": project_dir})()
        with patch("sticker0.app.Sticker0App.run"):
            stk_main()

    assert sticker_dir.exists()
    assert sticker_dir.is_dir()
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `uv run pytest tests/test_main.py -v`
Expected: ALL passed

- [ ] **Step 5: 전체 테스트 회귀 확인 + 커밋**

```bash
uv run pytest -v
git add tests/test_main.py
git commit -m "test: verify --help output and auto .sticker0/ creation"
```

---

## Self-Review Checklist

1. **Spec coverage**: CLI 파싱(`--workspace`/`-w`) ✅ | 선택적 경로 인자 ✅ | 자동 폴더 생성(`.sticker0/`) ✅ | settings.toml 독립 관리 ✅ | `~/.stkrc` 공통 적용 ✅ | `--help` 표시 ✅ | UI 변경 없음 ✅
2. **Placeholder scan**: 없음
3. **Type consistency**: `parse_args` 시그니처, `args.workspace` (Path | None) — 전 Task에서 일관
