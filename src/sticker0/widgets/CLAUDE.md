# widgets/ CLAUDE.md

## StickerWidget (sticker_widget.py)

개별 스티커. 드래그 이동/리사이즈, 최소화, 텍스트 편집, 우클릭 메뉴.

**드래그 모드** (`_classify_border(x,y)` — `outer_size` 기준):
- `y==0` → `_DRAG_MOVE` (이동)
- `x==0` → `_DRAG_RESIZE_LEFT` (너비+위치 동시)
- `x==w-1` → `_DRAG_RESIZE_RIGHT` (너비)
- `y==h-1` → `_DRAG_RESIZE_H` (높이)
- 내부 클릭 → None / 최소화 상태 → y==0만 허용

**`_apply_sticker_styles()`**:
- `colors.area == "transparent"` → `_get_board_background()` 상속
- border: 4면 sides 스타일 후 top 덮어씀
- `BORDER_STYLE_MAP`: `single→solid, double→double, heavy→heavy, simple→ascii`

**최소화 (`_set_minimized`)**:
- `True`: height=3, TextArea hide, `#minimized-label` Static mount (첫 줄 + ellipsis)
- `False`: height=sticker.size.height, TextArea show, `#minimized-label` remove
- mount 전 기존 `#minimized-label` remove로 중복 방지

**더블클릭**: 상단 테두리 0.4초 이내 2회 → `_toggle_minimize()`

**`_clamp_position()`**: 중앙점 기준 screen 우/하단 초과 방지, 좌/상단 `max(0,...)`

**자동 저장**: `on_text_area_changed` → 매 변경마다 `board.save_sticker()`

**우클릭**: `on_mouse_up(button==3)` → `board.close_all_menus()` + ContextMenu mount

**키**: `d`/`delete` → 삭제, `enter` → `_get_editor().focus()`

**주의**: `_move_to_front()` = `parent.move_child(self, after=children[-1])`

---

## StickerBoard (board.py)

스티커 캔버스. CRUD, 메뉴 상호 배제, 테마, 클램프 조율.

**레이어**: `layers: stickers menu` / StickerWidget은 `layer: stickers`

**주요 속성**: `board_bg`, `indicator` (config에서 초기화)

**`close_all_menus()`**: ContextMenu, BoardMenu, PresetPicker, ThemePicker 전부 remove

**메시지 핸들러**:

| 핸들러 | 동작 |
|--------|------|
| `on_context_menu_menu_action` | edit/delete/preset/minimize/restore 분기 |
| `on_board_menu_menu_action` | create/theme/quit 분기 |
| `on_preset_picker_preset_selected` | sticker.colors 교체 + 스타일 재적용 + save |
| `on_theme_picker_theme_selected` | board_bg/indicator 갱신 + 전 스티커 재적용 + save_board_theme() |
| `on_mouse_up (button==3)` | close_all_menus + BoardMenu mount |
| `on_resize` | 전 StickerWidget._clamp_position() |

---

## 팝업 위젯들

**공통 패턴**: 생성자에서 `indicator` 받음 → `on_mount()`에서 `styles.border/color` 동적 설정

| 위젯 | 역할 | 발송 메시지 |
|------|------|------------|
| ContextMenu | 스티커 우클릭 | `MenuAction(action, sticker_id)` |
| BoardMenu | 보드 우클릭 | `MenuAction(action, x, y)` |
| PresetPicker | 스티커 프리셋 선택 | `PresetSelected(sticker_id, colors)` |
| ThemePicker | 보드 테마 선택 | `ThemeSelected(background, indicator)` |

**ContextMenu action 값**: `"edit"`, `"delete"`, `"preset"`, `"minimize"`, `"restore"`
- minimized=True: "복원" 버튼만 표시 (편집/최소화 숨김)

**BoardMenu action 값**: `"create"`, `"theme"`, `"quit"`

**PresetPicker 버튼 id**: `f"preset-{name}"` (예: `#preset-Snow`)

**ThemePicker 버튼 id**: 공백→하이픈 (`"Dark Base"` → `#theme-Dark-Base`)
- `_id_to_name` dict로 역매핑 유지

---

## 우클릭 테스트

```python
await pilot.click(widget, button=3, offset=(5, 2))
```
