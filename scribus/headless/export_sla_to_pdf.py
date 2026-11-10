# -*- coding: utf-8 -*-
"""Scribus headless: .sla を PDF に書き出す（scribus -py 内で実行）。

環境変数 SCRIBUS_EXPORT_JOB に JSON パスを渡す。
  { "sla": "C:/.../運行指示書.sla", "pdf": "C:/.../out.pdf" }
"""
from __future__ import annotations

import json
import os
import sys

try:
    import scribus
except ImportError:
    print("Run inside Scribus (-py)", file=sys.stderr)
    sys.exit(1)

JOB_PATH = os.environ.get(
    "SCRIBUS_EXPORT_JOB",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "export_job.json"),
)

LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "export_pdf_log.txt")


def main() -> int:
    with open(JOB_PATH, encoding="utf-8") as f:
        job = json.load(f)
    sla = job["sla"]
    pdf = job["pdf"]

    if not os.path.isfile(sla):
        print(f"SLA not found: {sla}", file=sys.stderr)
        return 1

    out_dir = os.path.dirname(os.path.abspath(pdf))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    if scribus.haveDoc():
        scribus.closeDoc()

    scribus.openDoc(sla)

    pdf_obj = scribus.PDFfile()
    pdf_obj.file = pdf
    # フォント埋め込み（1 = 全埋め込み / 版により定数名が異なる場合あり）
    if hasattr(pdf_obj, "fontEmbedding"):
        pdf_obj.fontEmbedding = 1
    if hasattr(pdf_obj, "compress"):
        pdf_obj.compress = 1
    if hasattr(pdf_obj, "quality"):
        pdf_obj.quality = 0  # 最高品質寄り

    pdf_obj.save()
    print("exported:", pdf)

    if scribus.haveDoc():
        scribus.closeDoc()

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write(f"OK\n{sla}\n{pdf}\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        import traceback

        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise
