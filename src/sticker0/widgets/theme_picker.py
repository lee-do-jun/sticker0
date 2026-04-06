# src/sticker0/widgets/theme_picker.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Button
from textual.message import Message
from sticker0.presets import BoardThemePreset, BOARD_PRESETS
from sticker0.widgets.menu_button import PrimaryOnlyButton
from sticker0.widgets.popup_geometry import apply_clamp_popup_to_parent


class ThemePicker(Widget):
    """보드 테마 선택 팝업."""

    DEFAULT_CSS = """
    ThemePicker {
        position: absolute;
        width: 22;
        height: auto;
        background: $surface;
        color: $text;
        layer: menu;
    }
    ThemePicker Button {
        width: 1fr;
        height: auto;
        min-height: 1;
        border: none;
        background: transparent;
        color: $text;
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
        self.call_after_refresh(self._clamp_to_parent)

    def _clamp_to_parent(self) -> None:
        apply_clamp_popup_to_parent(self)

    def compose(self) -> ComposeResult:
        self._id_to_name: dict[str, str] = {}
        for name in self._all_presets:
            safe_id = f"theme-{name.replace(' ', '-')}"
            self._id_to_name[safe_id] = name
            yield PrimaryOnlyButton(name, id=safe_id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        btn_id = event.button.id or ""
        name = self._id_to_name.get(btn_id, "")
        preset = self._all_presets.get(name)
        if preset:
            self.post_message(
                self.ThemeSelected(preset.background, preset.indicator)
            )
        self.remove()
