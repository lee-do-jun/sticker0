# src/sticker0/main.py
from __future__ import annotations

import argparse
from pathlib import Path

from sticker0.app import Sticker0App


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="stk",
        description="Terminal sticky notes",
    )
    parser.add_argument(
        "-w",
        "--workspace",
        nargs="?",
        const="__CWD__",
        default=None,
        metavar="PATH",
        help="Use <PATH>/.sticker0/ as local storage (default: current directory)",
    )
    args = parser.parse_args(argv)
    if args.workspace == "__CWD__":
        args.workspace = Path.cwd()
    elif args.workspace is not None:
        args.workspace = Path(args.workspace).resolve()
    return args


def main() -> None:
    args = parse_args()
    if args.workspace is not None:
        data_dir = args.workspace / ".sticker0"
        from sticker0.config import AppConfig, CONFIG_PATH
        from sticker0.storage import StickerStorage

        data_dir.mkdir(parents=True, exist_ok=True)
        config = AppConfig.load(
            path=CONFIG_PATH,
            settings_path=data_dir / "settings.toml",
        )
        storage = StickerStorage(data_dir=data_dir)
        app = Sticker0App(storage=storage, config=config)
    else:
        app = Sticker0App()
    app.run()


if __name__ == "__main__":
    main()
