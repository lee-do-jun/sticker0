# src/sticker0/widgets/preset_picker.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Button
from textual.message import Message
from sticker0.sticker import StickerColors
from sticker0.widgets.menu_button import PrimaryOnlyButton
from sticker0.presets import StickerPreset, STICKER_PRESETS


class PresetPicker(Widget):
    """스티커 프리셋 선택 팝업."""

    DEFAULT_CSS = """
    PresetPicker {
        position: absolute;
        width: 22;
        height: auto;
        background: $surface;
        color: $text;
        layer: menu;
    }
    PresetPicker Button {
        width: 1fr;
        height: auto;
        min-height: 1;
        border: none;
        background: transparent;
        color: $text;
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

    def compose(self) -> ComposeResult:
        for name in self._all_presets:
            yield PrimaryOnlyButton(name, id=f"preset-{name}")

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
