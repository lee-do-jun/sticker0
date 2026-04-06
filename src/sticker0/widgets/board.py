# src/sticker0/widgets/board.py
from __future__ import annotations
from textual.containers import Container
from textual.widget import Widget
from textual.app import ComposeResult
from textual.events import MouseDown, MouseEvent, MouseUp, Resize
from sticker0.config import AppConfig
from sticker0.sticker import Sticker, StickerColors, StickerSize
from sticker0.storage import StickerStorage
from sticker0.widgets.sticker_widget import StickerWidget


class StickerBoard(Container):
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
        bt = cfg.board_theme
        colors = StickerColors(
            border=bt.sticker_border,
            text=bt.sticker_text,
            area=bt.sticker_area,
        )
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

    def _pointer_is_on_popup_layer(self, event: MouseEvent) -> bool:
        """포인터가 메뉴/피커(또는 그 자식) 위에 있는지. screen 좌표로 히트 테스트."""
        from sticker0.widgets.context_menu import ContextMenu
        from sticker0.widgets.board_menu import BoardMenu
        from sticker0.widgets.preset_picker import PresetPicker
        from sticker0.widgets.theme_picker import ThemePicker
        from textual.errors import NoWidget

        popup_types = (ContextMenu, BoardMenu, PresetPicker, ThemePicker)
        w: Widget | None
        try:
            w, _ = self.screen.get_widget_at(event.screen_x, event.screen_y)
        except NoWidget:
            w = event.widget
        while w is not None:
            if isinstance(w, popup_types):
                return True
            w = w.parent
        return False

    def _pointer_is_on_sticker_widget(self, event: MouseEvent) -> bool:
        """포인터가 StickerWidget(또는 그 자식) 위인지."""
        from textual.errors import NoWidget

        try:
            w, _ = self.screen.get_widget_at(event.screen_x, event.screen_y)
        except NoWidget:
            return False
        while w is not None:
            if isinstance(w, StickerWidget):
                return True
            w = w.parent
        return False

    def on_mouse_down(self, event: MouseDown) -> None:
        """빈 보드 클릭 시 TextArea 포커스 해제 → 앱 단축키(n)가 동작하도록."""
        if event.button != 1:
            return
        if self._pointer_is_on_popup_layer(event):
            return
        if self._pointer_is_on_sticker_widget(event):
            return
        self.app.set_focus(None)

    def on_mouse_up(self, event: MouseUp) -> None:
        if event.button == 1:
            if not self._pointer_is_on_popup_layer(event):
                self.close_all_menus()
            return
        if event.button == 3:
            if self._pointer_is_on_popup_layer(event):
                event.stop()
                return
            self.close_all_menus()
            from sticker0.widgets.board_menu import BoardMenu
            menu = BoardMenu(
                x=event.x,
                y=event.y,
                indicator=self.indicator,
                board_background=self.board_bg,
            )
            self.mount(menu)

    def on_resize(self, event: Resize) -> None:
        """터미널 크기 변경 시 모든 스티커·팝업 위치 보정."""
        from sticker0.widgets.board_menu import BoardMenu
        from sticker0.widgets.context_menu import ContextMenu
        from sticker0.widgets.preset_picker import PresetPicker
        from sticker0.widgets.popup_geometry import apply_clamp_popup_to_parent
        from sticker0.widgets.theme_picker import ThemePicker

        for widget in self.query(StickerWidget):
            widget._clamp_position()
        for popup_cls in (
            ContextMenu,
            BoardMenu,
            PresetPicker,
            ThemePicker,
        ):
            for w in self.query(popup_cls):
                apply_clamp_popup_to_parent(w)

    def on_context_menu_menu_action(self, message) -> None:
        if message.action == "delete":
            self.delete_sticker(message.sticker_id)
        elif message.action == "preset":
            from sticker0.widgets.preset_picker import PresetPicker
            self.close_all_menus()
            picker = PresetPicker(
                sticker_id=message.sticker_id,
                x=message.x,
                y=message.y,
                indicator=self.indicator,
                board_background=self.board_bg,
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
                board_background=self.board_bg,
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
        bt = self.config.board_theme
        bt.sticker_border = message.colors.border
        bt.sticker_text = message.colors.text
        bt.sticker_area = message.colors.area
        self.config.save_board_theme()

    def on_theme_picker_theme_selected(self, message) -> None:
        self.board_bg = message.background
        self.indicator = message.indicator
        self._apply_board_theme()
        # 모든 스티커 스타일 재적용 (transparent 상속 반영)
        for widget in self.query(StickerWidget):
            widget._apply_sticker_styles()
            widget.refresh()
        # config 업데이트 + 저장 (스티커 기본 색은 유지)
        self.config.board_theme.background = message.background
        self.config.board_theme.indicator = message.indicator
        self.config.save_board_theme()
