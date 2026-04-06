# sticker0

[![Version](https://img.shields.io/badge/version-0.4.0-yellow.svg)](https://github.com/dojun/sticker0)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

A terminal sticky notes TUI app built with Python + [Textual](https://textual.textualize.io/).

![sticker0 running in the terminal](assets/screenshot-1.png)

---

## Features

- **Drag & resize** stickers on the board (wide handles, bottom-corner diagonal resize)
- **Text editing** with a built-in `TextArea` (cursor/scroll styling matches each sticker)
- **Sticker color presets** — Graphite, Mist, Ocean, Amber, Forest, Crimson, Violet, Sky, Banana (plus custom `[presets.sticker.*]`)
- **Board themes** — Graphite, Ivory, Slate Blue, Dust Rose, Forest, Amber Night (plus custom `[presets.board.*]`)
- **Minimize / restore** — double-click the top border or use the context menu
- **Screen clamping** — stickers stay within the terminal
- **Auto-save** — each sticker stored as JSON under `~/.local/share/sticker0/`
- **Config** — `~/.stkrc` for board theme, sticker default colors, border style, size defaults, and optional `[keybindings]` (`new` only)

---

## 🚀 Installation

### ⚡ Modern installation with uv (recommended)

[uv](https://docs.astral.sh/uv/) is the fastest and easiest way to install and use sticker0.

**Why uv is a good choice:**

- ✅ Creates isolated environments automatically (fewer system conflicts)
- ✅ Avoids many Python version / “externally-managed-environment” issues
- ✅ Simple updates and uninstallation (`uv tool upgrade`, `uv tool uninstall`)
- ✅ Works on Linux, macOS, and Windows

**Requirements:** Python >= 3.11 (managed by uv as needed), Textual >= 0.80 (pulled in as a dependency).

---

### Install from PyPI

```bash
# Install directly from PyPI with uv (easiest)
uv tool install sticker0

# Run from anywhere
stk
```

**Alternative — pip:**

```bash
pip install sticker0
stk
```

---

### Install from source

```bash
git clone https://github.com/dojun/sticker0.git
cd sticker0
uv tool install .

# Run from anywhere
stk
```

For local development without installing a global tool:

```bash
uv sync --dev
uv run stk
```

---

### First-time uv users

If you don’t have uv installed yet, install it with one command:

**Linux / macOS:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, **restart your terminal** (or open a new one) so `uv` is on your `PATH`.

For more options (Homebrew, WinGet, PyPI, etc.), see the official uv installation guide:  
[Installation — Standalone installer & other methods](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)

---

## Usage

```bash
stk
```

---

## Keyboard shortcuts

| Key   | Action      |
| ----- | ----------- |
| `n`   | New sticker |

Delete stickers from the sticker context menu (**Delete**). Quit from the board right-click menu (**Quit**).

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
