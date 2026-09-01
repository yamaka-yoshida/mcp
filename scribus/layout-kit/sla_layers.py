# -*- coding: utf-8 -*-
"""帳票レイアウト用レイヤー標準（.sla 検証・init 用。Scribus 非依存）。"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

LAYERS_FILE = Path(__file__).resolve().parent / "layers.standard.json"
LAYER_TAG_RE = re.compile(r"<Layers\s+([^/>]+)/?>", re.MULTILINE)


def _parse_layer_tag(attrs_raw: str) -> dict[str, Any] | None:
    attrs = dict(re.findall(r'(\w+)="([^"]*)"', attrs_raw))
    name = attrs.get("Name")
    level = attrs.get("Level")
    printable = attrs.get("IsPrintable")
    if name is None or level is None:
        return None
    return {
        "name": name,
        "level": int(level),
        "printable": printable != "0",
    }


def parse_layers_from_sla(text: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for match in LAYER_TAG_RE.finditer(text):
        parsed = _parse_layer_tag(match.group(1))
        if parsed:
            found.append(parsed)
    return sorted(found, key=lambda x: x["level"])


def load_layer_profile(path: Path | None = None) -> dict[str, Any]:
    p = path or LAYERS_FILE
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def standard_layer_names(profile: dict[str, Any] | None = None) -> list[str]:
    prof = profile or load_layer_profile()
    return [layer["name"] for layer in prof["layers"]]


def required_layer_names(profile: dict[str, Any] | None = None) -> list[str]:
    prof = profile or load_layer_profile()
    # データ・作業は任意。最小構成は 背景・罫線・見出し
    return [layer["name"] for layer in prof["layers"] if layer["level"] <= 2]


def audit_sla_layers(
    sla_text: str,
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    prof = profile or load_layer_profile()
    expected = prof["layers"]
    expected_names = [layer["name"] for layer in expected]
    actual = parse_layers_from_sla(sla_text)
    actual_names = [layer["name"] for layer in actual]
    actual_by_name = {layer["name"]: layer for layer in actual}

    missing_required = [n for n in required_layer_names(prof) if n not in actual_names]
    missing_optional = [
        layer["name"]
        for layer in expected
        if layer["name"] not in actual_names and layer["level"] > 2
    ]
    extra = [n for n in actual_names if n not in expected_names]

    order_issues: list[str] = []
    for i, layer in enumerate(expected):
        if layer["name"] not in actual_by_name:
            continue
        if actual_by_name[layer["name"]]["level"] != layer["level"]:
            order_issues.append(
                f"{layer['name']}: expected level {layer['level']}, "
                f"got {actual_by_name[layer['name']]['level']}"
            )

    printable_issues: list[str] = []
    for layer in expected:
        actual_layer = actual_by_name.get(layer["name"])
        if not actual_layer:
            continue
        if actual_layer["printable"] != layer["printable"]:
            printable_issues.append(
                f"{layer['name']}: expected printable={layer['printable']}, "
                f"got {actual_layer['printable']}"
            )

    ok = not missing_required and not order_issues
    return {
        "profile": prof["profile"],
        "ok": ok,
        "actual": actual,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "extra": extra,
        "order_issues": order_issues,
        "printable_issues": printable_issues,
    }
