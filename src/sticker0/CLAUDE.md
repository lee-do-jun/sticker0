## 데이터 모델 (sticker.py)

**Sticker dataclass**: `id`(uuid4), `title`(""), `content`(""), `colors`(StickerColors), `line`(DEFAULT_BORDER_LINE="solid"), `minimized`(False), `position`(StickerPosition x/y), `size`(StickerSize w=30 h=10), `created_at/updated_at`(UTC datetime)

**BORDER_STYLES**: `["solid", "heavy", "round", "double", "ascii", "inner", "outer", "dashed"]` — 사용 가능한 Textual border 타입

**StickerColors 기본값** (dataclass): border/text="white", area="transparent" — 레거시 JSON에 `colors` 없으면 이 값으로 마이그레이션

**새 스티커 색**: `board.add_new_sticker()`는 `AppConfig.board_theme`의 `sticker_border` / `sticker_text` / `sticker_area`를 사용 (기본은 Graphite 프리셋과 동일 계열)

**touch()**: `updated_at` 갱신 — `storage.save()` 내부에서 자동 호출

## 프리셋 시스템 (presets.py)

**StickerPreset**(frozen): name, border, text, area  
**BoardThemePreset**(frozen): name, background, indicator

**내장 스티커 프리셋**: Graphite, Mist, Ocean, Amber, Forest, Crimson, Violet, Sky, Banana (`DEFAULT_STICKER_PRESET = "Graphite"`)

**내장 보드 프리셋**: Graphite, Ivory, Slate Blue, Dust Rose, Forest, Amber Night (`DEFAULT_BOARD_PRESET = "Graphite"`)

`get_sticker_preset(name, custom=None)` / `get_board_preset(name, custom=None)`: custom 우선, 내장 fallback, 미발견 시 None

## Config 시스템 (config.py)

### 파일 역할 분리

| 파일 | 경로 | 읽기 | 쓰기 |
|------|------|------|------|
| 사용자 설정 | `~/.stkrc` | 프로그램 | **인간만** |
| 프로그램 상태 | `~/.local/share/sticker0/settings.toml` | 프로그램 | **프로그램만** |

- `~/.stkrc`에 `[theme]`이 있어도 **완전히 무시**됨. 프로그램은 이 파일을 절대 쓰지 않음.
- `settings.toml`은 현재 적용된 테마와 마지막 스티커 색을 저장. 없으면 기본값 사용.

**BoardTheme** (`settings.toml [theme]`): `background`, `indicator` — 보드 배경·UI 강조색. **추가로** `border` / `text` / `area`는 **새로 만드는 스티커**의 기본 `StickerColors`, `sticker_line`은 기본 border 스타일 (스티커 프리셋/border를 고르면 다음 생성에도 반영되도록 `save_board_theme()`에 동일하게 저장)

**DefaultsConfig**: width, height, **preset** (새 스티커에 쓸 기본 스티커 프리셋 이름; 기본 `"Graphite"`)

**AppConfig**: `board_theme`, `defaults`, `sticker_presets`, `board_presets`  
- `load(path, settings_path)`: `path`(stkrc)에서 defaults/presets 읽기; `settings_path`(settings.toml)에서 `[theme]` 읽기  
- `_settings_path`: load 시 주입된 settings.toml 경로 — `save_board_theme()`이 이곳을 기본 대상으로 사용

**~/.stkrc 예시** (인간만 편집):
```toml
[defaults]
preset = "Graphite"

[presets.sticker.Fire]
border = "#ff0000"
text = "#ffffff"
area = "#330000"

[presets.board.Solarized]
background = "#002b36"
indicator = "#839496"
```

**settings.toml 예시** (프로그램이 자동 관리):
```toml
[theme]
background = "#1e1e22"
indicator = "#d4d4d8"
border = "#d4d4d8"
text = "#d4d4d8"
area = "#2a2a2e"
line = "solid"
```

**save_board_theme()**: `_replace_toml_section()`으로 `settings.toml`의 `[theme]`만 교체, `tempfile.mkstemp()` + `os.replace()`로 atomic write. 부모 디렉터리 없으면 자동 생성.

## Storage (storage.py)

경로: `~/.local/share/sticker0/{uuid}.json`  
`settings.toml`과 같은 디렉터리지만 `*.json`만 glob하므로 충돌 없음.  
- `load_all()`: *.json glob, 손상 파일 건너뜀, created_at 오름차순 정렬  
- `delete(id)`: 파일 없으면 noop

## App (app.py)

```python
class Sticker0App(App):
    # Screen CSS: layers: base stickers menu
    # self.config = config or AppConfig.load()  # config 주입 가능 (테스트용)
```

config 접근: 어디서든 `self.app.config`
