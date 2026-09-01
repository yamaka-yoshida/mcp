# -*- coding: utf-8 -*-
"""帳票レイアウト用レイヤー標準（Scribus Scripter 内で import）。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LAYERS_FILE = Path(__file__).resolve().parent / "layers.standard.json"


def load_layer_profile(path: Path | None = None) -> dict[str, Any]:
    p = path or LAYERS_FILE
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def layer_for_kind(kind: str, profile: dict[str, Any] | None = None) -> str:
    prof = profile or load_layer_profile()
    mapping = prof.get("kind_to_layer", {})
    if kind not in mapping:
        raise KeyError(f"unknown object kind: {kind!r}")
    return mapping[kind]


def ensure_layers(scribus: Any, profile: dict[str, Any] | None = None) -> list[str]:
    """標準レイヤーを下→上の順で作成し、不足分を補う。"""
    prof = profile or load_layer_profile()
    existing = set(scribus.getLayers())
    created: list[str] = []
    for layer in prof["layers"]:
        name = layer["name"]
        if name not in existing:
            scribus.createLayer(name)
            created.append(name)
            existing.add(name)
    for layer in prof["layers"]:
        name = layer["name"]
        if not layer.get("printable", True):
            try:
                scribus.setLayerPrintable(name, False)
            except Exception:
                pass
    return created


def set_layer(scribus: Any, kind: str, profile: dict[str, Any] | None = None) -> str:
    """object kind に応じたレイヤーをアクティブにする。"""
    name = layer_for_kind(kind, profile)
    scribus.setActiveLayer(name)
    return name


def set_layer_by_name(scribus: Any, name: str) -> None:
    scribus.setActiveLayer(name)
