# -*- coding: utf-8 -*-
"""SLA→PDF 書き出しランチャー（ASCII パス経由で scribus -py 実行）。"""
from __future__ import annotations

import os
import runpy

ROOT = os.environ.get("UNKO_HEADLESS_ROOT", r"C:\work\MCP\scribus\headless")
os.environ.setdefault(
    "SCRIBUS_EXPORT_JOB",
    os.path.join(ROOT, "export_job.json"),
)

runpy.run_path(os.path.join(ROOT, "export_sla_to_pdf.py"), run_name="__main__")
