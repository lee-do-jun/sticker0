# sticker0

[![Version](https://img.shields.io/badge/version-0.4.0-yellow.svg)](https://github.com/dojun/sticker0)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

A terminal sticky notes TUI app built with Python + [Textual](https://textual.textualize.io/).

---

## Features

- **Drag & resize** stickers on the board (wide handles, bottom-corner diagonal resize)
- **Text editing** with a built-in `TextArea` (cursor/scroll styling matches each sticker)
- **Sticker color presets** — Graphite, Mist, Ocean, Amber, Forest, Crimson, Violet, Sky, Banana (plus custom `[presets.sticker.*]`)
- **Board themes** — Graphite, Ivory, Slate Blue, Dust Rose, Forest, Amber Night (plus custom `[presets.board.*]`)
- **Minimize / restore** — double-click the top border or use the context menu
- **Screen clamping** — stickers stay within the terminal
- **Auto-save** — each sticker stored as JSON under `~/.local/share/sticker0/`
- **Config** — `~/.stkrc` for board theme, sticker default colors, border style, size defaults, and keybindings

---

## Installation

```bash
# Recommended (uv)
uv tool install sticker0

# pip
pip install sticker0
```

**Requirements:** Python >= 3.11, Textual >= 0.80

---

## Usage

```bash
stk
```

---

## Keyboard shortcuts

| Key            | Action                 |
| -------------- | ---------------------- |
| `n`            | New sticker            |
| `d` / `Delete` | Delete focused sticker |
| `q`            | Quit                   |

---

## Configuration (`~/.stkrc`)

The **`[theme]`** section holds both the **board** look and the **default colors for newly created stickers**:

- `background` / `indicator` — board background and UI accent (menus, borders).
- `border` / `text` / `area` — default `StickerColors` for **new** stickers. These update when you pick a sticker preset from the menu (so the next “Create” matches your last choice). Choosing a **board** theme from the menu updates `background` and `indicator` only and keeps the three sticker colors unless you change them via a sticker preset.

```toml
[theme]
background = "transparent"
indicator = "white"
border = "#d4d4d8"    # new sticker — border color
text = "#d4d4d8"      # new sticker — text color
area = "#2a2a2e"      # new sticker — area color

[border]
top = "heavy"         # single | double | heavy | simple
sides = "heavy"

[defaults]
width = 30
height = 10

[keybindings]
new = "n"
delete = "d"
quit = "q"

# Custom sticker preset
[presets.sticker.Fire]
border = "#ff0000"
text = "#ffffff"
area = "#330000"

# Custom board theme
[presets.board.Solarized]
background = "#002b36"
indicator = "#839496"
```
