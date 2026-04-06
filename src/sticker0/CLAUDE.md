## 데이터 모델 (sticker.py)

**Sticker dataclass**: `id`(uuid4), `title`(""), `content`(""), `colors`(StickerColors), `minimized`(False), `position`(StickerPosition x/y), `size`(StickerSize w=30 h=10), `created_at/updated_at`(UTC datetime)

**StickerColors 기본값**: border="white", text="white", area="transparent" (= Snow 프리셋)

**레거시 마이그레이션**: `from_dict()`에서 `"colors"` 키 없으면 → 기본 `StickerColors()` 적용

**touch()**: `updated_at` 갱신 — `storage.save()` 내부에서 자동 호출

## 프리셋 시스템 (presets.py)

**StickerPreset**(frozen): name, border, text, area  
**BoardThemePreset**(frozen): name, background, indicator

| 스티커 프리셋 | border | text | area |
|---|---|---|---|
| Snow (기본) | white | white | transparent |
| Ink | black | black | transparent |
| Sky | white | white | #1565c0 |
| Banana | black | black | #ffeb3b |

| 보드 프리셋 | background | indicator |
|---|---|---|
| Dark Mode (기본) | transparent | white |
| Dark Base | black | white |
| Light Base | white | black |
| White Mode | transparent | black |

`get_sticker_preset(name, custom=None)`: custom 우선, 내장 fallback, 미발견 시 None

## Config 시스템 (config.py)

**AppConfig**: `board_theme`(BoardTheme), `border`(BorderConfig top/sides), `defaults`(DefaultsConfig width/height/preset), `keybindings`(n/d/q), `sticker_presets`/`board_presets`(커스텀 dict)

**~/.stkrc 예시**:
```toml
[theme]
background = "black"   # indicator = "white"
[border]
top = "heavy"          # single|double|heavy|simple
[defaults]
preset = "Snow"
[presets.sticker.Fire]
border = "#ff0000"
text = "#ffffff"
area = "#330000"
```

**BORDER_STYLE_MAP**: `single→solid`, `double→double`, `heavy→heavy`, `simple→ascii`

**save_board_theme()**: `_replace_toml_section()`으로 [theme]만 교체, `tempfile.mkstemp()` + `os.replace()`로 atomic write

## Storage (storage.py)

경로: `~/.local/share/sticker0/{uuid}.json`  
- `load_all()`: *.json glob, 손상 파일 건너뜀, created_at 오름차순 정렬  
- `delete(id)`: 파일 없으면 noop

## App (app.py)

```python
class Sticker0App(App):
    # Screen CSS: layers: base stickers menu
    # self.config = AppConfig.load()
    # 키바인딩: n=새스티커, q=종료
    # d/Delete: StickerWidget.on_key에서 처리
```

config 접근: 어디서든 `self.app.config`
