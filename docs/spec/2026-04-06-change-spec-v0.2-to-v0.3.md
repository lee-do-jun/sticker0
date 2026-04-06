# sticker0 Update 2 — Change Spec

> v0.2.0 → v0.3.0

## Overview

이 업데이트는 색상 시스템을 프리셋 기반으로 전면 교체하고, 보드 테마 기능 구현, 스티커 최소화, 테두리 커스터마이징, 화면 제약을 추가한다. 기존 컨텍스트 메뉴 텍스트 미표시 버그도 근본적으로 수정한다.

---

## 변경 사항 목록

### 1. (버그) 컨텍스트 메뉴 텍스트 미표시 — 근본 수정

**현상:**

- 스티커 우클릭 팝업(ContextMenu)과 보드 우클릭 팝업(BoardMenu) 모두에서 버튼 텍스트가 보이지 않음.
- v0.2.0에서 `color: $text` CSS를 추가했으나 여전히 미해결.

**수정 방향:**

- `$text` 토큰이 현재 테마에서 해석되지 않을 수 있음. 하드코딩된 색상(예: `#ffffff` / `#000000`)으로 대체하거나, 보드 테마의 indicator 색상을 직접 참조.
- ContextMenu와 BoardMenu 모두 보드 테마의 `indicator` 색상을 텍스트/테두리에 적용.
- 실제 실행하여 텍스트가 보이는지 반드시 확인.

---

### 2. 스티커 색상 프리셋 시스템

**이전:** `StickerColor` 열거형 (YELLOW, BLUE 등) 단일 색상.

**새 시스템:** 스티커당 3가지 색상을 개별 저장.

| 색상 속성 | 용도                                        |
| --------- | ------------------------------------------- |
| `border`  | 테두리 색상                                 |
| `text`    | 텍스트 색상 + 스크롤바 막대 색상            |
| `area`    | 메모 영역 전체 배경 + 스크롤바 빈 영역 색상 |

**`area`가 Transparent일 때:** 보드 테마의 `background` 색상을 상속받음. 보드가 투명이면 스티커도 투명.

**내장 프리셋:**

| 프리셋 이름 | border | text  | area        |
| ----------- | ------ | ----- | ----------- |
| Snow        | White  | White | Transparent |
| Ink         | Black  | Black | Transparent |
| Sky         | White  | White | Blue        |
| Banana      | Black  | Black | Yellow      |

**기본값:** Snow (새 스티커 생성 시)

**데이터 모델 변경:**

기존 `Sticker.color: StickerColor` 필드를 제거하고, 3개 색상 필드로 교체:

```python
@dataclass
class StickerColors:
    border: str = "white"    # CSS 색상값 또는 "transparent"
    text: str = "white"
    area: str = "transparent"

@dataclass
class Sticker:
    ...
    colors: StickerColors = field(default_factory=StickerColors)
    # color: StickerColor 제거
```

**프리셋은 편의 기능:** 우클릭 메뉴에서 프리셋을 선택하면 3개 색상이 한번에 설정됨. 저장은 항상 개별 색상값.

**기존 JSON 호환성:** `from_dict`에서 기존 `"color": "yellow"` 형식을 새 형식으로 마이그레이션 처리.

**커스텀 프리셋 (.stkrc):**

```toml
[presets.sticker.MyCustom]
border = "#ff6600"
text = "#ffffff"
area = "#333333"
```

---

### 3. 보드 테마 시스템

**보드 테마:** 2가지 색상으로 구성.

| 색상 속성    | 용도                                                     |
| ------------ | -------------------------------------------------------- |
| `background` | 보드 배경색. Transparent 스티커의 area에 영향.           |
| `indicator`  | 팝업 메뉴(ContextMenu/BoardMenu)의 테두리 + 텍스트 색상. |

**내장 프리셋:**

| 프리셋 이름 | background  | indicator |
| ----------- | ----------- | --------- |
| Dark Base   | Black       | White     |
| Light Base  | White       | Black     |
| Dark Mode   | Transparent | White     |
| White Mode  | Transparent | Black     |

**기본값:** Dark Mode

**Transparent background:** 터미널 자체 배경색을 사용 (Textual `background: transparent`).

**보드 우클릭 메뉴에서 테마 변경:**

- `🎨 색상 테마 변경` 버튼 클릭 시 테마 선택 팝업 표시.
- 내장 프리셋 + .stkrc 커스텀 프리셋 목록.
- 선택 시 즉시 적용 + ~/.stkrc에 atomic write로 저장.

