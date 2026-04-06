# src/sticker0/widgets/preset_picker.py
from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Button
from textual.message import Message
from sticker0.sticker import StickerColors
from sticker0.widgets.menu_button import PrimaryOnlyButton
from sticker0.widgets.popup_geometry import (
    apply_clamp_popup_to_parent,
    apply_popup_board_theme,
)
from sticker0.presets import StickerPreset, STICKER_PRESETS
from sticker0.widgets.picker_labels import (
    resolve_sticker_picker_idle,
    sticker_preset_picker_label,
)


class PresetPicker(Widget):
    """스티커 프리셋 선택 팝업."""

    DEFAULT_CSS = """
    PresetPicker {
        position: absolute;
        width: 22;
        height: auto;
        background: transparent;
        layer: menu;
    }
    PresetPicker Button {
        width: 1fr;
        height: auto;
        min-height: 1;
        border: none;
        background: transparent;
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
        board_background: str = "transparent",
        custom_presets: dict[str, StickerPreset] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.sticker_id = sticker_id
        self._x = x
        self._y = y
        self._indicator = indicator
        self._board_background = board_background
        self._all_presets: dict[str, StickerPreset] = dict(STICKER_PRESETS)
        if custom_presets:
            self._all_presets.update(custom_presets)

    def on_mount(self) -> None:
        self.styles.offset = (self._x, self._y)
        self.styles.border = ("round", self._indicator)
        apply_popup_board_theme(
            self,
            self._board_background,
            self._indicator,
            style_buttons=False,
        )
        self.call_after_refresh(self._clamp_to_parent)

    def _clamp_to_parent(self) -> None:
        apply_clamp_popup_to_parent(self)

    def compose(self) -> ComposeResult:
        for name, preset in self._all_presets.items():
            idle_bg, idle_fg = resolve_sticker_picker_idle(
                preset, self._board_background, self._indicator
            )
            yield PrimaryOnlyButton(
                sticker_preset_picker_label(preset),
                id=f"preset-{name}",
                menu_indicator=self._indicator,
                menu_panel_bg=self._board_background,
                menu_idle_bg=idle_bg,
                menu_idle_color=idle_fg,
            )

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
