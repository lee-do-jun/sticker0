# sticker0 — Specification

## Overview

`sticker0`는 터미널 전용 스티커 메모 앱입니다. 데스크톱 스티커(포스트잇)의 기본 기능을 커서 단위 Terminal UI로 구현합니다. 주로 tmux 환경에서 별도 pane/window에 실행하여 사용합니다.

## Installation

```bash
uv tool install sticker0
```

실행:

```bash
stk
```

## Architecture

- **언어**: Python
- **패키지 매니저**: uv
- **실행 구조**: 단일 TUI 앱 — `stk` 명령어 실행 시 전용 터미널 창(tmux pane 등)에서 TUI가 열림
- **프로세스 모델**: 독립 터미널 프로세스 (daemon 없음)

## Features

### 스티커 기본 기능

- 스티커 생성, 편집, 삭제
- 여러 스티커를 동시에 TUI 화면에 floating 위젯으로 표시
- 각 스티커는 제목(선택)과 본문 텍스트로 구성

### 콘텐츠

- Plain text 메모
- ANSI 색상 및 스타일 지원 (bold, color 등)

### 마우스 인터랙션

| 동작 | 기능 |
|------|------|
| 드래그 | 스티커 위치 이동 |
| 모서리/가장자리 드래그 | 스티커 크기 조절 (리사이즈) |
| 우클릭 | 컨텍스트 메뉴 (편집, 삭제, 색상 변경 등) |
| 더블클릭 | 인라인 편집 모드 진입 |

### 키보드

앱 레벨 단축키는 두지 않는다. 새 스티커는 **보드 빈 영역 우클릭 → Create**, 스티커 삭제는 **스티커 우클릭 → Delete**, 앱 종료는 **보드 빈 영역 우클릭 → Quit**. 텍스트 편집은 `TextArea` 포커스 시 일반 입력·편집 키를 사용한다.

## Data Storage

- 저장 위치: `~/.local/share/sticker0/`
- 형식: **스티커당 JSON 파일 1개**
- 파일명: `{uuid}.json`

### JSON 스키마

```json
{
  "id": "uuid-v4",
  "title": "스티커 제목 (선택)",
  "content": "메모 내용",
  "color": "yellow",
  "border": "rounded",
  "position": { "x": 10, "y": 5 },
  "size": { "width": 30, "height": 10 },
  "created_at": "2026-04-06T00:00:00Z",
  "updated_at": "2026-04-06T00:00:00Z"
}
```

## Configuration: `~/.stkrc`

TOML 형식의 사용자 설정 파일.

```toml
[theme]
# 스티커 기본 색상 테마
default_color = "yellow"   # yellow | blue | green | pink | white | dark

[border]
# 스티커 테두리 스타일
type = "rounded"           # rounded | sharp | double | thick | ascii

[defaults]
# 새 스티커 기본 크기
width = 30
height = 10
```

## TUI Layout

```
┌─────────────────────────────────────────────────────┐
│  sticker0   (Create / Quit: 보드 우클릭 메뉴)        │
├─────────────────────────────────────────────────────┤
│                                                     │
│   ╭──────────────────╮   ╭──────────────────╮      │
│   │ 📌 TODO           │   │ 📌 아이디어        │      │
│   │                  │   │                  │      │
│   │ - 미팅 준비       │   │ sticker0 v2에    │      │
│   │ - PR 리뷰         │   │ 태그 기능 추가?   │      │
│   │                  │   │                  │      │
│   ╰──────────────────╯   ╰──────────────────╯      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## tmux 활용 예시

```bash
# tmux에서 새 pane을 열고 sticker0 실행
tmux split-window -h 'stk'

# 또는 새 window에서 실행
tmux new-window -n stickers 'stk'
```

## Project Structure

```
sticker0/
├── pyproject.toml
├── docs/spec/2026-04-06-product-spec.md
├── README.md
└── src/
    └── sticker0/
        ├── __init__.py
        ├── main.py          # 엔트리포인트
        ├── app.py           # TUI 앱 메인 클래스
        ├── sticker.py       # 스티커 모델
        ├── storage.py       # JSON 파일 저장/로드
        ├── config.py        # ~/.stkrc 파싱
        └── widgets/
            ├── __init__.py
            ├── board.py     # 스티커 보드 (메인 화면)
            └── sticker_widget.py  # 개별 스티커 위젯
```

## Tech Stack (Planned)

| 용도 | 라이브러리 |
|------|-----------|
| TUI 프레임워크 | [Textual](https://github.com/Textualize/textual) |
| 설정 파싱 | `tomllib` (Python 3.11+ 표준) |
| 데이터 모델 | `dataclasses` 또는 `pydantic` |
| UUID 생성 | `uuid` (표준) |
