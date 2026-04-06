# src/sticker0/widgets/popup_geometry.py
"""보드(부모) 영역 안에 팝업 offset을 제한."""
from __future__ import annotations

from textual.widget import Widget
from textual.widgets import Button


def clamp_offset_to_parent(
    x: int,
    y: int,
    widget_w: int,
    widget_h: int,
    parent_w: int,
    parent_h: int,
) -> tuple[int, int]:
    """팝업 전체가 부모 직사각형 안에 들어가도록 (x, y) 보정."""
    x_max = max(0, parent_w - widget_w)
    y_max = max(0, parent_h - widget_h)
    return (max(0, min(x, x_max)), max(0, min(y, y_max)))


def apply_clamp_popup_to_parent(widget: Widget) -> None:
    """레이아웃 후 `outer_size` 기준으로 부모(StickerBoard) 안에 맞춘다."""
    parent = widget.parent
    if parent is None:
        return
    pw, ph = parent.size.width, parent.size.height
    if pw < 1 or ph < 1:
        return
    ow, oh = widget.outer_size.width, widget.outer_size.height
    if ow < 1 or oh < 1:
        return
    ox, oy = int(widget.offset.x), int(widget.offset.y)
    nx, ny = clamp_offset_to_parent(ox, oy, ow, oh, pw, ph)
    if (nx, ny) != (ox, oy):
        widget.styles.offset = (nx, ny)


def apply_popup_board_theme(
    widget: Widget,
    board_background: str,
    indicator: str,
    *,
    style_buttons: bool = True,
) -> None:
    """보드 테마와 맞춤: 패널 배경 = board_background, 라벨·버튼 글자 = indicator.

    ``style_buttons=False``이면 자식 버튼은 건드리지 않는다(프리셋/테마 피커 행별 배경).
    """
    widget.styles.background = board_background
    widget.styles.color = indicator
    if not style_buttons:
        return
    for btn in widget.query(Button):
        btn.styles.color = indicator
        btn.styles.background = "transparent"
