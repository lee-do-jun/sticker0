from unittest.mock import MagicMock, patch

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
