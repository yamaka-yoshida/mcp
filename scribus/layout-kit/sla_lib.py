# -*- coding: utf-8 -*-
"""Scribus .sla 座標キャリブレーション共通ライブラリ。"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

PT_PER_MM = 72.0 / 25.4
A4_W_PT = 595.275590551181
A4_H_PT = 841.889763779528
CANVAS_X = "100.001"
CANVAS_Y = "20.001"
HEADLESS_OFFSET_PT = (100.0, 20.0)

PAGE_OBJECT_RE = re.compile(r"<PageObject (?P<attrs>[^>]+)/?>", re.MULTILINE)
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')


def mm_to_pt(v: float) -> float:
    return v * PT_PER_MM


def pt_to_mm(v: float) -> float:
    return v / PT_PER_MM


def load_calibration(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save_calibration(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_sla_path(cal: dict[str, Any], cal_path: Path) -> Path:
    scribus = cal.get("scribus", {})
    rel = scribus.get("sla_path")
    if rel:
        root = cal_path.parent
        for base in (root, *root.parents):
            candidate = base / rel
            if candidate.exists():
                return candidate
        return root / Path(rel).name
    explicit = scribus.get("sla_file")
    if explicit:
        p = Path(explicit)
        return p if p.is_absolute() else cal_path.parent / p
    stem = cal.get("template") or cal_path.stem.replace(".calibration", "")
    return cal_path.with_name(f"{stem}.sla")


def parse_attrs(raw: str) -> dict[str, str]:
    return dict(ATTR_RE.findall(raw))


def fval(attrs: dict[str, str], key: str, default: float = 0.0) -> float:
    return float(attrs.get(key, default))


def bbox_from_attrs(attrs: dict[str, str]) -> tuple[float, float, float, float]:
    x = fval(attrs, "XPosition")
    y = fval(attrs, "YPosition")
    w = max(fval(attrs, "Width"), 0.0)
    h = max(fval(attrs, "Height"), 0.0)
    if w == 0 and h == 0:
        return x, y, x, y
    return x, y, x + w, y + h


def merge_bbox(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    return min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])


def iter_page_object_bboxes(text: str) -> tuple[float, float, float, float] | None:
    bbox = None
    for mobj in PAGE_OBJECT_RE.finditer(text):
        bb = bbox_from_attrs(parse_attrs(mobj.group("attrs")))
        bbox = bb if bbox is None else merge_bbox(bbox, bb)
    return bbox


def shift_page_objects(text: str, dx_pt: float, dy_pt: float = 0.0) -> str:
    def shift_block(block: str) -> str:
        for attr in ("XPosition", "gXpos"):
            block = re.sub(
                rf'({attr}=")([0-9.]+)(")',
                lambda m, a=attr: f'{m.group(1)}{float(m.group(2)) + dx_pt}{m.group(3)}',
                block,
            )
        for attr in ("YPosition", "gYpos"):
            block = re.sub(
                rf'({attr}=")([0-9.]+)(")',
                lambda m, a=attr: f'{m.group(1)}{float(m.group(2)) + dy_pt}{m.group(3)}',
                block,
            )
        return block

    parts = text.split("<PageObject ")
    if len(parts) < 2:
        return text
    head, *chunks = parts
    return head + "".join(shift_block("<PageObject " + c) for c in chunks)


def scale_attrs(attrs: dict[str, str], s: float, ax: float, ay: float) -> dict[str, str]:
    out = dict(attrs)
    for key in ("XPosition", "gXpos"):
        if key in out:
            v = float(out[key])
            out[key] = str(v + (v - ax) * (s - 1))
    for key in ("YPosition", "gYpos"):
        if key in out:
            v = float(out[key])
            out[key] = str(v + (v - ay) * (s - 1))
    for key in ("Width", "Height", "LineWidth"):
        if key in out:
            v = float(out[key])
            if v > 0:
                out[key] = str(v * s)
    return out


def attrs_to_string(attrs: dict[str, str]) -> str:
    return " ".join(f'{k}="{v}"' for k, v in attrs.items())


def target_margin_rect_pt(cal: dict[str, Any]) -> tuple[float, float, float, float]:
    paper_w, paper_h = cal["paper"]["size_mm"]
    m = cal["margins_mm"]
    return (
        mm_to_pt(m["left"]),
        mm_to_pt(m["top"]),
        mm_to_pt(paper_w - m["right"]),
        mm_to_pt(paper_h - m["bottom"]),
    )


def compute_fit_scale(
    content: tuple[float, float, float, float],
    target: tuple[float, float, float, float],
    percent: float,
) -> float:
    cx0, cy0, cx1, cy1 = content
    tx0, ty0, tx1, ty1 = target
    cw = max(cx1 - cx0, 1e-6)
    ch = max(cy1 - cy0, 1e-6)
    tw = max(tx1 - tx0, 1e-6)
    th = max(ty1 - ty0, 1e-6)
    return min(tw / cw, th / ch) * (percent / 100.0)


def fit_sla_text(text: str, cal: dict[str, Any], percent: float) -> tuple[str, dict[str, Any]]:
    target = target_margin_rect_pt(cal)
    bbox = iter_page_object_bboxes(text)
    if bbox is None:
        raise RuntimeError("no PageObject in sla")
    ax = (bbox[0] + bbox[2]) / 2
    ay = (bbox[1] + bbox[3]) / 2
    scale = compute_fit_scale(bbox, target, percent)

    def repl(match: re.Match[str]) -> str:
        attrs = scale_attrs(parse_attrs(match.group("attrs")), scale, ax, ay)
        return "<PageObject " + attrs_to_string(attrs) + "/>"

    info = {
        "content_bbox_mm": [pt_to_mm(v) for v in bbox],
        "target_bbox_mm": [pt_to_mm(v) for v in target],
        "anchor_center_mm": [pt_to_mm(ax), pt_to_mm(ay)],
        "fit_scale": round(scale, 6),
        "percent": percent,
        "effective_percent": round(scale * 100, 2),
    }
    return PAGE_OBJECT_RE.sub(repl, text), info


def fix_page_size(text: str) -> str:
    text = text.replace("1686.61417322835", str(A4_W_PT))
    text = text.replace("2386.77165354331", str(A4_H_PT))
    text = text.replace('PageWidth="595"', f'PageWidth="{A4_W_PT}"')
    text = text.replace('PageHeight="842"', f'PageHeight="{A4_H_PT}"')
    text = text.replace('PageSize="Custom"', 'PageSize="IsoA_A04"')
    return text


def remove_headless_offset(text: str) -> str:
    if 'XPosition="140.' not in text:
        return text
    ox, oy = HEADLESS_OFFSET_PT
    for attr in ("XPosition", "gXpos"):
        text = re.sub(
            rf'{attr}="([0-9.]+)"',
            lambda m, a=attr: f'{a}="{float(m.group(1)) - ox}"',
            text,
        )
    for attr in ("YPosition", "gYpos"):
        text = re.sub(
            rf'{attr}="([0-9.]+)"',
            lambda m, a=attr: f'{a}="{float(m.group(1)) - oy}"',
            text,
        )
    return text


def calibrate_canvas_and_guides(text: str, cal: dict[str, Any]) -> str:
    m = cal["margins_mm"]
    calib = cal.get("calibration", {})
    origin = calib.get("origin_page_mm", {})
    left_mm = origin.get("x", m["left"])
    top_mm = origin.get("y", m["top"])
    paper_w, paper_h = cal["paper"]["size_mm"]
    right_mm = paper_w - m["right"]
    bottom_mm = paper_h - m["bottom"]
    v_guides = f"{mm_to_pt(left_mm)} {mm_to_pt(right_mm)}"
    h_guides = f"{mm_to_pt(top_mm)} {mm_to_pt(bottom_mm)}"

    for tag in ("MasterPage", "Page"):
        text = re.sub(
            rf'(<{tag} [^>]*?)PageXPosition="[^"]*"',
            rf'\1PageXPosition="{CANVAS_X}"',
            text,
            count=1,
        )
        text = re.sub(
            rf'(<{tag} [^>]*?)PageYPosition="[^"]*"',
            rf'\1PageYPosition="{CANVAS_Y}"',
            text,
            count=1,
        )
        text = re.sub(
            rf'(<{tag} [^>]*?)VerticalGuides="[^"]*"',
            rf'\1VerticalGuides="{v_guides}"',
            text,
            count=1,
        )
        text = re.sub(
            rf'(<{tag} [^>]*?)HorizontalGuides="[^"]*"',
            rf'\1HorizontalGuides="{h_guides}"',
            text,
            count=1,
        )
    return text
