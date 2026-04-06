# sticker0 CLAUDE.md

터미널 스티키 노트 TUI 앱 (Python + Textual >= 0.80). `stk` CLI로 실행, v0.4.0.  
스티커를 자유롭게 드래그·리사이즈·최소화하며 TOML config + JSON 파일로 영속화.

저장소 루트 `README.md`에는 실행 화면 예시로 `assets/screenshot-1.png`가 포함된다.

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
  app.py            # Sticker0App: `n` 새 스티커 바인딩, config 보유 (종료·삭제는 우클릭 메뉴)
  sticker.py        # Sticker dataclass, StickerColors, StickerPosition, StickerSize
  presets.py        # 내장 스티커/보드 프리셋 (Graphite 기본 등)
  config.py         # AppConfig: ~/.stkrc TOML 파싱, atomic write
  storage.py        # StickerStorage: ~/.local/share/sticker0/*.json
  widgets/
    sticker_widget.py  # StickerWidget: 드래그/리사이즈/최소화
    board.py           # StickerBoard: 스티커 캔버스, 메뉴·마우스 조율
    context_menu.py    # 스티커 우클릭 팝업
    board_menu.py      # 보드 우클릭 팝업
    preset_picker.py   # 스티커 프리셋 선택 팝업
    theme_picker.py    # 보드 테마 선택 팝업
    menu_button.py     # PrimaryOnlyButton — 팝업 전용 버튼(좌클릭만 press)
    popup_geometry.py  # 팝업 부모 영역 클램프, 보드 테마 색 적용
tests/
  test_sticker.py   test_presets.py   test_config.py   test_popup_geometry.py
  test_storage.py   test_app.py
assets/
  screenshot-1.png  # README 미리보기용
```

## 데이터 흐름

- **생성**: `board.add_new_sticker()` → `[theme]`의 스티커 기본색 + `defaults` 크기 → `Sticker` → `storage.save()` → `StickerWidget` mount
- **저장**: 드래그/TextArea 변경/최소화 → `board.save_sticker()` → `{uuid}.json`
- **로드**: `board.compose()` → `storage.load_all()` → `Sticker.from_dict()`

## 핵심 패턴

- `self.app.config`로 어디서든 `AppConfig` 접근
- 팝업은 `on_mount()`에서 `apply_popup_board_theme()` + `call_after_refresh(apply_clamp_popup_to_parent)`로 보드와 맞춤·클램프
- 모든 팝업 버튼은 `PrimaryOnlyButton` — 우클릭은 메뉴 닫힘을 유발하지 않도록 좌클릭만 `Pressed` 처리
- `board.close_all_menus()`로 메뉴/피커 상호 배제; 빈 보드 좌클릭(`on_mouse_down`)은 포커스 해제로 앱 단축키(`n`)가 먹히게 함
- 터미널 리사이즈 시 스티커 `_clamp_position()` + 열린 팝업 `apply_clamp_popup_to_parent` 재적용
- `StickerWidget._clamp_position()`으로 화면 제약

## 개발 명령어

```bash
uv run stk          # 앱 실행
uv run pytest -v    # 전체 테스트 (60 tests)
```

## 주의사항 (함정)

- `Widget.move_to_front()` 없음 → `parent.move_child(self, after=children[-1])`
- `_classify_border()`는 `self.outer_size` 사용 (`self.size` 아님)
- TextArea에 `background: transparent` 직접 설정 금지
- 빈 문자열 `""` 색상 금지
- `StickerColor`/`BorderType` enum 제거됨 (v0.3.0)
- `color_picker.py` 삭제됨 → `preset_picker.py`
- ThemePicker 버튼 id: 공백→하이픈 (`"Slate Blue"` → `#theme-Slate-Blue`)

## 상세 레퍼런스

- 도메인·설정·스토리지 심화: `src/sticker0/CLAUDE.md`
- 위젯·입력·팝업 동작: `src/sticker0/widgets/CLAUDE.md`
