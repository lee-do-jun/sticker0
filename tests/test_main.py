# tests/test_main.py
from sticker0.main import parse_args


def test_no_args_returns_none_workspace():
    args = parse_args([])
    assert args.workspace is None


def test_workspace_flag_without_path_uses_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    args = parse_args(["--workspace"])
    assert args.workspace == tmp_path


def test_workspace_short_flag(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    args = parse_args(["-w"])
    assert args.workspace == tmp_path


def test_workspace_with_explicit_path(tmp_path):
    args = parse_args(["--workspace", str(tmp_path)])
    assert args.workspace == tmp_path


def test_workspace_short_with_explicit_path(tmp_path):
    args = parse_args(["-w", str(tmp_path)])
    assert args.workspace == tmp_path


def test_help_shows_workspace_option(capsys):
    try:
        parse_args(["--help"])
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert "--workspace" in captured.out
    assert "-w," in captured.out


def test_workspace_creates_sticker0_dir(tmp_path):
    """workspace 지정 시 .sticker0/ 폴더가 자동 생성되어야 한다."""
    from sticker0.main import main as stk_main
    from unittest.mock import patch

    project_dir = tmp_path / "my_project"
    project_dir.mkdir()
    sticker_dir = project_dir / ".sticker0"
    assert not sticker_dir.exists()

    with patch("sticker0.main.parse_args") as mock_parse:
        mock_parse.return_value = type("Args", (), {"workspace": project_dir})()
        with patch("sticker0.app.Sticker0App.run"):
            stk_main()

    assert sticker_dir.exists()
    assert sticker_dir.is_dir()
