## 데이터 모델 (sticker.py)

**Sticker dataclass**: `id`(uuid4), `title`(""), `content`(""), `colors`(StickerColors), `minimized`(False), `position`(StickerPosition x/y), `size`(StickerSize w=30 h=10), `created_at/updated_at`(UTC datetime)

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

**BoardTheme** (`[theme]`): `background`, `indicator` — 보드 배경·UI 강조색. **추가로** `border` / `text` / `area`는 **새로 만드는 스티커**의 기본 `StickerColors` (스티커 프리셋을 고르면 다음 생성에도 반영되도록 `save_board_theme()`에 동일하게 저장)

**BorderConfig**: top / sides (`BORDER_STYLE_MAP`: single→solid, double→double, heavy→heavy, simple→ascii)

**DefaultsConfig**: width, height, **preset** (새 스티커에 쓸 기본 스티커 프리셋 이름; 기본 `"Graphite"`)

**AppConfig**: `board_theme`, `border`, `defaults`, `keybindings`, `sticker_presets`, `board_presets` (TOML `[presets.sticker.*]` / `[presets.board.*]`에서 로드)

**~/.stkrc 예시**:
```toml
[theme]
background = "#1e1e22"
indicator = "#d4d4d8"
border = "#d4d4d8"
text = "#d4d4d8"
area = "#2a2a2e"

[border]
top = "heavy"
sides = "heavy"

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

**save_board_theme()**: `_replace_toml_section()`으로 `[theme]`만 교체, `tempfile.mkstemp()` + `os.replace()`로 atomic write

## Storage (storage.py)

경로: `~/.local/share/sticker0/{uuid}.json`  
- `load_all()`: *.json glob, 손상 파일 건너뜀, created_at 오름차순 정렬  
- `delete(id)`: 파일 없으면 noop

## App (app.py)

```python
class Sticker0App(App):
    # Screen CSS: layers: base stickers menu
    # self.config = AppConfig.load()
    # 키바인딩: n=새 스티커, q=종료
    # d/Delete: StickerWidget.on_key에서 처리
```

config 접근: 어디서든 `self.app.config`
