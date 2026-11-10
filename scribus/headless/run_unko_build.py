# -*- coding: utf-8 -*-
"""運行指示書レイアウトを headless 生成（日本語パス回避用ランチャー）。

build スクリプトは C:\\temp\\unko_build_layout.py にコピーしてから実行する。
"""
from __future__ import annotations

import json
import os
import runpy
import shutil
from pathlib import Path

ROOT = Path(os.environ.get("UNKO_HEADLESS_ROOT", r"C:\work\MCP\scribus\headless"))
cfg = json.loads((ROOT / "unko_paths.json").read_text(encoding="utf-8"))
design = Path(cfg["design_dir"])
build_src = design / cfg["build_script"]
build_tmp = Path(r"C:\temp\unko_build_layout.py")
final_sla = design / cfg["sla_name"]
out_sla = ROOT / "unko_out.sla"

shutil.copy2(build_src, build_tmp)
os.environ["SCRIBUS_SLA_OUT"] = str(out_sla)
os.environ["SCRIBUS_SLA_FINAL"] = str(final_sla)
os.environ["SCRIBUS_BUILD_LOG"] = r"C:\temp\unko_build_layout_log.txt"

runpy.run_path(str(build_tmp), run_name="__main__")
if out_sla.is_file():
    shutil.copy2(out_sla, final_sla)
