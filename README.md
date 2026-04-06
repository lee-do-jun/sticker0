# sticker0

[![Version](https://img.shields.io/badge/version-0.3.0-yellow.svg)](https://github.com/dojun/sticker0)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

A terminal sticky notes TUI app built with Python + [Textual](https://textual.textualize.io/).

---

## Features

- **Drag & resize** stickers freely on the board
- **Text editing** with built-in TextArea
- **Color presets** — Snow, Ink, Sky, Banana (and custom)
- **Board themes** — Dark Mode, Dark Base, Light Base, White Mode (and custom)
- **Minimize / restore** stickers (double-click header or right-click menu)
- **Screen clamping** — stickers stay on screen
- **Auto-save** — changes persist to `~/.local/share/sticker0/`
- **Config file** — customize defaults via `~/.stkrc`

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

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `n` | New sticker |
| `d` / `Delete` | Delete focused sticker |
| `q` | Quit |

---

## Mouse Controls

| Action | Result |
|--------|--------|
| Drag top border | Move sticker |
| Drag left/right border | Resize width |
| Drag bottom border | Resize height |
| Double-click top border | Minimize / restore |
| Right-click sticker | Context menu |
| Right-click empty area | Board menu |

---

## Configuration (`~/.stkrc`)

```toml
[theme]
background = "transparent"   # Board background color
indicator = "white"          # Menu text/border color

[border]
top = "double"    # single | double | heavy | simple
sides = "single"

[defaults]
width = 30
height = 10
preset = "Snow"

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

---

## Development

```bash
git clone https://github.com/dojun/sticker0
cd sticker0
uv sync --dev
uv run stk       # Run app
uv run pytest    # Run tests
```