**~/.stkrc 저장 형식:**

```toml
[theme]
background = "transparent"
indicator = "white"
```

**커스텀 보드 테마 (.stkrc):**

```toml
[presets.board.Solarized]
background = "#002b36"
indicator = "#839496"
```

**atomic write:** 임시 파일에 쓴 후 `os.replace()`로 교체. 쓰기 중 충돌/손상 방지.

---

### 4. 컨텍스트 메뉴 상호 배제

**동작:** 스티커 우클릭 메뉴(ContextMenu)와 보드 우클릭 메뉴(BoardMenu)는 동시에 존재할 수 없음.

- 한쪽 메뉴가 표시되면 다른 쪽 메뉴 자동 제거.
- 기존 코드에서 부분적으로 구현되어 있으나, 양방향 모두 확인 필요.

---

### 5. 스티커 최소화

**트리거:**

- 우클릭 메뉴 → "최소화" 항목
- 상단 테두리 더블클릭

**최소화 상태:**

- 높이가 3줄로 축소
- 텍스트는 첫 줄만 표시, 가로 초과 시 elipsis 처리
- 이때 상단 테두리 드래그 이동만 가능
- 크기 조절 불가 (좌/우/하단 테두리 드래그 무시)
- 텍스트 편집 불가 (내부 클릭 무시)

**복원:**

- 상단 테두리 더블클릭
- 우클릭 메뉴 → "복원" 항목 (최소화 상태에서만 표시)

**데이터 모델:**

```python
@dataclass
class Sticker:
    ...
    minimized: bool = False
```

**최소화 시 원래 크기 보존:**

- `minimized` 플래그만 토글. `size` 필드는 변경하지 않음.
- 최소화 시 `styles.height = 3`으로 표시.
- 복원 시 `styles.height = sticker.size.height`로 원복.

---

### 6. .stkrc 테두리 스타일 커스터마이징

**설정 형식:**

```toml
[border]
top = "double"
sides = "single"
```

| 필드    | 적용 대상                       | 기본값     |
| ------- | ------------------------------- | ---------- |
| `top`   | 상단 테두리 (양 끝 모서리 포함) | `"double"` |
| `sides` | 좌/우/하단 테두리               | `"single"` |

**사용 가능한 스타일:**

| 스타일   | Textual 매핑 | 설명             |
| -------- | ------------ | ---------------- |
| `single` | `"solid"`    | 기본 단선        |
| `double` | `"double"`   | 이중선           |
| `heavy`  | `"heavy"`    | 두꺼운 단선      |
| `simple` | `"ascii"`    | ASCII (+, -, \|) |

**기존 `border_type` 필드 교체:**

`BorderConfig.border_type: BorderType` → `BorderConfig.top: str`, `BorderConfig.sides: str`

**`BorderType` 열거형 제거.** 문자열로 직접 관리.

---

### 7. 스크롤바 여백

**조건:** TextArea에 스크롤바가 표시될 때, 본문과 스크롤바 사이에 1칸 여백.

**구현:** TextArea의 CSS `padding-right: 1` 적용 (스크롤바 존재 시).

---

### 8. 스티커 중앙점 화면 제약

**제약 조건:**

- 스티커의 중앙점(`position.x + size.width / 2`, `position.y + size.height / 2`)이 화면 우변/하변을 넘을 수 없음.
- 좌측/상단은 기존 `max(0, ...)` 로직으로 이미 제한됨.

**적용 시점:**

1. 드래그 이동 중 (`_apply_drag`)
2. 터미널 크기 변경 시 (Textual `on_resize` 이벤트)

**구현:**

```python
def _clamp_position(self) -> None:
    """스티커 중앙점이 화면 밖으로 나가지 않도록 위치 보정."""
    screen_w = self.screen.size.width
    screen_h = self.screen.size.height
    center_x = self.sticker.position.x + self.sticker.size.width // 2
    center_y = self.sticker.position.y + self.sticker.size.height // 2
    if center_x > screen_w:
        self.sticker.position.x = screen_w - self.sticker.size.width // 2
    if center_y > screen_h:
        self.sticker.position.y = screen_h - self.sticker.size.height // 2
    # 좌/상단은 기존 max(0, ...) 유지
    self.sticker.position.x = max(0, self.sticker.position.x)
    self.sticker.position.y = max(0, self.sticker.position.y)
    self.styles.offset = (self.sticker.position.x, self.sticker.position.y)
```

