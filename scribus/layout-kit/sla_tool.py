# -*- coding: utf-8 -*-
"""Scribus .sla キャリブレーション CLI（プロジェクト共通）。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sla_lib import (
    PT_PER_MM,
    calibrate_canvas_and_guides,
    fit_sla_text,
    fix_page_size,
    iter_page_object_bboxes,
    load_calibration,
    pt_to_mm,
    remove_headless_offset,
    resolve_sla_path,
    save_calibration,
    shift_page_objects,
    target_margin_rect_pt,
)
from sla_layers import audit_sla_layers

KIT_DIR = Path(__file__).resolve().parent


def cmd_info(args: argparse.Namespace) -> int:
    cal = load_calibration(args.calibration)
    sla = args.sla or resolve_sla_path(cal, args.calibration)
    text = sla.read_text(encoding="utf-8")
    bbox = iter_page_object_bboxes(text)
    if bbox is None:
        print("no objects")
        return 1
    target = target_margin_rect_pt(cal)
    payload = {
        "sla": str(sla),
        "calibration": str(args.calibration),
        "content_bbox_mm": [pt_to_mm(v) for v in bbox],
        "target_bbox_mm": [pt_to_mm(v) for v in target],
        "calibration_origin_mm": cal.get("calibration", {}).get("origin_page_mm"),
        "scale": cal.get("scale", {}),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_shift(args: argparse.Namespace) -> int:
    cal = load_calibration(args.calibration)
    sla = args.sla or resolve_sla_path(cal, args.calibration)
    text = sla.read_text(encoding="utf-8")
    text = shift_page_objects(text, args.dx_mm * PT_PER_MM, args.dy_mm * PT_PER_MM)
    sla.write_text(text, encoding="utf-8")
    print(f"shifted dx={args.dx_mm}mm dy={args.dy_mm}mm -> {sla}")
    return 0


def cmd_fit(args: argparse.Namespace) -> int:
    cal = load_calibration(args.calibration)
    sla = args.sla or resolve_sla_path(cal, args.calibration)
    text = sla.read_text(encoding="utf-8")
    new_text, info = fit_sla_text(text, cal, args.percent)
    print(json.dumps(info, ensure_ascii=False, indent=2))
    if args.dry_run:
        return 0
    sla.write_text(new_text, encoding="utf-8")
    cal.setdefault("scale", {})
    cal["scale"].update(
        {
            "anchor": "content_center",
            "fit_mode": "uniform",
            "last_percent": args.percent,
            "last_scale": info["fit_scale"],
            "content_bbox_mm": info["content_bbox_mm"],
        }
    )
    save_calibration(args.calibration, cal)
    print("saved:", sla)
    return 0


def cmd_normalize(args: argparse.Namespace) -> int:
    cal = load_calibration(args.calibration)
    sla = args.sla or resolve_sla_path(cal, args.calibration)
    text = sla.read_text(encoding="utf-8")
    text = fix_page_size(text)
    if args.remove_headless_offset:
        text = remove_headless_offset(text)
    text = calibrate_canvas_and_guides(text, cal)
    sla.write_text(text, encoding="utf-8")
    print("normalized:", sla)
    return 0


def cmd_init_calibration(args: argparse.Namespace) -> int:
    template = KIT_DIR / "calibration.template.json"
    data = json.loads(template.read_text(encoding="utf-8"))
    data["template"] = args.name
    if args.sla:
        data["scribus"]["sla_file"] = str(args.sla)
    out = args.output or Path.cwd() / f"{args.name}.calibration.json"
    save_calibration(out, data)
    print("created:", out)
    return 0


def cmd_layers(args: argparse.Namespace) -> int:
    cal = load_calibration(args.calibration)
    sla = args.sla or resolve_sla_path(cal, args.calibration)
    report = audit_sla_layers(sla.read_text(encoding="utf-8"))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Scribus layout calibration toolkit")
    sub = p.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--calibration", type=Path, required=True, help="*.calibration.json")
    common.add_argument("--sla", type=Path, help="override .sla path")

    sp = sub.add_parser("info", parents=[common], help="bbox / target を表示")
    sp.set_defaults(func=cmd_info)

    sp = sub.add_parser("shift", parents=[common], help="全オブジェクトを mm シフト")
    sp.add_argument("--dx-mm", type=float, default=0.0)
    sp.add_argument("--dy-mm", type=float, default=0.0)
    sp.set_defaults(func=cmd_shift)

    sp = sub.add_parser("fit", parents=[common], help="余白内に uniform scale")
    sp.add_argument("--percent", type=float, default=100.0)
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(func=cmd_fit)

    sp = sub.add_parser("normalize", parents=[common], help="ページサイズ・ガイド・headless 補正")
    sp.add_argument("--remove-headless-offset", action="store_true")
    sp.set_defaults(func=cmd_normalize)

    sp = sub.add_parser("layers", parents=[common], help="レイヤー標準との照合")
    sp.set_defaults(func=cmd_layers)

    sp = sub.add_parser("init", help="calibration.template.json から新規作成")
    sp.add_argument("--name", required=True, help="テンプレート名")
    sp.add_argument("--output", type=Path)
    sp.add_argument("--sla", type=Path)
    sp.set_defaults(func=cmd_init_calibration)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
