# sticker0 Update 1 — Change Spec

> v0.1.0 → v0.2.0

## Overview

이 업데이트는 UX를 근본적으로 개선한다. 헤더/푸터를 제거하고 전체화면 보드로 전환하며, 스티커 편집 방식을 단일 클릭 즉시 편집으로 단순화한다. 또한 버그를 수정하고 z-index 동작을 추가한다.

---

## 변경 사항 목록

### 1. z-index — 클릭 시 최상단 이동

**동작:**

- 스티커를 클릭(마우스 다운)하면 해당 스티커가 다른 스티커 위에 표시됨
- Textual에서는 `Widget.move_to_front()`를 호출하거나, StickerBoard에서 해당 위젯을 DOM 순서상 마지막으로 재마운트

**조건:**

- 드래그 시작, 클릭 시작 모두 최상단 이동 트리거
- 한 번에 하나의 스티커만 최상단

---

### 2. 헤더/푸터 제거 + 빈 영역 우클릭 메뉴

**제거:**

- `Header(show_clock=True)` 완전 제거
- `Footer()` 완전 제거
- `stk` 단축키 표시 없음. 키바인딩은 내부적으로 유지하되 UI에 표시하지 않음

**StickerBoard 빈 영역 우클릭 메뉴 추가:**

- 스티커 위젯이 없는 보드 영역에서 우클릭 시 팝업 메뉴 표시
- 기존 스티커 위의 우클릭은 기존 ContextMenu 유지

**빈 영역 메뉴 항목:**

| 항목              | ID              | 동작                                           |
| ----------------- | --------------- | ---------------------------------------------- |
| ✨ Create         | `#board-create` | 클릭한 위치 근처에 새 스티커 생성              |
| 🎨 색상 테마 변경 | `#board-theme`  | 앱 전체 테마 변경 (미래 확장, 현재는 reserved) |
| ✖ Quit            | `#board-quit`   | 앱 종료                                        |

**새 파일:** `src/sticker0/widgets/board_menu.py` — `BoardMenu(Widget)`

---

### 3. (버그 수정) 스티커 우클릭 메뉴 텍스트 미표시

**현상:** 스티커 우클릭 시 ContextMenu 팝업이 나타나지만 버튼 텍스트가 보이지 않음.

**원인 추정:** 스티커 배경색이 버튼 텍스트와 동일하거나, `layer: menu`가 스티커 색상을 상속하는 문제.

**수정:**

- `ContextMenu`의 CSS에 명시적 텍스트 색상 지정 (`color: $text`)
- `background: $surface` 명시
- 버튼 텍스트 색상 강제 지정으로 배경색 영향 차단

---

### 4. 단일 클릭 즉시 편집

**이전 동작:** 더블클릭 → 편집 모드 (DOUBLE_CLICK_INTERVAL 기반)

**새 동작:**

| 상태                                    | 클릭 동작                                                |
| --------------------------------------- | -------------------------------------------------------- |
| 비포커스 (다른 스티커/빈 영역에 포커스) | 해당 스티커 포커스 획득 + TextArea 마지막 커서 위치 유지 |
| 포커스 (이미 이 스티커가 활성)          | 클릭한 위치로 커서 이동 (테두리 아닌 경우에만)           |

**구현 방식:**

- 스티커 내부는 항상 `TextArea`로 렌더링 (비편집 상태에서도)
- 비포커스 상태: `TextArea`는 읽기 전용처럼 동작하지만 클릭 시 즉시 포커스+편집 가능
- 별도의 Static ↔ TextArea 교체 없음. 항상 TextArea 사용
- `on_click` / `on_focus` / `on_blur`로 시각적 상태 변화 처리

**제거:**

- `DOUBLE_CLICK_INTERVAL`, `on_click`의 더블클릭 감지 로직
- `_enter_edit_mode()`, `_exit_edit_mode()` (혹은 단순화)
- `_editing` 플래그

**Esc 키:**

- Esc → TextArea 포커스 해제. 내용은 자동 저장됨 (on_blur에서 저장)

---

### 5. 배경색 투명 (기본값)

**변경:**

- 스티커 기본 배경색 = 터미널 기본 배경 (투명)
- `StickerColor.TRANSPARENT` 또는 `None` 값 추가 (기존 "yellow" 기본값 교체)
- `~/.stkrc`의 `default_color`는 색상 지정 시 적용, 미설정 시 투명

**색상 기능 유지:**

- 우클릭 → 색상 변경 메뉴 유지
- 색상 6가지 + "투명 (기본)" 옵션 추가

**CSS 변경:**

```css
StickerWidget {
  background: transparent; /* 기본값 */
}
```

---

### 6. UI 리디자인 — 테두리 역할 분리

**이전:** 우하단 2x2 영역 = 리사이즈, 나머지 = 드래그 이동

**새 UI 구조:**

