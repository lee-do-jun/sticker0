# sticker0 CLAUDE.md

터미널 스티키 노트 TUI 앱 (Python + Textual >= 0.80). `stk` CLI로 실행, v0.4.0.
스티커를 자유롭게 드래그·리사이즈·최소화하며 TOML config + JSON 파일로 영속화.

## 아키텍처

```
Sticker0App (App)
  └── StickerBoard (Widget) — 캔버스, CRUD 조율
        ├── StickerWidget * N    layer: stickers
        ├── ContextMenu          layer: menu
        ├── BoardMenu            layer: menu
        ├── PresetPicker         layer: menu
        └── ThemePicker          layer: menu
```

Screen layers: `base stickers menu` / Board layers: `stickers menu`

## 파일 맵

```
src/sticker0/
  __init__.py       # __version__ = "0.4.0"
  main.py           # CLI 진입점 (stk)
  app.py            # Sticker0App: 키바인딩, config 보유
  sticker.py        # Sticker dataclass, StickerColors, StickerPosition, StickerSize
  presets.py        # 내장 프리셋 (Snow/Ink/Sky/Banana, Dark Base 등)
  config.py         # AppConfig: ~/.stkrc TOML 파싱, atomic write
  storage.py        # StickerStorage: ~/.local/share/sticker0/*.json
  widgets/
    sticker_widget.py  # StickerWidget: 드래그/리사이즈/최소화
    board.py           # StickerBoard: 스티커 캔버스, 메시지 조율
    context_menu.py    # 스티커 우클릭 팝업
    board_menu.py      # 보드 우클릭 팝업
    preset_picker.py   # 스티커 프리셋 선택 팝업
    theme_picker.py    # 보드 테마 선택 팝업
tests/
  test_sticker.py   test_presets.py   test_config.py
  test_storage.py   test_app.py
```

## 데이터 흐름

- **생성**: `board.add_new_sticker()` → `Sticker` 객체 → `storage.save()` → `StickerWidget` mount
- **저장**: 드래그/TextArea 변경/최소화 → `board.save_sticker()` → `{uuid}.json`
- **로드**: `board.compose()` → `storage.load_all()` → `Sticker.from_dict()`

## 핵심 패턴

- `self.app.config`로 어디서든 `AppConfig` 접근
- 모든 팝업은 `on_mount()`에서 indicator 색상 동적 설정
- `board.close_all_menus()`로 메뉴 상호 배제
- `StickerWidget._clamp_position()`으로 화면 제약

## 개발 명령어

```bash
uv run stk          # 앱 실행
uv run pytest -v    # 전체 테스트 (56 tests)
```

## 주의사항 (함정)

- `Widget.move_to_front()` 없음 → `parent.move_child(self, after=children[-1])`
- `_classify_border()`는 `self.outer_size` 사용 (`self.size` 아님)
- TextArea에 `background: transparent` 직접 설정 금지
- 빈 문자열 `""` 색상 금지
- `StickerColor`/`BorderType` enum 제거됨 (v0.3.0)
- `color_picker.py` 삭제됨 → `preset_picker.py`
- ThemePicker 버튼 id: 공백→하이픈 (`"Dark Base"` → `#theme-Dark-Base`)
