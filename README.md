# sticker0

[![Version](https://img.shields.io/badge/version-0.5.0-yellow.svg)](https://github.com/dojun/sticker0)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

A terminal sticky notes TUI app built with Python + [Textual](https://textual.textualize.io/).

![sticker0 running in the terminal](assets/screenshot-1.png)

---

## Features

- **Mouse-first UX** — create, delete, quit, themes, and clipboard actions from context menus (no global keyboard shortcuts)
- **Drag & resize** stickers on the board (wide handles, bottom-corner diagonal resize)
- **Text editing** with a built-in `TextArea` (cursor/scroll styling matches each sticker)
- **Clipboard** — **Copy** / **Paste** on the sticker menu; **New from clipboard** on the board menu (OS clipboard via `pyperclip`)
- **Sticker color presets** — Clear, Graphite, Mist, Ocean, Amber, Forest, Crimson, Violet, Sky, Banana (plus custom `[presets.sticker.*]` in `~/.stkrc`)
- **Board themes** — Graphite, Ivory, Slate, Dust, Forest, Amber (plus custom `[presets.board.*]` in `~/.stkrc`)
- **Minimize / restore** — double-click the top border or use the context menu
- **Screen clamping** — stickers stay within the terminal
- **Auto-save** — each sticker stored as JSON under `~/.local/share/sticker0/`
- **Config** — `~/.stkrc` for border style, size defaults, and custom presets; active board/sticker colors live in `~/.local/share/sticker0/settings.toml` (updated when you pick themes from the menus)

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
stk
```

---

Create stickers from the board right-click menu (**Create**), or **New from clipboard** when the OS clipboard has text. On a sticker, use **Copy** / **Paste** in the context menu. Delete with **Delete**; quit with **Quit** on the board menu.

---

## Configuration (`~/.stkrc`)

**`~/.stkrc`** is for human-edited options only: custom **sticker** and **board** presets, **border** line styles, and **defaults** (new-sticker size and default preset name). The app does not write this file.

**Runtime colors** (current board background/accent and colors used for newly created stickers after you pick presets in the UI) are stored under **`~/.local/share/sticker0/settings.toml`** in a `[theme]` section. A `[theme]` block in `~/.stkrc`, if present, is **ignored** — keep theme state in `settings.toml` or change it from the in-app theme menus.

Example `~/.stkrc` with several custom presets (add your own `[presets.sticker.Name]` / `[presets.board.Name]` tables); put **`[border]`** and **`[defaults]`** at the bottom:

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

[border]
top = "heavy"         # single | double | heavy | simple
sides = "heavy"

[defaults]
width = 30
height = 10
```
