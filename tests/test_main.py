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