---

## 파일별 변경 목록

| 파일                                     | 변경 유형     | 내용                                                                                                            |
| ---------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------- |
| `src/sticker0/sticker.py`                | **대폭 수정** | `StickerColor`/`BorderType` enum 제거, `StickerColors` dataclass 추가, `minimized` 필드 추가, JSON 마이그레이션 |
| `src/sticker0/presets.py`                | **신규**      | 내장 스티커/보드 프리셋 정의, .stkrc 커스텀 프리셋 로드                                                         |
| `src/sticker0/config.py`                 | **수정**      | `ThemeConfig` → 보드 테마 (background/indicator), `BorderConfig` → top/sides, 프리셋 로드, atomic write         |
| `src/sticker0/widgets/sticker_widget.py` | **수정**      | 새 색상 시스템 적용, 최소화/복원, 더블클릭 감지, 중앙점 제약, 스크롤바 여백                                     |
| `src/sticker0/widgets/context_menu.py`   | **수정**      | 텍스트 색상 버그 수정, "최소화"/"복원" 항목 추가, 보드 테마 indicator 색상 적용                                 |
| `src/sticker0/widgets/board_menu.py`     | **수정**      | 텍스트 색상 버그 수정, 테마 변경 기능 구현, 보드 테마 indicator 색상 적용                                       |
| `src/sticker0/widgets/board.py`          | **수정**      | 보드 테마 적용, on_resize 핸들러 (중앙점 보정), 메뉴 상호 배제 강화                                             |
| `src/sticker0/widgets/color_picker.py`   | **대폭 수정** | 기존 단일 색상 → 프리셋 선택기로 변경                                                                           |
| `src/sticker0/widgets/theme_picker.py`   | **신규**      | 보드 테마 선택 팝업 위젯                                                                                        |
| `tests/test_app.py`                      | **수정**      | 새 동작에 맞게 테스트 업데이트                                                                                  |
| `tests/test_sticker.py`                  | **수정**      | 새 데이터 모델 테스트                                                                                           |
| `tests/test_config.py`                   | **수정**      | 새 설정 형식 테스트                                                                                             |

---

## 제거되는 기능

- `StickerColor` 열거형 (YELLOW, BLUE, GREEN, PINK, WHITE, DARK, NONE)
- `BorderType` 열거형 (ROUNDED, SHARP, DOUBLE, THICK, ASCII)
- `ColorPicker`의 단일 색상 선택 방식
- `color_picker.py`의 `COLOR_LABELS` 딕셔너리

---

## 유지되는 기능

- JSON 파일 영속화 (`~/.local/share/sticker0/`)
- `~/.stkrc` TOML 설정
- 스티커 드래그 이동/리사이즈 (테두리 역할 분리)
- 우클릭 컨텍스트 메뉴
- `n` 키 새 스티커 생성; 삭제·앱 종료는 각 우클릭 메뉴 (키보드 `q`/`d`/Delete로 종료·삭제 없음)
- z-index (클릭 시 최상단 이동)
- 빈 영역 우클릭 → BoardMenu

---

## Clarification Summary

### Before (Original)

"`docs/ask/2026-04-06-stakeholder-notes-v0.3.md` — 컨텍스트 메뉴 버그, 스티커 프리셋, 보드 테마, 최소화, 테두리 설정, 스크롤바, 화면 제약"

### After (Clarified)

**Goal**: v0.2.0의 버그를 수정하고 색상 프리셋 시스템, 최소화, 화면 제약 기능을 추가하여 v0.3.0으로 업그레이드

**Decisions Made**:

| 질문             | 결정                                                         |
| ---------------- | ------------------------------------------------------------ |
| 프리셋 저장 방식 | 3개 색상값(border/text/area) 개별 저장. 프리셋은 편의 단축키 |
| 최소화 복원 방법 | 더블클릭 + 우클릭 둘 다                                      |
| 보드 테마 저장   | ~/.stkrc에 atomic write                                      |
| 커스텀 프리셋    | .stkrc에서 추가 가능                                         |
| 화면 제약 범위   | 우/하단만, 드래그 중 + resize 이벤트 모두                    |
| 테두리 설정 형식 | [border] top/sides 2개 필드                                  |
| Transparent 동작 | 보드 배경색 상속. 보드가 투명이면 터미널 배경                |
