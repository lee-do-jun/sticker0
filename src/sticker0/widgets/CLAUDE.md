# widgets/ CLAUDE.md

## 공통: 팝업 스타일·기하

**`popup_geometry.apply_popup_board_theme(widget, board_background, indicator)`**  
패널 배경 = 보드 배경, 라벨·버튼 글자색 = indicator (버튼 배경은 transparent 유지).

**`popup_geometry.apply_clamp_popup_to_parent(widget)`**  
`outer_size` 기준으로 부모(StickerBoard) 안에 팝업이 들어가도록 `offset` 보정. `on_mount` 끝에서 `call_after_refresh`로 한 번, `StickerBoard.on_resize`에서 열린 팝업마다 재호출.

**`menu_button.PrimaryOnlyButton`**  
팝업 전용 `Button`: `compact=True` 기본, hover 시 indicator·배경 스왑. **우클릭은 무시**해 메뉴 밖으로 이벤트가 새지 않게 함.

---

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

**우클릭**: `on_mouse_up(button==3)` → `board.close_all_menus()` + ContextMenu mount (`minimized` 전달)

**주의**: `_move_to_front()` = `parent.move_child(self, after=children[-1])`

---

## StickerBoard (board.py)

스티커 캔버스. CRUD, 메뉴 상호 배제, 테마, 클램프·마우스 조율.

**레이어**: `layers: stickers menu` / StickerWidget은 `layer: stickers`

**주요 속성**: `board_bg`, `indicator` (config에서 초기화)

**`close_all_menus()`**: ContextMenu, BoardMenu, PresetPicker, ThemePicker 전부 remove

**마우스**:
- **좌클릭 다운** (`on_mouse_down`, button 1): 포인터가 팝업이나 스티커 위가 아니면 `app.set_focus(None)` — 빈 보드 클릭 시 TextArea 포커스 해제 (종료·삭제는 각 우클릭 메뉴)
- **좌클릭 업**: 팝업 밖이면 `close_all_menus()`
- **우클릭**: 팝업 위면 `event.stop()`; 아니면 메뉴 닫고 `BoardMenu` mount

**`on_resize`**: 모든 `StickerWidget._clamp_position()` + 열린 팝업에 `apply_clamp_popup_to_parent`

**메시지 핸들러**:

| 핸들러 | 동작 |
|--------|------|
| `on_context_menu_menu_action` | copy / paste / delete / preset(피커 마운트) / minimize / restore |
| `on_board_menu_menu_action` | create / theme(피커 마운트) / quit |
| `on_preset_picker_preset_selected` | sticker.colors 교체 + 스타일 재적용 + save |
| `on_theme_picker_theme_selected` | board_bg/indicator 갱신 + 전 스티커 재적용 + save_board_theme() |

`ContextMenu.MenuAction`은 `x,y`를 포함 — 프리셋 피커를 같은 근처에 띄울 때 사용.

---

## 팝업 위젯들

**공통 패턴**: `indicator`, `board_background`를 받음 → `on_mount()`에서 테두리 + `apply_popup_board_theme` + refresh 후 클램프

| 위젯 | 역할 | 발송 메시지 |
|------|------|------------|
| ContextMenu | 스티커 우클릭 | `MenuAction(action, sticker_id, x, y)` |
| BoardMenu | 보드 우클릭 | `MenuAction(action, x, y)` |
| PresetPicker | 스티커 프리셋 선택 | `PresetSelected(sticker_id, colors)` |
| ThemePicker | 보드 테마 선택 | `ThemeSelected(background, indicator)` |

**ContextMenu** (최소화 여부에 따라):
- 일반: Minimize, Copy, Paste, Color, Delete
- 최소화: Expand, Copy, Paste, Color, Delete  
  (`"edit"` 액션 없음 — 텍스트는 스티커 영역 포커스로 편집)

**ContextMenu action 값**: `"copy"`, `"paste"`, `"delete"`, `"preset"`, `"minimize"`, `"restore"`

**클립보드**: `sticker0.system_clipboard` — OS는 `pyperclip`, Textual 버퍼·OSC52는 `write_clipboard_from_app`에서 `app.copy_to_clipboard`로 동기화.

**BoardMenu action 값**: `"create"`, `"theme"`, `"quit"`

**PresetPicker 버튼 id**: `f"preset-{name}"` (예: `#preset-Graphite`)

**ThemePicker 버튼 id**: 공백→하이픈 (`"Slate Blue"` → `#theme-Slate-Blue`)  
- `_id_to_name` dict로 역매핑 유지

---

## 우클릭 테스트

```python
await pilot.click(widget, button=3, offset=(5, 2))
```
