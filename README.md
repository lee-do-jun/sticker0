# sticker0

[![Version](https://img.shields.io/badge/version-0.5.0-yellow.svg)](https://github.com/dojun/sticker0)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

A terminal sticky notes TUI app. Pairs naturally with tmux and terminal-based workflows like Claude Code.

![sticker0 running in the terminal](assets/screenshot-1.png)

---

## Features

- **Mouse-first UX** — create, delete, quit, themes, and clipboard actions from context menus (no global keyboard shortcuts)
- **Drag & resize** stickers on the board (wide handles, bottom-corner diagonal resize)
- **Text editing** with a built-in `TextArea` (cursor/scroll styling matches each sticker)
- **Clipboard** — **Copy** / **Paste** on the sticker menu; **New from clipboard** on the board menu (OS clipboard via `pyperclip`)
- **Sticker color presets** — Clear, Graphite, Mist, Ocean, Amber, Forest, Crimson, Violet, Sky, Banana (plus custom `[presets.sticker.*]` in `~/.stkrc`)
- **Board themes** — Graphite, Ivory, Slate, Dust, Forest, Amber (plus custom `[presets.board.*]` in `~/.stkrc`)
- **Border line styles** — per-sticker **Change Border** in the context menu (solid, heavy, round, double, ascii, inner, outer, dashed); each sticker saves its own style in JSON, and the last choice becomes the default for newly created stickers via `settings.toml`
- **Minimize / restore** — double-click the top border or use the context menu
- **Screen clamping** — stickers stay within the terminal
- **Auto-save** — each sticker stored as JSON under `~/.local/share/sticker0/`
- **Workspace mode** — `stk -w` stores stickers and settings in a local `.sticker0/` directory per project, so each workspace keeps its own notes and theme
- **Config** — `~/.stkrc` for custom presets and **defaults** (new-sticker size and default color preset name); **runtime theme** (board colors, default sticker colors, default border line style) is written to `~/.local/share/sticker0/settings.toml` when you use the in-app menus

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

## What’s new in 0.5.0

- **No global shortcuts** — keyboard shortcuts for app-level actions were removed entirely; interaction stays mouse- and menu-driven.
- **Clipboard workflow** — copy sticker body to the OS clipboard, paste clipboard text into the focused sticker, or create a new sticker prefilled from the clipboard (**New from clipboard** on the board menu).

---

## Usage

```bash
stk                       # global mode (~/.local/share/sticker0/)
stk -w                    # workspace mode (./sticker0/ in current directory)
stk --workspace /path     # workspace mode (specified path)
```

---

Create stickers from the board right-click menu (**Create**), or **New from clipboard** when the OS clipboard has text. On a sticker, use **Copy** / **Paste**, **Change Color** (preset), or **Change Border** (outline style) in the context menu. Delete with **Delete**; quit with **Quit** on the board menu.

### Workspace mode

By default sticker0 stores all data under `~/.local/share/sticker0/`. With the **`--workspace`** (or **`-w`**) flag, sticker0 instead uses a `.sticker0/` directory inside the given project root:

```bash
cd ~/projects/my-app
stk -w                    # creates & uses ./sticker0/
stk -w ~/projects/other   # creates & uses ~/projects/other/.sticker0/
```

Each workspace has its **own stickers and `settings.toml`** (independent theme, border defaults, etc.). `~/.stkrc` is still applied as the shared base config.

---

## Configuration (`~/.stkrc`)

**`~/.stkrc`** is for human-edited options only: custom **sticker** and **board** presets, and **defaults** (new-sticker size and default preset name). The app does not write this file.

**Runtime theme** (not hand-edited in `~/.stkrc`) is stored under **`~/.local/share/sticker0/settings.toml`** in a `[theme]` section:

- **`background` / `indicator`** — current board theme (from **Board theme** on the board menu).
- **`border` / `text` / `area`** — default sticker **colors** for the next new sticker after you pick **Change Color**.
- **`line`** — default **border line style** for the next new sticker after you pick **Change Border** (one of `solid`, `heavy`, `round`, `double`, `ascii`, `inner`, `outer`, `dashed` — Textual border types).

Each sticker’s own color preset and border style are also stored in that sticker’s JSON file (`~/.local/share/sticker0/<id>.json`).

A `[theme]` block in `~/.stkrc`, if present, is **ignored** — keep theme state in `settings.toml` or change it from the in-app menus.

Example `~/.stkrc` with several custom presets (add your own `[presets.sticker.Name]` / `[presets.board.Name]` tables); put **`[defaults]`** at the bottom:

```toml
[presets.sticker.Sakura]
border = "#fce7f3"
text = "#831843"
area = "#500724"

[presets.sticker.Nordic]
border = "#e2e8f0"
text = "#0f172a"
area = "#1e293b"

[presets.sticker.Pistachio]
border = "#d9f99d"
text = "#14532d"
area = "#166534"

[presets.sticker.Twilight]
border = "#c4b5fd"
text = "#eef2ff"
area = "#312e81"

[presets.board.Midnight]
background = "#0c0a09"
indicator = "#a8a29e"

[presets.board.Dawn]
background = "#fff7ed"
indicator = "#c2410c"

[presets.board.Fjord]
background = "#0f172a"
indicator = "#38bdf8"

[presets.board.Solarized]
background = "#002b36"
indicator = "#839496"

[defaults]
width = 30
height = 10
```

---

## Runtime theme (`settings.toml`)

The app manages **`~/.local/share/sticker0/settings.toml`** for you. Example `[theme]` block (values reflect your last choices in the UI):

```toml
[theme]
background = "#1e1e22"
indicator = "#d4d4d8"
border = "#d4d4d8"
text = "#d4d4d8"
area = "#2a2a2e"
line = "solid"
```

`line` applies to the **outline** drawn around each sticker (all four edges use the same style). It does not replace the color preset fields above; those control sticker fill and text colors.