```
╭==================╮   ← 상단 border 라인 = 드래그 이동 핸들
│ (내용, 편집 가능)│   ← 내부 전체 = 클릭 즉시 편집
│ (내용, 편집 가능)│
│ (내용, 편집 가능)│
╰──────────────────╯
↑                  ↑
│                  └── 우측 border = 드래그 리사이즈 (가로 크기)
└── 좌측 border = 드래그 리사이즈 (가로 크기)
     하단 border = 드래그 리사이즈 (세로 크기)
```

**드래그 영역 분류:**

| 마우스 위치                                  | 동작                          |
| -------------------------------------------- | ----------------------------- |
| 상단 border 라인 (`y == 0`, border 영역)     | 드래그 이동                   |
| 좌측 border (`x == 0`)                       | 드래그 리사이즈 (width 변경)  |
| 우측 border (`x == width - 1`)               | 드래그 리사이즈 (width 변경)  |
| 하단 border (`y == height - 1`)              | 드래그 리사이즈 (height 변경) |
| 내부 (`1 ≤ x ≤ width-2`, `1 ≤ y ≤ height-2`) | 클릭 즉시 편집                |

**Textual에서 border 영역 클릭 감지:**

- `event.x`, `event.y`는 위젯 내부 좌표 (padding 포함)
- border 영역 감지: `event.x == 0`, `event.x == self.size.width - 1` 등
- 단, Textual의 border는 widget 좌표계 밖일 수 있음 → 실제 테스트 필요

**제목 영역 제거:**

- `Static(classes="sticker-title")` 완전 제거
- 스티커 전체 내용 = 하나의 `TextArea`

**Border 스타일:**

- 상단: `╭═══════╮` (double horizontal = 드래그 핸들 시각적 표시)
- 하단/좌/우: `╰───────╯` (single)
- Textual border 커스터마이징 or 직접 렌더링

---

## 파일별 변경 목록

| 파일                                     | 변경 유형     | 내용                                                                     |
| ---------------------------------------- | ------------- | ------------------------------------------------------------------------ |
| `src/sticker0/app.py`                    | **수정**      | Header/Footer 제거                                                       |
| `src/sticker0/widgets/board.py`          | **수정**      | 빈 영역 우클릭 → BoardMenu 표시                                          |
| `src/sticker0/widgets/board_menu.py`     | **신규**      | BoardMenu 위젯 (Create/테마/Quit)                                        |
| `src/sticker0/widgets/sticker_widget.py` | **대폭 수정** | TextArea 항상 표시, 단일 클릭 편집, border 역할 분리, z-index, 투명 배경 |
| `src/sticker0/widgets/context_menu.py`   | **수정**      | 텍스트 미표시 버그 수정 (색상 명시)                                      |
| `src/sticker0/sticker.py`                | **수정**      | `StickerColor`에 투명(`TRANSPARENT`/`none`) 추가                         |
| `src/sticker0/widgets/color_picker.py`   | **수정**      | 투명 옵션 추가                                                           |
| `tests/test_app.py`                      | **수정**      | 새 동작에 맞게 테스트 업데이트                                           |

---

## 제거되는 기능

- `Header`, `Footer` 위젯
- 더블클릭 편집 로직 (`DOUBLE_CLICK_INTERVAL`, `_editing` 플래그)
- `Static ↔ TextArea` 교체 방식
- 우하단 모서리 리사이즈 (→ 테두리 전체로 대체)
- 스티커 `title` 필드 표시 (데이터 유지, UI에서만 미표시)

---

## 유지되는 기능

- JSON 파일 영속화
- `~/.stkrc` 설정 (색상, 테두리, 기본 크기, 키바인딩)
- 우클릭 컨텍스트 메뉴 (스티커 위에서)
- 색상 변경 (6가지 + 투명)
- `n` 키 새 스티커 생성 (Header 없어도 키바인딩 내부 유지)
- `d`/Delete 키 삭제

---

## Clarification Summary

### Before (Original)

"`docs/ask/2026-04-06-stakeholder-notes-v0.2.md` — 스티커 z-index, 상/하단바 제거, 빈 영역 우클릭 메뉴, 단일 클릭 편집, 투명 배경, 테두리 역할 분리"

### After (Clarified)

**Goal**: v0.1.0의 UX를 단순화하여 더 직관적인 터미널 스티커 앱으로 개선

**Decisions Made**:

| 질문                     | 결정                                           |
| ------------------------ | ---------------------------------------------- |
| 편집 모드 진입           | 단일 클릭 즉시 편집 (더블클릭 제거)            |
| 배경색                   | 터미널 기본 배경 (투명), 색상 기능 자체는 유지 |
| 드래그 핸들 범위         | 상단 테두리 border 1줄만                       |
| 빈 영역 우클릭 메뉴 항목 | Create, 색상 테마 변경, Quit                   |
