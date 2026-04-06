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
